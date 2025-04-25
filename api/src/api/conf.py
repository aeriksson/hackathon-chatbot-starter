from pydantic import BaseModel

from .utils import env, log
from .utils.env import EnvVarSpec

logger = log.get_logger(__name__)

#### Types ####

class HttpServerConf(BaseModel):
    host: str
    port: int
    debug: bool
    autoreload: bool

class PostgresConf(BaseModel):
    hostname: str
    db: str
    username: str
    password: str

#### Env Vars ####

## Logging ##

LOG_LEVEL = EnvVarSpec(id="LOG_LEVEL", default="INFO")

## HTTP ##

HTTP_HOST = EnvVarSpec(id="HTTP_HOST", default="0.0.0.0")

HTTP_PORT = EnvVarSpec(id="HTTP_PORT", default="8000")

HTTP_DEBUG = EnvVarSpec(
    id="HTTP_DEBUG",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

HTTP_AUTORELOAD = EnvVarSpec(
    id="HTTP_AUTORELOAD",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

## Opper ##

OPPER_API_KEY = EnvVarSpec(id="OPPER_API_KEY", is_secret=True)

## Postgres ##

POSTGRES_DATABASE = EnvVarSpec(id="POSTGRES_DATABASE", default="postgres")
POSTGRES_PASSWORD = EnvVarSpec(id="POSTGRES_PASSWORD", is_secret=True, default="password")
POSTGRES_HOSTNAME = EnvVarSpec(id="POSTGRES_HOSTNAME")
POSTGRES_USERNAME = EnvVarSpec(id="POSTGRES_USERNAME", default="postgres")

#### Validation ####

def validate() -> bool:
    return env.validate(
        [
            LOG_LEVEL,
            HTTP_PORT,
            HTTP_DEBUG,
            HTTP_AUTORELOAD,
            OPPER_API_KEY,
            POSTGRES_HOSTNAME,
            POSTGRES_DATABASE,
            POSTGRES_USERNAME,
        ]
    )

#### Getters ####

def get_log_level() -> str:
    return env.parse(LOG_LEVEL)

def get_http_conf() -> HttpServerConf:
    return HttpServerConf(
        host=env.parse(HTTP_HOST),
        port=env.parse(HTTP_PORT),
        debug=env.parse(HTTP_DEBUG),
        autoreload=env.parse(HTTP_AUTORELOAD),
    )

def get_postgres_conf() -> PostgresConf:
    return PostgresConf(
        hostname=env.parse(POSTGRES_HOSTNAME),
        db=env.parse(POSTGRES_DATABASE),
        username=env.parse(POSTGRES_USERNAME),
        password=env.parse(POSTGRES_PASSWORD),
    )

def get_opper_api_key() -> str:
    return env.parse(OPPER_API_KEY)
