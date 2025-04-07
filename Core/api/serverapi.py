from http.server import BaseHTTPRequestHandler, HTTPServer
from gewechat.client import LoginApi
import urllib.parse
import json
from config import Config
import os
import sys
import traceback
import time
def print_green(text):
    print(f"\033[32m{text}\033[0m")

config = Config()

def print_yellow(text):
    print(f"\033[33m{text}\033[0m")

def print_red(text):
    print(f"\033[31m{text}\033[0m")

# 获取项目根目录
current_file_path = os.path.abspath(__file__)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
sys.path.append(root_dir)

# 导入Channel实例
def get_channel_instance():
    """获取全局Channel实例"""
    try:
        from Core.initializer import channel
        return channel
    except Exception as e:
        print(f"获取Channel实例失败: {e}")
        traceback.print_exc()
        return None

loginAPI = LoginApi(base_url=f"http://{config.get('gewe_server_ip')}:2531/v2/api", token=config.get("gewechat_token"))

gewechat_app_id = config.get('gewechat_app_id', '')

tmp_app_id = 0

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/login'):
            self.handle_login()
        elif self.path.startswith('/check_login'):
            self.handle_check_login()
        elif self.path.startswith('/changedify'):
            self.handle_change_dify()
        elif self.path.startswith('/changecoze'):
            self.handle_change_coze()
        elif self.path.startswith('/changeplatform'):
            self.handle_change_platform()
        elif self.path.startswith('/changegewe'):
            self.handle_change_gewe()
        elif self.path.startswith('/check_online'):
            self.handle_check_online()

    def handle_login(self):
        global tmp_app_id

        app_id = config.get('gewechat_app_id', '')
        if app_id:
            print("检查在线状态...")
            check_online_response = loginAPI.check_online(app_id)
            if check_online_response.get('ret') == 200 and check_online_response.get('data'):
                print_green(f"AppID: {app_id} 已在线，正在退出登录...")
                # 退出登录
                logout_response = loginAPI.logout(app_id)
                if logout_response.get('ret') != 200:
                    print_red(f"退出登录失败: {logout_response}")
                    self._send_json_response(500, {"error": "退出登录失败"})
                    return
                print_green("退出登录成功，正在重新获取二维码...")
                time.sleep(1)  # 等待一秒确保退出完成
            else:
                print_yellow(f"AppID: {app_id} 未在线，直接获取二维码...")
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
        print_green(f"检查登录状态返回: {login_status}")

        if login_status.get('ret') != 200:
            self._send_json_response(500, {"error": "检查登录状态失败"})
            return

        login_data = login_status.get('data', {})
        status = login_data.get('status')
        expired_time = login_data.get('expiredTime', 0)
        print_green(f"登录状态: {status}, 过期时间: {expired_time}")

        # 如果二维码即将过期，返回特殊状态
        if expired_time <= 5:
            self._send_json_response(200, {
                "status": 0,  # 使用0表示需要重新获取二维码
                "message": "二维码即将过期，请重新获取"
            })
            return

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

        response_data = {
            "status": status,
            "app_id": login_data.get('appId', app_id)  # 返回新的app_id
        }
        print_green(f"返回数据: {response_data}")
        self._send_json_response(200, response_data)

    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        response_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(response_data)

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
        print_green(f"返回二维码: {qr_url}")

    def handle_change_dify(self):
        """
        处理修改Dify配置的请求
        格式: /changedify?server_ip=xxx&api_key=yyy
        """
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        server_ip = params.get('server_ip', [None])[0]
        api_key = params.get('api_key', [None])[0]

        # 更新配置
        updated = False
        if server_ip:
            config.set("dify_server_ip", server_ip)
            updated = True
        if api_key:
            config.set("dify_api_key", api_key)
            updated = True

        if updated:
            # 通知Channel刷新配置
            channel = get_channel_instance()
            if channel:
                channel.refresh_config()
                print_green("已通知Channel刷新配置")
            self._send_json_response(200, {"success": True, "message": "Dify配置已更新"})
            print_green("Dify配置已更新")
        else:
            self._send_json_response(400, {"success": False, "message": "未提供任何有效参数"})

    def handle_change_coze(self):
        """
        处理修改Coze配置的请求
        格式: /changecoze?agent_id=xxx&api_token=yyy
        """
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        agent_id = params.get('agent_id', [None])[0]
        api_token = params.get('api_token', [None])[0]

        # 更新配置
        updated = False
        if agent_id:
            config.set("coze_agent_id", agent_id)
            updated = True
        if api_token:
            config.set("coze_api_token", api_token)
            updated = True

        if updated:
            # 通知Channel刷新配置
            channel = get_channel_instance()
            if channel:
                channel.refresh_config()
                print_green("已通知Channel刷新配置")
            self._send_json_response(200, {"success": True, "message": "Coze配置已更新"})
            print_green("Coze配置已更新")
        else:
            self._send_json_response(400, {"success": False, "message": "未提供任何有效参数"})

    def handle_change_platform(self):
        """
        处理修改AI平台的请求
        格式: /changeplatform?platform=dify 或 /changeplatform?platform=coze
        """
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        platform = params.get('platform', [None])[0]

        if platform in ["dify", "coze"]:
            config.set("agent_platform", platform)
            # 通知Channel刷新配置
            channel = get_channel_instance()
            if channel:
                channel.refresh_config()
                print_green("已通知Channel刷新配置")
            self._send_json_response(200, {"success": True, "message": f"AI平台已切换为{platform}"})
        else:
            self._send_json_response(400, {"success": False, "message": "无效的平台参数，请使用'dify'或'coze'"})

    def handle_change_gewe(self):
        """
        处理修改GEWE服务器配置的请求
        格式: /changegewe?server_ip=xxx
        """
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        server_ip = params.get('server_ip', [None])[0]

        if server_ip:
            config.set("gewe_server_ip", server_ip)
            self._send_json_response(200, {"success": True, "message": "GEWE服务器配置已更新"})
            print_green("GEWE服务器配置已更新")
        else:
            self._send_json_response(400, {"success": False, "message": "未提供服务器IP地址"})

    def handle_check_online(self):
        """
        处理检查在线状态的请求
        """
        app_id = config.get('gewechat_app_id', '')
        if not app_id:
            self._send_json_response(200, {"online": False, "message": "未登录"})
            return

        try:
            check_online_response = loginAPI.check_online(app_id)
            if check_online_response.get('ret') == 200 and check_online_response.get('data'):
                self._send_json_response(200, {"online": True, "message": "在线"})
            else:
                self._send_json_response(200, {"online": False, "message": "离线"})
        except Exception as e:
            print_red(f"检查在线状态失败: {e}")
            self._send_json_response(200, {"online": False, "message": f"检查失败: {str(e)}"})

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8002):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"API服务器已启动: http://{config.get('gewe_server_ip')}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()