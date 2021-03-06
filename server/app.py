from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import numpy as np
import flask
import uuid

import minesweeper

GAMES = {"TEST": minesweeper.Game()}

app = Flask(__name__, static_folder="../build")
CORS(app)


class NumpyEncoder(json.JSONEncoder):
    """
    Extends json dumps to recursively convert numpy arrays to lists
    """

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def find_game_state(game_id):
    """
    Returns json blob with current state of game with specific id

    Args:
        game (minesweeper.Game)

    Returns:
        response (string): json blog of game state
    """
    game = GAMES[game_id]
    response = {
        "game_id": game_id,
        "revealed_state": game.revealed_state,
        "unclicked_non_mine_count": game.unclicked_non_mine_count,
        "has_won": game.has_won,
        "has_lost": game.has_lost,
    }
    return json.dumps(response, cls=NumpyEncoder)


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({"error": "Not found"}), 404)


##
# API routes
##


@app.route("/api/ping", methods=["GET"])
def health_check():
    """ 
    Health check 

    Required headers:
        None

    Required body:
        None
    """
    return "Response"


@app.route("/api/game_state/<string:game_id>", methods=["GET"])
def get_state(game_id):
    """ 
    Return current state of game with specificed game_id

    Headers
        None

    Returns
        game_state (dict): state of game
    """
    return find_game_state(game_id)


@app.route("/api/click", methods=["POST"])
def make_click():
    """
    Click on cell and return updated game state

    Headers
        (Content-Type, application/json)

    Body
        {'game_id':game_id_to_update,
        'x':x_coordinate_to_click,
        'y':y_coordinate_to_click}

    Returns
        game_state (dict): state of game
    """
    move_inputs = json.loads(flask.request.data)
    global GAMES
    GAMES[move_inputs["game_id"]].click(int(move_inputs["x"]), int(move_inputs["y"]))
    return find_game_state(move_inputs["game_id"])


@app.route("/api/create", methods=["POST"])
def reset_game():
    """
    Create new game with specified game parameters

    Headers
        (Content-Type, application/json)

    Body (all optional)
        {'x_max':number_of_rows (default 10),
        'y_max':number_of_cols (default 10),
        'num_mines':number_of_miens (default 10)}

    Returns
        game_state (dict): state of game
    """
    game_inputs = json.loads(flask.request.data)
    game_id = str(uuid.uuid4())
    global GAMES
    GAMES[game_id] = minesweeper.Game(**game_inputs)
    return find_game_state(game_id)


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
