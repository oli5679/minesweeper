from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import numpy as np
import flask

import minesweeper

GAME = minesweeper.Game()

for row in GAME.mine_locations:
    print(row)

app = Flask(__name__, static_folder="../build")
CORS(app)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def format_game_state(game):
    response = {
        "revealed_state": game.revealed_state,
        "unclicked_non_mine_count": game.unclicked_non_mine_count,
        "has_won": game.has_won,
        "has_lost": game.has_lost,
    }
    return json.dumps(response, cls=NumpyEncoder)


##
# API routes
##


@app.route("/ping")
def health_check():
    return "Response"


@app.route("/game_state", methods=["GET"])
def get_state():
    return format_game_state(GAME)


@app.route("/click", methods=["POST"])
def make_click():
    move_inputs = json.loads(flask.request.data)
    global GAME
    GAME.click(int(move_inputs["x"]), int(move_inputs["y"]))
    return format_game_state(GAME)


@app.route("/reset", methods=["POST"])
def reset_game():
    game_inputs = json.loads(flask.request.data)
    global GAME
    GAME = minesweeper.Game(**game_inputs)
    return format_game_state(GAME)


##
# View route
##


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    """Return index.html for all non-api routes"""
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
