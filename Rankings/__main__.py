import click
import uvicorn

from Rankings.api import build_api
from Rankings.manager import Manager
from Rankings.settings import Settings


@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8080)
def main(host: str, port: int):
    settings = Settings()  # TODO: load these
    manager = Manager(config=settings)
    api = build_api(manager=manager)

    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    main()
