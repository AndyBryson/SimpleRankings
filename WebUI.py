#!/usr/bin/env python

"""
WebUI.py: A web UI for a Rankings object
"""

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"

from flask import Flask, render_template, send_from_directory, request
import os
import inspect

from Rankings import Manager


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
    html = render_template('index.html',
                           league_title=ranking_manager.league_title,
                           ranking_manager=ranking_manager,
                           players_by_rank=ranking_manager.get_players_in_rank_order(),
                           players_by_name=ranking_manager.get_players_in_name_order())
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
        winner = request.form.get("winner")
        loser = request.form.get("loser")
        if winner != loser and winner != "" and loser != "":
            ranking_manager.match(int(winner), int(loser))
    return match_manager()


@app.route('/user_manager')
def user_manager():
    html = render_template('user_manager.html',
                           players_by_name=ranking_manager.get_players_in_name_order(True),
                           league_title=ranking_manager.league_title)
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
                           matches=ranking_manager.matches,
                           players_dict=ranking_manager.players,
                           league_title=ranking_manager.league_title,
                           players_by_name=ranking_manager.get_players_in_name_order())
    return html


@app.route('/match_mod', methods=["GET", "POST"])
def match_mod():
    if request.method == 'POST':
        match_to_delete = request.form.get("match_to_delete")
        if match_to_delete != "":
            ranking_manager.delete_match(int(match_to_delete))
    return match_manager()


@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


def start_flask(host, port):
    app.run(host=host,
            port=port)


ranking_manager=None


class FlaskInterface(object):
    def __init__(self, manager, host="0.0.0.0", port=180):
        global ranking_manager
        ranking_manager = manager
        self.__host = host
        self.__port = port

    def start(self):
        start_flask(self.__host, self.__port)
        print("start")


