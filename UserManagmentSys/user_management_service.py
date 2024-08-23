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


@app.route("/create", methods=['POST'])
def create_new_account():
    try:
        print("create_new_account called")
        with open('users.json') as file:
            users = json.load(file)
        new_user = request.json
        users.append(new_user)

        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
    except FileNotFoundError:
        print(f"Error: The file users.json was not found.")
        return Response(response="Error while storing the new user", status=500, mimetype='application/json')
    except json.JSONDecodeError:
        print("Error: The file does not contain valid JSON.")
        return Response(response="Error while parsing user json file", status=500, mimetype='application/json')
    except ValueError as ve:
        print(f"Error: {ve}")

    return Response(response="User successfully stored", status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(port=8080)
