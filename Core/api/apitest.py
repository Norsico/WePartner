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
        return data
    else:
        print("登录失败，状态码：", response.status_code)
        return None

# 测试检查登录状态接口
def test_check_login(uuid, app_id):
    url = f"{BASE_URL}/check_login"
    params = {
        "app_id": app_id,
        "uuid": uuid
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("检查登录状态失败，状态码：", response.status_code)
        return None

# 轮询检查登录状态
def poll_check_login(uuid, app_id):
    print("开始轮询检查登录状态")
    retry_count = 0
    max_retries = 100  # 最大重试次数

    while retry_count < max_retries:
        check_login_result = test_check_login(uuid, app_id)
        if check_login_result:
            status = check_login_result.get("status")

            if status == 2:  # 登录成功
                print("登录成功！")
                return True
            else:
                retry_count += 1
                if retry_count >= max_retries:
                    print("登录超时，请重新尝试")
                    return False
                time.sleep(5)
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

# 主测试函数
def main():
    # 测试登录
    login_result = test_login()
    if login_result:
        uuid = login_result.get("uuid")
        app_id = login_result.get("app_id")
        qr_url = login_result.get("qr_url")

        # 输出二维码URL
        print(f"请使用微信扫码登录：{qr_url}")

        # 轮询检查登录状态
        if not poll_check_login(uuid, app_id):
            print("登录失败")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"发生错误：{e}")
