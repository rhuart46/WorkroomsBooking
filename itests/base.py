import os
from typing import BinaryIO, ClassVar, Optional
from unittest import TestCase

from flask import Flask
from flask.testing import FlaskClient
import requests

from configs import config
from manage_storage import empty_sqlite_db, init_sqlite_db

from app import create_app


class IntegrationTest(TestCase):
    app: ClassVar[Flask]
    client: ClassVar[FlaskClient]
    db_fd: ClassVar[BinaryIO]
    db_file_name: ClassVar[str]

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self) -> None:
        init_sqlite_db()

    def tearDown(self) -> None:
        empty_sqlite_db()
        os.remove(config.DATABASE_URI.replace("sqlite:///", ""))

    def run(self, result=None):
        with self.app.test_client() as test_client:
            self.test_client = test_client
            super(IntegrationTest, self).run(result)

    @classmethod
    def _make_url(cls, namespace_root: str, endpoint: Optional[str]) -> str:
        _namespace_root = "/" + namespace_root if namespace_root[0] != "/" else namespace_root
        if endpoint is not None:
            return "/".join((_namespace_root, endpoint)).replace("//", "/")
        else:
            return _namespace_root

    def bookings_api_get(self, endpoint: Optional[str] = None, **kwargs) -> requests.Response:
        return self.test_client.get(self._make_url("bookings", endpoint), follow_redirects=True, **kwargs)

    def bookings_api_post(self, endpoint: Optional[str] = None, **kwargs) -> requests.Response:
        return self.test_client.post(self._make_url("bookings", endpoint), follow_redirects=True, **kwargs)

    def bookings_api_delete(self, endpoint: Optional[str] = None, **kwargs) -> requests.Response:
        return self.test_client.delete(self._make_url("bookings", endpoint), follow_redirects=True, **kwargs)

    def rooms_api_get(self, endpoint: Optional[str] = None, **kwargs) -> requests.Response:
        return self.test_client.get(self._make_url("rooms", endpoint), follow_redirects=True, **kwargs)
