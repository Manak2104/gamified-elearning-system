from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data to simulate a database
users = []

# Create User
@app.route('/users', methods=['POST'])
def create_user():
    user = request.get_json()
    users.append(user)
    return jsonify(user), 201

# Read Users
@app.route('/users', methods=['GET'])
def read_users():
    return jsonify(users)

# Read User by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def read_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    return jsonify(user)

# Update User
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    updates = request.get_json()
    user.update(updates)
    return jsonify(user)

# Delete User
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u['id'] != user_id]
    return jsonify({'result': 'User deleted'}), 204

if __name__ == '__main__':
    app.run(debug=True)