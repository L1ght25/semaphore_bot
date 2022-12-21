import os
import json
from flask import Flask, make_response, request

app = Flask(__name__)
app.secret_key = os.getenv('PASSWORD')

with open('./data/database.json', 'r') as file:
    aneks_database = json.load(file)


@app.route("/get-aneks", methods=['GET'])
def get_aneks():
    password = request.form.get('password')
    if password != app.secret_key:
        return 'Authorization error'
    return make_response(aneks_database)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)