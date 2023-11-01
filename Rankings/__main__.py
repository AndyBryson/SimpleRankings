from datetime import datetime, timedelta, timezone

import click
import uvicorn

from Rankings.api import build_api
from Rankings.data_models import MatchAPI, PlayerAPI
from Rankings.manager import Manager
from Rankings.settings import Settings


@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8080)
@click.option("--debug", is_flag=True)
def main(host: str, port: int, debug: bool):
    settings = Settings()  # TODO: load these
    manager = Manager(config=settings)

    if debug:
        alice = manager.add_player(PlayerAPI(name="Alice Smith"))
        bob = manager.add_player(PlayerAPI(name="Bob Jones"))
        charlie = manager.add_player(PlayerAPI(name="Charlie Brown"))
        charlie_id = str(charlie.id)
        bob_id = str(bob.id)
        alice_id = str(alice.id)
        manager.add_match(
            MatchAPI(result=[alice_id, bob_id], draw=False, date=datetime.now(tz=timezone.utc) - timedelta(hours=1))
        )
        manager.add_match(
            MatchAPI(result=[bob_id, charlie_id], draw=False, date=datetime.now(tz=timezone.utc) - timedelta(hours=2))
        )

    api = build_api(manager=manager, settings=settings)

    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    main()
