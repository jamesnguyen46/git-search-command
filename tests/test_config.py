from gsc import config

# Test BaseConfig
MOCK_ENV_FILE_NAME = "test"
mock_data = {"key1": "value1", "key2": "value2"}


def test_get_key(mocker):
    mocker.patch("dotenv.dotenv_values", return_value=mock_data)
    baseconfig = config.BaseConfig(MOCK_ENV_FILE_NAME)
    assert baseconfig.get_key("key1") == mock_data["key1"]
    assert baseconfig.get_key("key2") == mock_data["key2"]


# Test AppConfig

# Test GitLabConfig

# Test GitHubConfig
