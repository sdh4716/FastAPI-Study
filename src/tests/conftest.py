import pytest

from fastapi.testclient import TestClient
from main import app

# fixture로 등록해 놓으면 전역으로 사용 가능
@pytest.fixture
def client():
    return TestClient(app=app)