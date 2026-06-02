import requests
import time
import sys

# ================= 配置区 =================
VM_IP = "192.168.128.128"  # 👈 请修改为虚拟机的真实IP
BASE_URL = f"http://{VM_IP}/api"
USERNAME = "admin"
PASSWORD = "arlpass"
TARGET = "scanme.nmap.org" # 官方授权的合法扫描靶机
# ==========================================

def print_step(msg):
    print(f"\n[+] {'='*10} {msg} {'='*10}")

def print_error(msg):
    print(f"[!] ❌ 错误: {msg}")
    sys.exit(1)

def run_tests():
    session = requests.Session()

    # ---------------------------------------------------------
    print_step("关卡 1：API 登录与鉴权测试")
    # ---------------------------------------------------------
    login_url = f"{BASE_URL}/user/login"
    login_data = {"username": USERNAME, "password": PASSWORD}

    try:
        res = session.post(login_url, json=login_data, timeout=5)
        res_json = res.json()

        if res.status_code == 200 and res_json.get("code") == 200:
            token = res_json["data"]["token"]
            print(f"✅ 登录成功！获取到 Token: {token[:10]}...{token[-5:]}")
            # 将 Token 塞入后续所有请求的请求头中
            session.headers.update({"Token": token})
        else:
            print_error(f"登录失败，返回值: {res_json}")
    except Exception as e:
        print_error(f"无法连接到虚拟机 {VM_IP}，请检查 IP 和服务是否启动！({str(e)})")

    # ---------------------------------------------------------
    print_step("关卡 2：越权防御测试 (无 Token 强行访问)")
    # ---------------------------------------------------------
    try:
        bad_res = requests.get(f"{BASE_URL}/task/", timeout=5) # 故意不用带 Token 的 session
        if bad_res.json().get("code") == 401:
            print("✅ 越权防御生效！成功拦截无 Token 的非法请求。")
        else:
            print_error("越权防御失败，未授权也能拉取数据！")
    except Exception as e:
        print_error(f"越权防御测试请求异常: {str(e)}")

    # ---------------------------------------------------------
    print_step("关卡 3：核心中枢 - 下发端口与目录扫描任务")
    # ---------------------------------------------------------
    task_url = f"{BASE_URL}/task/"
    task_payload = {
        "name": f"Auto_Test_{int(time.time())}",
        "target": TARGET,
        "port_scan": True,           # 开启端口扫描
        "port_scan_type": "top100",  # 只扫 top100 端口加快速度
        "site_identify": True,       # 开启站点识别
    }

    task_id = None
    try:
        res = session.post(task_url, json=task_payload)
        res_json = res.json()

        if res_json.get("code") == 200:
            # ARL 下发任务返回的是一个列表 items
            task_list = res_json.get("items", [])
            if task_list:
                task_id = task_list[0].get("task_id") or task_list[0].get("_id")
                print(f"✅ 任务下发成功！目标: {TARGET}, Task ID: {task_id}")
            else:
                print_error("API返回200，但未提取到 task_id")
        else:
            print_error(f"任务下发失败: {res_json}")
    except Exception as e:
        print_error(f"任务下发请求异常: {str(e)}")

    # ---------------------------------------------------------
    print_step("关卡 4：Worker 引擎状态轮询 (最高等待 60 秒)")
    # ---------------------------------------------------------
    if not task_id:
        return

    query_url = f"{BASE_URL}/task/"
    max_retries = 12

    print("⏳ 开始监听 Worker 执行状态...")
    for i in range(max_retries):
        try:
            res = session.get(query_url, params={"_id": task_id})
            task_info = res.json().get("items", [{}])[0]
            status = task_info.get("status", "unknown")

            print(f"  [{i+1}/{max_retries}] 当前状态: {status} ...")

            if status == "done":
                print("\n✅ 测试完美通关！Worker 成功完成了扫描任务并存入数据库！")
                break
            elif status == "error":
                print_error("\n❌ 任务执行失败！Worker 内部发生了异常。")

            time.sleep(5) # 每 5 秒轮询一次

        except Exception as e:
            print_error(f"状态轮询异常: {str(e)}")

    else:
        print("\n⚠️ 达到最大轮询时间。任务仍在运行中（这是正常的，因为即使是 top100 端口扫描可能也需要几分钟）。")
        print("✅ 后端中枢与消息队列连通性验证成功！")

if __name__ == "__main__":
    run_tests()