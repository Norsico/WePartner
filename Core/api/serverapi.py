from http.server import BaseHTTPRequestHandler, HTTPServer
from gewechat.client import LoginApi
import urllib.parse
import json
from config import Config

def print_green(text):
    print(f"\033[32m{text}\033[0m")

config = Config()

loginAPI = LoginApi(base_url=f"http://{config.get("gewe_server_ip")}:2531/v2/api", token=config.get("gewechat_token"))

gewechat_app_id = config.get('gewechat_app_id', '')

tmp_app_id = 0

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/login'):
            self.handle_login()
        elif self.path.startswith('/check_login'):
            self.handle_check_login()

    def handle_login(self):
        global tmp_app_id

        app_id = config.get('gewechat_app_id', '')
        if app_id:
            print("退出登录")
            loginAPI.logout(app_id)
            print("退出成功")
            self._handle_login(app_id)
        else:
            print("新登录")
            self._handle_login(app_id)
            
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
            nick_name = login_data.get('nickName', '未知用户')
            print_green(f"\n登录成功！用户昵称: {nick_name}")
            # 保存appId
            config.set("gewechat_app_id", str(tmp_app_id))
            # 设置回调地址
            callback_url = f"http://{config.get('gewe_server_ip')}:1145/v2/api/callback/collect"
            if callback_url:
                callback_resp = loginAPI.set_callback(config.get("gewechat_token"), callback_url)
                print(f"设置回调结果: {callback_resp}")

        self._send_json_response(200, {
            "status": status,
            "app_id": login_data.get('appId', app_id)  # 返回新的app_id
        })


    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _handle_login(self, app_id):
        global tmp_app_id

        # 获取二维码
        app_id, uuid = loginAPI._get_and_validate_qr(app_id)
        if not uuid:  # 只检查uuid，因为首次登录时app_id可能为空
            self._send_json_response(500, {"error": "获取二维码失败"})
            return

        base_url = f"http://weixin.qq.com/x/{uuid}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?data={base_url}"

        # 缓存appId
        tmp_app_id = app_id
        self._send_json_response(200, {
            "qr_url": qr_url,
            "uuid": uuid,
            "app_id": app_id
        })

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8002):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"API服务器已启动: http://{config.get('gewe_server_ip')}:{port}")
    print(f"请访问 http://{config.get('gewe_server_ip')}:{port}/ 进行登录")
    httpd.serve_forever()

if __name__ == "__main__":
    run()