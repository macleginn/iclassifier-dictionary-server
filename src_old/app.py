import sqlite3

from flask import request, make_response, jsonify, Flask

# Global data
CORS_ORIGIN = 'https://www.iclassifier.pw'
# CORS_ORIGIN = '192.236.176.184'
SUPPORTED_LANGUAGES = [
    'chinese',
    'tla'
]
conn = sqlite3.connect('../data/dictionary.sqlite')
cursor = conn.cursor()

# Flask app
app = Flask(__name__)


# Helper funs
def row2dict(row_tuple):
    """
    Converts a subset of a table row 
    to a dictionary with named fields.
    """
    return {
        'entry': row_tuple[2],
        'short_meaning': row_tuple[3]
    }


@app.route('/<language>/byid', methods=['GET'])
def byid(language):
    entry_id = request.args.get('id',
                                default = -1,
                                type = int)
    if language not in SUPPORTED_LANGUAGES:
        resp = make_response(
            'There is no dictionary for this language.', 400)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
        return resp
    elif entry_id == -1:
        resp = make_response('No valid lemma id provided.', 400)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
        return resp

    # language is bound to be in SUPPORTED_LANGUAGES
    # by this point; no injection is possible.
    result = cursor.execute(
        f"""
        SELECT * FROM {language}
        WHERE id = ?""",
        (entry_id,)).fetchone()
    if not result:
        resp = make_response(
            f'Entry with id {entry_id} was not found.', 404)
    else:
        resp_dict = row2dict(result)
        resp = make_response(
            jsonify(resp_dict),
            200)
    resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
    return resp


@app.route('/<language>/bystringid', methods=['GET'])
def bystringid(language):
    entry_id = request.args.get('id',
                                default = '---',
                                type = str)
    if language not in SUPPORTED_LANGUAGES:
        resp = make_response(
            'There is no dictionary for this language.', 400)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
        return resp
    elif entry_id == '---':
        resp = make_response('No valid lemma id provided.', 400)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
        return resp

    # language is bound to be in SUPPORTED_LANGUAGES
    # by this point; no injection is possible.
    result = cursor.execute(
        f"""
        SELECT * FROM {language}
        WHERE `string_id` = ?""",
        (entry_id,)).fetchone()
    if not result:
        resp = make_response(
            f'Entry with string id "{entry_id}" was not found.',
            404)
    else:
        resp_dict = row2dict(result)
        resp = make_response(
            jsonify(resp_dict),
            200)
    resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
    return resp


@app.route('/<language>/bysubstring', methods=['GET'])
def bysubstring(language):
    substr = request.args.get('substr',
                                default = '---',
                                type = str)
    if language not in SUPPORTED_LANGUAGES:
        resp = make_response(
            'There is no dictionary for this language.', 400)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
        return resp
    elif substr == '---':
        resp = make_response('No valid lemma part provided.',
                             400)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
        return resp

    # language is bound to be in SUPPORTED_LANGUAGES
    # by this point; no injection is possible.
    result = cursor.execute(
        f"""
        SELECT * FROM {language}
        WHERE `string_id` like ?
        """,
        ('%'+substr+'%',)
    )
    resp_dict = {}
    for row in result:
        row_id = row[0]
        row_dict = row2dict(row)
        resp_dict[row_id] = row_dict
    resp = make_response(
        jsonify(resp_dict),
        200)
    resp.headers['Access-Control-Allow-Origin'] = CORS_ORIGIN
    return resp
