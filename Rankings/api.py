from fastapi import FastAPI

from .manager import Manager


def build_api(manager: Manager) -> FastAPI:
    app = FastAPI()

    return app
