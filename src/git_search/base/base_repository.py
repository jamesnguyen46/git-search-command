from http import HTTPStatus
import requests


class BaseRepository:
    def __init__(self, base_url, common_header=None):
        self.base_url = base_url
        self.common_header = common_header

    def send_http_get(self, api_path, request_param=None):
        try:
            response = requests.get(
                url=f"{self.base_url}/{api_path}",
                params=request_param,
                headers=self.common_header,
            )
            if response.status_code != HTTPStatus.OK:
                return (
                    False,
                    f"[Error] Api \"{api_path}\" : {response.json()['message']}",
                )

            return True, response
        except Exception as error:
            return False, f'[Error] Api "{api_path}" : {error} occurred.'
