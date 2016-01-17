import argparse

from Rankings import Manager
from WebUI import FlaskInterface


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str,
                        help="What is the league called (for display)",
                        default=None)
    args = parser.parse_args()
    ranking_manager = Manager()
    if args.name is not None:
        ranking_manager.league_title = args.name

    flask_interface = FlaskInterface(ranking_manager)
    flask_interface.start()

