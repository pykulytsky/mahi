from app.core import security
import jwt
from app.core.config import settings
import pytest


def test_create_access_token(user):
    token = security.create_access_token(user.id)
    decoded_jwt = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM
    )

    assert 'exp' in decoded_jwt
    assert 'sub' in decoded_jwt
    assert decoded_jwt['sub'] == str(user.id)


@pytest.mark.freeze_time('2117-07-07')
def test_token_expiration(user):
    token = security.create_access_token(user.id)
    decoded_jwt = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM
    )

    assert 'sub' in decoded_jwt
    assert decoded_jwt['exp'] == 4655664000
