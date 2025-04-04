import requests
import time

# 配置接口服务器地址和端口
BASE_URL = ""

# 测试登录接口
def test_login():
    print("测试登录接口")
    url = f"{BASE_URL}/login"
    params = {
        "app_id": ""  # 替换为实际的app_id，或者留空测试默认值
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("登录成功，返回数据：", data)
        return data
    else:
        print("登录失败，状态码：", response.status_code)
        return None

# 测试检查登录状态接口
def test_check_login(uuid, app_id):
    print("测试检查登录状态接口")
    url = f"{BASE_URL}/check_login"
    params = {
        "app_id": app_id,
        "uuid": uuid
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("检查登录状态成功，返回数据：", data)
        return data
    else:
        print("检查登录状态失败，状态码：", response.status_code)
        return None

# 轮询检查登录状态
def poll_check_login(uuid, app_id):
    print("开始轮询检查登录状态")
    max_retries = 100  # 最大重试次数
    retry_interval = 5  # 重试间隔（秒）

    for attempt in range(max_retries):
        check_login_result = test_check_login(uuid, app_id)
        if check_login_result:
            status = check_login_result.get("status")
            if status == 2:  # 登录成功
                print("登录成功！")
                return True
            elif status == 1:  # 二维码未过期，但未登录
                print(f"等待用户扫码登录，尝试次数：{attempt + 1}/{max_retries}")
                time.sleep(retry_interval)
            elif status == 0:  # 未知状态，可能是用户未扫码
                print(f"用户尚未扫码，等待用户操作，尝试次数：{attempt + 1}/{max_retries}")
                time.sleep(retry_interval)
            else:
                print(f"未知状态码：{status}，退出轮询")
                return False
        else:
            print("检查登录状态失败，退出轮询")
            return False

    print("登录超时，退出轮询")
    return False

# 测试重新登录接口
def test_relogin(app_id):
    print("测试重新登录接口")
    url = f"{BASE_URL}/relogin"
    params = {
        "app_id": app_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("重新登录成功，返回数据：", data)
        return data
    else:
        print("重新登录失败，状态码：", response.status_code)
        return None

# 测试设置回调地址接口
def test_set_callback(app_id, callback_url):
    print("测试设置回调地址接口")
    url = f"{BASE_URL}/set_callback"
    params = {
        "app_id": app_id,
        "callback_url": callback_url
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("设置回调地址成功，返回数据：", data)
        return data
    else:
        print("设置回调地址失败，状态码：", response.status_code)
        return None

# 轮询检查登录状态
def poll_check_login(uuid, app_id):
    print("开始轮询检查登录状态")
    max_retries = 100  # 最大重试次数
    retry_interval = 5  # 重试间隔（秒）

    for attempt in range(max_retries):
        check_login_result = test_check_login(uuid, app_id)
        if check_login_result:
            status = check_login_result.get("status")
            expired_time = check_login_result.get("expiredTime", 0)

            if status == 2:  # 登录成功
                print("登录成功！")
                return True
            elif status == 1:  # 二维码未过期，但未登录
                print(f"等待用户扫码登录，尝试次数：{attempt + 1}/{max_retries}")
                time.sleep(retry_interval)
            elif status == -1 or expired_time <= 0:  # 二维码已过期
                print("二维码已过期，正在重新获取...")
                login_result = test_login()
                if login_result:
                    uuid = login_result.get("uuid")
                    print(f"新的二维码已生成，请重新扫码：{login_result.get('qr_url')}")
                else:
                    print("重新获取二维码失败")
                    return False
            else:
                print(f"未知状态码：{status}，退出轮询")
                return False
        else:
            print("检查登录状态失败，退出轮询")
            return False

    print("登录超时，退出轮询")
    return False

# 主测试函数
def main():
    # 测试登录
    login_result = test_login()
    if login_result:
        uuid = login_result.get("uuid")
        app_id = login_result.get("app_id")
        
        # 轮询检查登录状态
        if not poll_check_login(uuid, app_id):
            print("登录失败，请检查以下内容：")
            print("1. 确保二维码链接可以通过浏览器正常访问：")
            print(f"   {login_result.get('qr_url')}")
            print("2. 确保网络连接正常。")
            print("3. 如果问题仍然存在，请稍后重试或检查二维码链接的合法性。")
            return
        
        # # 测试重新登录
        # relogin_result = test_relogin(app_id)
        
        # 测试设置回调地址
        callback_url = "http://47.93.3.37:1145/v2/api/callback/collect"  # 替换为实际的回调地址
        set_callback_result = test_set_callback(app_id, callback_url)
        print(set_callback_result)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"发生错误：{e}")

# 处理链接解析失败的情况
def handle_link_resolution_failure():
    print("由于网络原因，无法解析网页内容。")
    print("请检查网页链接的合法性，并确保网络连接正常。")
    print("如果需要进一步帮助，请提供更多信息或尝试重新加载网页。")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        handle_link_resolution_failure()
        print(f"发生错误：{e}")
    