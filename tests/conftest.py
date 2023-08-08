import pytest
from fastapi.testclient import TestClient

from fast_zero.main import app


@pytest.fixture
def client():
    return TestClient(app)
