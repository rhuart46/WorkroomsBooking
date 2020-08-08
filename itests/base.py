from typing import Any
from unittest import TestCase

import requests

# TODO: this would be to handle differently when running tests on any nonlocal environment:
from configs.local import HOST, PORT


class IntegrationTest(TestCase):

    def _make_url(self, namespace_root: str, endpoint: str) -> str:
        return "/".join((f"{HOST}:{PORT}", namespace_root, endpoint)).replace("//", "/")

    def bookings_api_get(self, endpoint: str, **kwargs) -> Any:
        return requests.get(self._make_url("bookings", endpoint), **kwargs)

    def bookings_api_post(self, endpoint: str, **kwargs) -> Any:
        return requests.post(self._make_url("bookings", endpoint), **kwargs)

    def bookings_api_delete(self, endpoint: str, **kwargs) -> Any:
        return requests.delete(self._make_url("bookings", endpoint), **kwargs)

    def rooms_api_get(self, endpoint: str, **kwargs) -> Any:
        return requests.get(self._make_url("rooms", endpoint), **kwargs)
