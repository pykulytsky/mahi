import typing

import requests
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette.testclient import (
    ASGI2App,
    ASGI3App,
    Cookies,
    DataType,
    FileType,
    Params,
    TimeOut,
)

from app import schemas
from app.models import User


class BearerAuth(requests.auth.AuthBase):
    """Base Bearer authentication"""

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers["authorization"] = "Bearer " + self.token
        return request


class JWTAuthTestClient(TestClient):
    def __init__(
        self,
        app: typing.Union[ASGI2App, ASGI3App],
        user: schemas.User,
        db: Session,
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        root_path: str = "",
    ) -> None:

        self.db = db
        self.token = User.manager(self.db).generate_access_token(user.id)

        super().__init__(
            app,
            base_url=base_url,
            raise_server_exceptions=raise_server_exceptions,
            root_path=root_path,
        )

    def request(
        self,
        method: str,
        url: str,
        params: Params = None,
        data: DataType = None,
        headers: typing.MutableMapping[str, str] = None,
        cookies: Cookies = None,
        files: FileType = None,
        timeout: TimeOut = None,
        allow_redirects: bool = None,
        proxies: typing.MutableMapping[str, str] = None,
        hooks: typing.Any = None,
        stream: bool = None,
        verify: typing.Union[bool, str] = None,
        cert: typing.Union[str, typing.Tuple[str, str]] = None,
        json: typing.Any = None,
    ) -> requests.Response:

        return super().request(
            method,
            url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=BearerAuth(self.token),
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
        )
