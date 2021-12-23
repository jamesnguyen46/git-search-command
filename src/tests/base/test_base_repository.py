from http import HTTPStatus
import json
import unittest
import mock
from git_search.base.base_repository import BaseRepository


class TestBaseRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.patch = mock.patch("git_search.base.base_repository.requests.get")
        self.get_method = self.patch.start()

    def tearDown(self) -> None:
        self.patch.stop()

    def test_send_http_get_success(self) -> None:
        mock_resp = mock.Mock()
        mock_resp.status_code = HTTPStatus.OK
        with open("tests/mock_json/response_success.json", encoding="utf-8") as file:
            mock_body = json.load(file)
            mock_resp.json = mock.Mock(return_value=mock_body)
        self.get_method.return_value = mock_resp

        result, response = BaseRepository(mock.Mock()).send_http_get(mock.Mock())
        self.assertTrue(result)
        self.assertEqual(response.json(), mock_body)

    def test_send_http_get_failed_404(self) -> None:
        api_path = "test_send_http_get_failed_404"
        mock_resp = mock.Mock()
        mock_resp.status_code = HTTPStatus.NOT_FOUND
        with open("tests/mock_json/response_failed_404.json", encoding="utf-8") as file:
            mock_body = json.load(file)
            mock_resp.json = mock.Mock(return_value=mock_body)
        self.get_method.return_value = mock_resp

        result, response = BaseRepository(mock.Mock()).send_http_get(api_path)
        self.assertFalse(result)
        self.assertEqual(
            response, f"[Error] Api \"{api_path}\" : {mock_body['message']}"
        )

    def test_send_http_get_failed_throw_exception(self) -> None:
        api_path = "test_send_http_get_failed_throw_exception"
        mock_exception = ConnectionError()
        self.get_method.side_effect = mock_exception

        result, response = BaseRepository(mock.Mock()).send_http_get(api_path)
        self.assertFalse(result)
        self.assertEqual(
            response, f'[Error] Api "{api_path}" : {mock_exception} occurred.'
        )
