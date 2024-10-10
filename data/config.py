from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    RANDOM_BET_COUNT: list[int] = [100, 150, 200, 500]

    SLEEP_BETWEEN_PLAY: list[float] = [3, 5]
    SLEEP_BY_LOW_PIR: list[float] = [1800, 2400]

    MINIMAL_PIR_BALANCE: int = 500
    PLAY_GAME: bool = True

    USE_PROXY_FROM_FILE: bool = False  # True - if use proxy from file, False - if use proxy from accounts.json
    PROXY_PATH: str = "data/proxy.txt"
    PROXY_TYPE_TG: str = "socks5"  # proxy type for tg client. "socks4", "socks5" and "http" are supported
    # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
    PROXY_TYPE_REQUESTS: str = "socks5"

    WORKDIR: str = 'sessions/'

    # timeout in seconds for checking accounts on valid
    TIMEOUT: int = 30

    DELAY_CONN_ACCOUNT: list[int] = [5, 15]


config = Settings()
