import requests

def test_login_success():
    """测试：使用正确的账号密码可以成功登录并获取 Token"""
    from conftest import BASE_URL, USERNAME, PASSWORD # 仅用于此独立测试

    res = requests.post(f"{BASE_URL}/user/login", json={"username": USERNAME, "password": PASSWORD})
    assert res.status_code == 200
    assert res.json().get("code") == 200
    assert "token" in res.json().get("data", {})

def test_login_wrong_password():
    """测试：使用错误的密码登录会被拒绝"""
    from conftest import BASE_URL, USERNAME

    res = requests.post(f"{BASE_URL}/user/login", json={"username": USERNAME, "password": "wrongpassword"})
    assert res.status_code == 200 # HTTP 状态码可能是 200
    assert res.json().get("code") == 401 # 但业务状态码应该是 401 (未授权)

def test_access_without_token():
    """测试：不携带 Token 访问受保护接口，应当被拦截"""
    from conftest import BASE_URL

    # 使用一个全新的、没有 Token 的 requests session
    res = requests.get(f"{BASE_URL}/task/")
    assert res.json().get("code") == 401

def test_access_with_token(api_client):
    """
    测试：携带 Token 访问受保护接口，应当成功。
    注意参数里的 `api_client`，Pytest 会自动调用 conftest.py 把它塞进来！
    """
    res = api_client.get(f"{api_client.base_url}/task/")
    assert res.status_code == 200
    assert res.json().get("code") == 200