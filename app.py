from flask import Flask, render_template, request, jsonify, send_from_directory
import webbrowser
import threading
import requests
import os
import subprocess
import sys
import json

app = Flask(__name__, static_folder='static')

# 配置服务器地址和端口
SERVER_IP = "localhost"
SERVER_PORT = 8002
BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# 存储main.py进程
main_process = None

# 添加favicon配置
app.config['FAVICON'] = 'docs/images/logo.png'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def config():
    return render_template('config.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/get_current_platform', methods=['GET'])
def get_current_platform():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return jsonify({'platform': config.get('agent_platform', 'dify')})
    except Exception as e:
        return jsonify({'platform': 'dify'})

@app.route('/api/get_current_config', methods=['GET'])
def get_current_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return jsonify({
                'dify': {
                    'server_ip': config.get('dify_server_ip', ''),
                    'api_key': config.get('dify_api_key', '')
                },
                'coze': {
                    'agent_id': config.get('coze_agent_id', ''),
                    'api_token': config.get('coze_api_token', '')
                },
                'gewe_server_ip': config.get('gewe_server_ip', '')
            })
    except Exception as e:
        return jsonify({
            'dify': {'server_ip': '', 'api_key': ''},
            'coze': {'agent_id': '', 'api_token': ''},
            'gewe_server_ip': ''
        })

@app.route('/api/change_platform', methods=['POST'])
def change_platform():
    platform = request.json.get('platform')
    if platform not in ['dify', 'coze']:
        return jsonify({'success': False, 'message': '无效的平台参数'})
    
    try:
        response = requests.get(f"{BASE_URL}/changeplatform", params={'platform': platform})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/change_dify', methods=['POST'])
def change_dify():
    server_ip = request.json.get('server_ip')
    api_key = request.json.get('api_key')
    
    if not server_ip and not api_key:
        return jsonify({'success': False, 'message': '至少需要提供一个参数'})
    
    try:
        response = requests.get(f"{BASE_URL}/changedify", params={'server_ip': server_ip, 'api_key': api_key})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/change_coze', methods=['POST'])
def change_coze():
    agent_id = request.json.get('agent_id')
    api_token = request.json.get('api_token')
    
    if not agent_id and not api_token:
        return jsonify({'success': False, 'message': '至少需要提供一个参数'})
    
    try:
        response = requests.get(f"{BASE_URL}/changecoze", params={'agent_id': agent_id, 'api_token': api_token})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/login', methods=['GET'])
def get_login_qr():
    try:
        response = requests.get(f"{BASE_URL}/login")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/check_login', methods=['GET'])
def check_login():
    uuid = request.args.get('uuid')
    app_id = request.args.get('app_id')
    
    if not uuid:
        return jsonify({'success': False, 'message': '缺少必要参数'})
    
    try:
        response = requests.get(f"{BASE_URL}/check_login", params={'uuid': uuid, 'app_id': app_id})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/changegewe', methods=['GET'])
def change_gewe():
    server_ip = request.args.get('server_ip')
    
    if not server_ip:
        return jsonify({'success': False, 'message': '未提供服务器IP地址'})
    
    try:
        response = requests.get(f"{BASE_URL}/changegewe", params={'server_ip': server_ip})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/check_online', methods=['GET'])
def check_online():
    try:
        response = requests.get(f"{BASE_URL}/check_online")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'online': False, 'message': str(e)})

def open_browser():
    webbrowser.open('http://localhost:5000')

def start_main_process():
    """启动main.py进程"""
    global main_process
    try:
        # 获取main.py的绝对路径
        main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        
        # 启动main.py进程
        main_process = subprocess.Popen([sys.executable, main_script])
        print("main.py进程已启动")
    except Exception as e:
        print(f"启动main.py失败: {str(e)}")

def cleanup():
    """清理资源"""
    global main_process
    if main_process:
        try:
            main_process.terminate()
            main_process.wait(timeout=5)
            print("main.py进程已终止")
        except Exception as e:
            print(f"终止main.py进程时出错: {str(e)}")

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    
    # 创建静态文件目录
    os.makedirs('static', exist_ok=True)
    
    # 启动main.py进程
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        start_main_process()
        # 启动浏览器
        threading.Timer(1.25, open_browser).start()
    
    try:
        # 启动Flask应用
        app.run(debug=True, use_reloader=True)
    finally:
        # 确保在程序退出时清理资源
        cleanup() 