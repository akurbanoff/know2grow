from tests.conftest import client
from src.main import app
import json

def test_registration():
    data = {
      "name": "Artem",
      "email": "Uspeshniy.ae@yandex.ru",
      "password": "Jlidero88"
    }
    response = client.post(url='/auth/register', json=data)#json=json.dumps(data))

    assert response.status_code == 201


def test_some():
    a = 1

    assert a == 1
