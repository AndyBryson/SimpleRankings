#!/usr/bin/env python

"""
WebUI.py: A web UI for a Rankings object
"""

import inspect
import os
from Rankings import Manager
from ConfigParser import ConfigParser

from flask import Flask, render_template, send_from_directory, request


__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "GPLv3"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


app = Flask(__name__
            , static_folder=os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'static')
            , static_url_path='')


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory(os.path.join(app.static_folder, 'images'), path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.join(app.static_folder, 'css'), path)


@app.route('/')
def index():
    sport = config.get("ui", "sport")
    show_wins = config.getboolean("ui", "show_wins")
    show_draws = config.getboolean("ui", "show_draws")
    show_losses = config.getboolean("ui", "show_losses")
    show_percent = config.getboolean("ui", "show_percent")
    show_rating = config.getboolean("ui", "show_rating")
    show_normalised_rating = config.getboolean("ui", "show_normalised_rating")
    html = render_template('index.html',
                           sport=sport,
                           league_title=config.get("ui", "league_title"),
                           ranking_manager=ranking_manager,
                           players_by_rank=get_players_in_rank_order(),
                           show_wins=show_wins,
                           show_draws=show_draws,
                           show_losses=show_losses,
                           show_percent=show_percent,
                           show_rating=show_rating,
                           show_normalised_rating=show_normalised_rating)
    return html


@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    if request.method == 'POST':
        new_player = request.form["add_name"]
        print new_player
        ranking_manager.add_player(new_player)
    return index()


@app.route('/report_result', methods=["GET", "POST"])
def report_result():
    if request.method == 'POST':
        raw_results = []
        for i in range(1, config.getint("ui", "max_players_per_game") + 1):
            raw_results.append(request.form.get(str(i)))

        proper_results = []
        for player in raw_results:
            if player == "":
                continue

            if int(player) not in proper_results:
                proper_results.append(int(player))
        draw = request.form.get("draw") == "on"

        if len(proper_results) > 1:
            ranking_manager.match(proper_results, draw=draw)

    return match_manager()


@app.route('/user_manager')
def user_manager():
    html = render_template('user_manager.html',
                           sport=config.get("ui", "sport"),
                           players_by_name=get_players_in_name_order(True),
                           league_title=config.get("ui", "league_title"))
    return html


@app.route('/user_mod', methods=["GET", "POST"])
def user_mod():
    if request.method == 'POST':
        user = request.form.get("user")
        name = request.form.get("name")
        active = request.form.get("active") == "on"

        if user != "" and name != "":
            ranking_manager.set_name(int(user), name)

        ranking_manager.set_active(int(user), active)

    return user_manager()


@app.route('/match_manager')
def match_manager():
    html = render_template('match_manager.html',
                           sport=config.get("ui", "sport"),
                           support_draws=config.get("ui", "support_draws"),
                           matches=list(reversed(ranking_manager.matches)),
                           players_dict=ranking_manager.players,
                           league_title=config.get("ui", "league_title"),
                           players_by_name=get_players_in_name_order(),
                           max_players=config.getint("ui", "max_players_per_game"))
    return html


@app.route('/match_mod', methods=["GET", "POST"])
def match_mod():
    if request.method == 'POST':
        match_to_delete = request.form.get("match_to_delete")
        if match_to_delete != "":
            ranking_manager.delete_match(int(match_to_delete))
    return match_manager()


@app.route('/head_to_head')
def head_to_heads():
    headings = []
    players = get_players_in_name_order(remove_never_played=True)
    player_ids = []
    for player in players:
        headings.append(player.short_name)
        player_ids.append(player.player_id)

    matrix = [0 for player in players]
    for i in range(0, len(matrix)):
        matrix[i] = [0 for player in players]

    for i in range(0, len(player_ids)):
        for j in range(0, len(player_ids)):
            if i is j:
                matrix[i][j] = "X"
            else:
                count = 0
                for match in ranking_manager.matches:
                    if match.draw is True and i in match.result_array:
                        count += 0.5
                    else:
                        i_found = False
                        for player_id in match.result_array:
                            if player_id is player_ids[i]:
                                i_found = True
                                continue

                            if player_id is player_ids[j]:
                                if i_found is True:
                                    count += 1
                                else:
                                    break

                matrix[i][j] = count

    html = render_template('head_to_head.html',
                           sport=config.get("ui", "sport"),
                           headings=headings,
                           matrix=matrix,
                           league_title=config.get("ui", "league_title"))
    return html


def remove_inactive_players(players):
    return [x for x in players if x.active]


def remove_no_game_players(players):
    return [x for x in players if x.played_match]


def get_players_in_rank_order(remove_inactive=True, remove_never_played=False):
    players = ranking_manager.players.values()
    if config.getboolean("ui", "sort_by_normalised") is True:
        players.sort(key=lambda x: (x.played_match, x.normalised_rating), reverse=True)
    else:
        players.sort(key=lambda x: (x.played_match, x.rating), reverse=True)

    if remove_inactive is True:
        players = remove_inactive_players(players)

    if remove_never_played is True:
        players = remove_no_game_players(players)

    return players


def get_players_in_name_order(remove_inactive=True, remove_never_played=False):
    players = ranking_manager.players.values()
    players.sort(key=lambda x: x.short_name.lower())

    if remove_inactive is True:
        players = remove_inactive_players(players)

    if remove_never_played is True:
        players = remove_no_game_players(players)

    return players

@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


def start_flask(host, port):
    app.run(host=host,
            port=port)


ranking_manager = None
config = None


class FlaskInterface(object):
    def __init__(self, config_in, manager):
        global ranking_manager
        self.__config = config_in
        self.init_config()
        ranking_manager = manager
        global config
        config = config_in

    def init_config(self):
        if self.__config.has_section("ui") is False:
            self.__config.add_section("ui")

        if self.__config.has_option("ui", "host") is False:
            self.__config.set("ui", "host", "0.0.0.0")

        if self.__config.has_option("ui", "port") is False:
            self.__config.set("ui", "port", "180")

        if self.__config.has_option("ui", "show_wins") is False:
            self.__config.set("ui", "show_wins", "1")

        if self.__config.has_option("ui", "show_losses") is False:
            self.__config.set("ui", "show_losses", "1")

        if self.__config.has_option("ui", "show_draws") is False:
            self.__config.set("ui", "show_draws", "1")

        if self.__config.has_option("ui", "show_percent") is False:
            self.__config.set("ui", "show_percent", "1")

        if self.__config.has_option("ui", "show_rating") is False:
            self.__config.set("ui", "show_rating", "1")

        if self.__config.has_option("ui", "show_normalised_rating") is False:
            self.__config.set("ui", "show_normalised_rating", "0")

        if self.__config.has_option("ui", "sort_by_normalised") is False:
            self.__config.set("ui", "sort_by_normalised", "0")

        if self.__config.has_option("ui", "support_draws") is False:
            self.__config.set("ui", "support_draws", "1")

        if self.__config.has_option("ui", "max_players_per_game") is False:
            self.__config.set("ui", "max_players_per_game", "2")

        with open(self.__config.file_name, 'wb') as configfile:
            self.__config.write(configfile)

    def start(self):
        host = self.__config.get("ui", "host")
        port = self.__config.getint("ui", "port")
        start_flask(host, port)
        print("start")


