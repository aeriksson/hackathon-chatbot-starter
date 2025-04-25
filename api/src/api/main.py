from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from opperai import Opper

from .clients.postgres import PostgresChatClient
from .routes import router
from .utils import log
from . import conf

log.init(conf.get_log_level())
logger = log.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    pg_conf = conf.get_postgres_conf()
    app.state.db = PostgresChatClient(
        hostname=pg_conf.hostname,
        db=pg_conf.db,
        username=pg_conf.username,
        password=pg_conf.password,
    )
    try:
        app.state.db.connect()
        logger.info("Connected to Postgres")
    except Exception:
        logger.warning("Couldn't connect to Postgres - retrying on next request.")
    app.state.opper = Opper(api_key=conf.get_opper_api_key())

    yield

app = FastAPI(
    title="Customer Support Chat API",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)
app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    if not conf.validate():
        raise ValueError("Invalid configuration.")

    http_conf = conf.get_http_conf()
    logger.info(f"Starting API on port {http_conf.port}")
    uvicorn.run(
        "api.main:app",
        host=http_conf.host,
        port=http_conf.port,
        reload=http_conf.autoreload,
        log_level="debug" if http_conf.debug else "info",
        log_config=None
    )
