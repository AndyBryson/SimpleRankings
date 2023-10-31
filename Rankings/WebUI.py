#!/usr/bin/env python

"""
WebUI.py: A web UI for a Rankings object
"""

from pathlib import Path

from flask import Flask, render_template, request, send_from_directory

from Rankings.manager import Manager
from Rankings.settings import Settings

settings = Settings()
ranking_manager = Manager(settings)

static_directory = Path(__file__).parent / "static"

app = Flask(
    __name__,
    static_folder=static_directory,
    static_url_path="",
)


@app.route("/images/<path:path>")
def send_images(path):
    return send_from_directory(static_directory / "images", path)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory(static_directory / "css", path)


@app.route("/")
def index():
    html = render_template(
        "index.html",
        sport=settings.sport,
        league_title=settings.league_title,
        ranking_manager=ranking_manager,
        players_by_rank=get_players_in_rank_order(),
        show_wins=settings.show_wins,
        show_draws=settings.show_draws,
        show_losses=settings.show_losses,
        show_percent=settings.show_percent,
        show_rating=settings.show_rating,
    )
    return html


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        new_player = request.form["add_name"]
        ranking_manager.add_player(new_player)
    return index()


@app.route("/report_team_result", methods=["GET", "POST"])
def report_team_result():
    if request.method == "POST":
        first = []
        second = []
        third = []
        forth = []

        max_teams = settings.max_teams

        for i in range(settings.max_players_per_game):
            i_first = request.form.get(str(i) + "_first")
            if i_first != "":
                first.append(int(i_first))

            i_second = request.form.get(str(i) + "_second")
            if i_second != "":
                second.append(int(i_second))

            if max_teams > 2:
                i_third = request.form.get(str(i) + "_third")
                if i_third != "":
                    third.append(int(i_third))

            if max_teams > 3:
                i_forth = request.form.get(str(i) + "_forth")
                if i_forth != "":
                    forth.append(int(i_forth))

        draw = request.form.get("team_draw") == "on"

        result = []
        for array in [first, second, third, forth]:
            if array:
                result.append(array)

        if len(result) > 1:
            ranking_manager.add_match(result, draw=draw)

    return match_manager()


@app.route("/report_individual_result", methods=["GET", "POST"])
def report_individual_result():
    if request.method == "POST":
        raw_results = []
        for i in range(1, settings.max_players_per_game + 1):
            raw_results.append(request.form.get(str(i)))

        proper_results = []
        for player in raw_results:
            if player == "":
                continue

            if int(player) not in proper_results:
                proper_results.append([int(player)])

        draw = request.form.get("ind_draw") == "on"

        if len(proper_results) > 1:
            ranking_manager.add_match(proper_results, draw=draw)

    return match_manager()


@app.route("/user_manager")
def user_manager():
    html = render_template(
        "user_manager.html",
        sport=settings.sport,
        players_by_name=get_players_in_name_order(True),
        league_title=settings.league_title,
    )
    return html


@app.route("/user_mod", methods=["GET", "POST"])
def user_mod():
    if request.method == "POST":
        user = request.form.get("user")
        name = request.form.get("name")
        active = request.form.get("active") == "on"

        if user != "" and name != "":
            ranking_manager.set_name(int(user), name)

        ranking_manager.set_active(int(user), active)

    return user_manager()


@app.route("/match_manager")
def match_manager():
    html = render_template(
        "match_manager.html",
        sport=settings.sport,
        support_draws=settings.support_draws,
        matches=list(reversed(ranking_manager.matches)),
        players_dict=ranking_manager.players,
        league_title=settings.league_title,
        players_by_name=get_players_in_name_order(),
        max_players=settings.max_players_per_game,
        max_teams=settings.max_teams,
        support_individual=settings.support_individual,
    )
    return html


@app.route("/match_mod", methods=["GET", "POST"])
def match_mod():
    if request.method == "POST":
        match_to_delete = request.form.get("match_to_delete")
        if match_to_delete != "":
            ranking_manager.delete_match(int(match_to_delete))
    return match_manager()


@app.route("/head_to_head")
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
                        team_game = False
                        match_players = []
                        for team in match.result_array:
                            if len(team) > 1:
                                team_game = True
                                break
                            match_players += team

                        if not team_game:
                            for player_id in match_players:
                                if player_id is player_ids[i]:
                                    i_found = True
                                    continue

                                if player_id is player_ids[j]:
                                    if i_found is True:
                                        count += 1
                                    else:
                                        break

                matrix[i][j] = count

    html = render_template(
        "head_to_head.html", sport=settings.sport, headings=headings, matrix=matrix, league_title=settings.league_title
    )
    return html


def remove_inactive_players(players):
    return [x for x in players if x.active]


def remove_no_game_players(players):
    return [x for x in players if x.played_match]


def get_players_in_rank_order(remove_inactive=True, remove_never_played=False):
    players = list(ranking_manager.players.values())
    sort_by = settings.sort_by
    if sort_by.lower() == "nrating":
        players.sort(key=lambda x: (x.played_match, x.normalised_rating), reverse=True)
    elif sort_by.lower() == "true_skill" and settings.use_true_skill is True:
        players.sort(key=lambda x: (x.played_match, x.true_skill.mu), reverse=True)
    else:
        players.sort(key=lambda x: (x.played_match, x.rating), reverse=True)

    if remove_inactive is True:
        players = remove_inactive_players(players)

    if remove_never_played is True:
        players = remove_no_game_players(players)

    return players


def get_players_in_name_order(remove_inactive=True, remove_never_played=False):
    players = list(ranking_manager.players.values())
    players.sort(key=lambda x: x.short_name.lower())

    if remove_inactive is True:
        players = remove_inactive_players(players)

    if remove_never_played is True:
        players = remove_no_game_players(players)

    return players


@app.route("/<path:path>")
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


def start_flask(host, port):
    app.run(host=host, port=port, threaded=True)


if __name__ == "__main__":
    start_flask(settings.host, settings.port)
