import os
import sys
from typing import List, Optional

import dotenv
import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine

from tradecopier.infrastructure.repositories.sql_model import metadata
from tradecopier.restapi.api import api, endpoints
from tradecopier.restapi.deps import Container
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
]

def get_db_connection():
    engine = create_engine(os.environ["DB_DSN"])
    create_db(engine)
    db_conn = engine.connect()
    return db_conn


def create_db(engine):
    metadata.create_all(engine)


def main(argv: Optional[List[str]]):
    config_path = os.environ.get(
        "CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), os.pardir, ".env"),
    )
    dotenv.load_dotenv(config_path)
    db_conn = get_db_connection()
    container = Container()
    container.config.db_dsn.from_env("DB_DSN")
    container.config.token_expire.from_env("TOKEN_EXPIRE_DAYS")
    container.config.secret_key.from_env("SECRET_KEY")
    container.wire(packages=[endpoints])
    pfx = os.environ.get("API_PREFIX", "")
    api_url = pfx + os.environ.get("API_V1_STR", "")

    app = FastAPI(
        title=os.environ.get("PROJECT_NAME", "Trade Copier API"),
        openapi_url=f"{api_url}/openapi.json",
        docs_url=f"{pfx}/docs",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )
    app.include_router(api.api_router, prefix=api_url)
    uvicorn.run(app, host="0.0.0.0", port=os.environ.get("REST_PORT", 8000))


if __name__ == "__main__":
    main(sys.argv[1:])
