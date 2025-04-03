from http.server import BaseHTTPRequestHandler, HTTPServer
from gewechat.client import LoginApi
import urllib.parse
import json
from config import Config

config = Config()

print(f"gewechat_base_url: {config.get("gewechat_base_url")}")
print(f"gewechat_token: {config.get("gewechat_token")}")

loginAPI = LoginApi(base_url=config.get("gewechat_base_url"), token=config.get("gewechat_token"))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/relogin'):
            self.handle_relogin()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_relogin(self):
        # 解析查询参数
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        app_id = params.get('app_id', [None])[0]
        if not app_id:
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self._send_response({"error": "缺少app_id参数"})
            return

        # 调用re_login函数
        app_id, qr_url, error_msg = loginAPI.re_login(app_id)
        if error_msg:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self._send_response({"error": error_msg})
            return

        # 返回新的二维码链接
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self._send_response({"qr_url": qr_url})

    def _send_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')  # 指定编码为 UTF-8
        self.end_headers()
        if isinstance(data, str):
            self.wfile.write(data.encode('utf-8'))
        else:
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))  # 确保中文字符正确编码

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8002):
    server_address = ('0.0.0.0', port)  # 绑定到所有网络接口
    httpd = server_class(server_address, handler_class)
    print(f"HTTP服务器已启动，监听端口: {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
