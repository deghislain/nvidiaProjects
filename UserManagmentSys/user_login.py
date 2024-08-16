import json
from flask import Flask, request, Response

app = Flask(__name__)


@app.route("/login", methods=['GET'])
def login():
    print("login called")
    with open('users.json') as file:
        users = json.load(file)
    user_data = request.json

    u = user_data['username']
    p = user_data['password']

    response = None
    for user in users:
        if user['username'] == u and user['password'] == p:
            print(user)
            response = Response(response=json.dumps(user), status=200, mimetype='application/json')
            break
        else:
            response = Response(response="User not found", status=404, mimetype='application/json')

    return response


if __name__ == "__main__":
    app.run(port=8080)
