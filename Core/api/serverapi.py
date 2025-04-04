from http.server import BaseHTTPRequestHandler, HTTPServer
from gewechat.client import LoginApi
import urllib.parse
import json
import os
from config import Config

config = Config()
print(f"gewechat_base_url: {config.get('gewechat_base_url')}")
print(f"gewechat_token: {config.get('gewechat_token')}")

loginAPI = LoginApi(base_url=config.get("gewechat_base_url"), token=config.get("gewechat_token"))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/login'):
            self.handle_login()
        elif self.path.startswith('/check_login'):
            self.handle_check_login()
        elif self.path.startswith('/relogin'):
            self.handle_relogin()
        elif self.path.startswith('/set_callback'):
            self.handle_set_callback()
        elif self.path == '/' or self.path.startswith('/?'):
            self.redirect_to_login()
        else:
            self.serve_static_files()

    def redirect_to_login(self):
        # 从URL中获取app_id参数
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [None])[0]
        
        # 如果URL中没有app_id，则使用配置中的app_id
        if not app_id:
            app_id = config.get('gewechat_app_id', '')
            
        # 重定向到登录页面，即使app_id为空也没关系
        self.send_response(302)
        self.send_header('Location', f'/login.html?app_id={app_id if app_id else ""}')
        self.end_headers()

    def serve_static_files(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'templates', self.path.lstrip('/'))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                elif file_path.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif file_path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def handle_login(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [''])[0]  # 默认为空字符串而不是None
        
        # 获取二维码（即使app_id为空也可以）
        app_id, uuid = loginAPI._get_and_validate_qr(app_id)
        if not uuid:  # 只检查uuid，因为首次登录时app_id可能为空
            self._send_json_response(500, {"error": "获取二维码失败"})
            return

        base_url = f"http://weixin.qq.com/x/{uuid}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?data={base_url}"
        
        self._send_json_response(200, {
            "qr_url": qr_url,
            "uuid": uuid,
            "app_id": app_id
        })

    def handle_check_login(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [''])[0]  # 默认为空字符串
        uuid = params.get('uuid', [None])[0]

        if not uuid:  # 只检查uuid，因为首次登录时app_id可能为空
            self._send_json_response(400, {"error": "缺少必要参数"})
            return

        # 检查登录状态
        login_status = loginAPI.check_qr(app_id, uuid, "")
        if login_status.get('ret') != 200:
            self._send_json_response(500, {"error": "检查登录状态失败"})
            return

        login_data = login_status.get('data', {})
        status = login_data.get('status')

        # 如果登录成功
        if status == 2:
            # 保存新的app_id（如果有的话）
            if login_data.get('appId'):
                config.set('gewechat_app_id', login_data['appId'])
                
            # 设置回调地址
            callback_url = config.get('gewechat_callback_url')
            if callback_url:
                callback_resp = loginAPI.set_callback(login_data.get('appId'), callback_url)
                print(f"设置回调结果: {callback_resp}")

        self._send_json_response(200, {
            "status": status,
            "app_id": login_data.get('appId', app_id)  # 返回新的app_id
        })

    def handle_relogin(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [None])[0]
        
        if not app_id:
            self._send_json_response(400, {"error": "缺少app_id参数"})
            return

        app_id, qr_url, error_msg = loginAPI.re_login(app_id)
        if error_msg:
            self._send_json_response(500, {"error": error_msg})
            return

        self._send_json_response(200, {"qr_url": qr_url})

    def handle_set_callback(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [None])[0]
        callback_url = params.get('callback_url', [None])[0]
        
        if not app_id or not callback_url:
            self._send_json_response(400, {"error": "缺少app_id或callback_url参数"})
            return

        callback_resp = loginAPI.set_callback(app_id, callback_url)
        if callback_resp.get("ret") == 200:
            self._send_json_response(200, {"message": "回调地址设置成功"})
        else:
            self._send_json_response(500, {"error": "回调地址设置失败"})

    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8002):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"API服务器已启动: http://{config.get('server_host')}:{port}")
    print(f"请访问 http://{config.get('server_host')}:{port}/ 进行登录")
    httpd.serve_forever()

if __name__ == "__main__":
    run()