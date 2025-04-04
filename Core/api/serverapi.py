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
        elif self.path == '/':
            self.redirect_to_login()
        else:
            self.serve_static_files()

    def redirect_to_login(self):
        app_id = config.get('gewechat_app_id')
        self.send_response(302)
        self.send_header('Location', f'/login.html?app_id={app_id}')
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
        app_id = params.get('app_id', [None])[0]
        
        if not app_id:
            self._send_json_response(400, {"error": "缺少app_id参数"})
            return

        # 获取二维码
        app_id, uuid = loginAPI._get_and_validate_qr(app_id)
        if not app_id or not uuid:
            self._send_json_response(500, {"error": "获取二维码失败"})
            return

        qr_url = f"http://weixin.qq.com/x/{uuid}"
        self._send_json_response(200, {
            "qr_url": qr_url,
            "uuid": uuid
        })

    def handle_check_login(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [None])[0]
        uuid = params.get('uuid', [None])[0]

        if not app_id or not uuid:
            self._send_json_response(400, {"error": "缺少必要参数"})
            return

        # 检查登录状态
        login_status = loginAPI.check_qr(app_id, uuid, "")
        if login_status.get('ret') != 200:
            self._send_json_response(500, {"error": "检查登录状态失败"})
            return

        login_data = login_status.get('data', {})
        status = login_data.get('status')

        # 如果登录成功，自动设置回调
        if status == 2:
            callback_url = config.get('gewechat_callback_url')
            callback_resp = loginAPI.set_callback(app_id, callback_url)
            print(f"设置回调结果: {callback_resp}")

        self._send_json_response(200, {"status": status})

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
    print(f"API服务器已启动: http://localhost:{port}")
    print(f"请访问 http://localhost:{port}/?app_id={config.get('gewechat_app_id')} 进行登录")
    httpd.serve_forever()

if __name__ == "__main__":
    run()