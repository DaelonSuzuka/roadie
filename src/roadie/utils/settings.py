from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: Literal['LOCAL', 'DEV', 'PROD'] = 'LOCAL'

    DEVELOPMENT: bool = True