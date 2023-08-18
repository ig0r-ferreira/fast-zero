from jose import jwt

from fast_zero.security import create_access_token
from fast_zero.settings import Settings

settings = Settings()


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded_data = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded_data['test'] == data['test']
    assert decoded_data['exp']
