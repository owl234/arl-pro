import pytest
import requests

# 测试环境的基础配置 (后续可以通过环境变量动态替换)
BASE_URL = "http://192.168.128.128/api"  # 👈 请替换为您虚拟机的 IP
USERNAME = "admin"
PASSWORD = "arlpass"

@pytest.fixture(scope="session")
def api_client():
    """
    这是一个全局 HTTP 客户端夹具。
    它会在所有测试开始前，自动模拟登录并拿到 Token，
    然后把带有 Token 的 session 交给后续的测试用例使用。
    """
    session = requests.Session()
    login_url = f"{BASE_URL}/user/login"

    res = session.post(login_url, json={"username": USERNAME, "password": PASSWORD})
    assert res.status_code == 200, "全局前置条件失败：无法连接后端或登录失败"

    token = res.json().get("data", {}).get("token")
    assert token is not None, "全局前置条件失败：未获取到 Token"

    # 将 Token 注入全局 Session
    session.headers.update({"Token": token})

    # 顺便把 BASE_URL 也挂在 session 上，方便后续调用
    session.base_url = BASE_URL

    yield session  # 将这个带身份的 session 交给后续测试用例

    # 如果有测试结束后的清理工作（比如退出登录、清理脏数据），可以写在 yield 之后
    session.close()