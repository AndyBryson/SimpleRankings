import argparse
from ConfigParser import ConfigParser

from Rankings import Manager
from WebUI import FlaskInterface


if __name__ == "__main__":
    config = ConfigParser()
    config.file_name = "config.txt"
    config.read(config.file_name)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str,
                        help="What is the league called (for display)",
                        default=None)
    parser.add_argument("-s", "--sport", type=str,
                        help="What sport are you playing (for display)",
                        default=None)
    args = parser.parse_args()

    if config.has_section("ui") is False:
        config.add_section("ui")

    if args.name is not None:
        config.set("ui", "league_title", args.name)
    elif config.has_option("ui", "league_title") is False:
        config.set("ui", "league_title", "")

    if args.sport is not None:
        config.set("ui", "sport", args.sport)
    elif config.has_option("ui", "sport") is False:
        config.set("ui", "sport", "")

    with open(config.file_name, 'wb') as configfile:
        config.write(configfile)

    ranking_manager = Manager(config)

    flask_interface = FlaskInterface(config, ranking_manager)
    flask_interface.start()

