from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_swagger_ui import get_swaggerui_blueprint
from schemas import UserSchema, TaskSchema
from error_handlers import register_error_handlers
from database import db, cursor

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key
jwt = JWTManager(app)

# Register global error handlers
register_error_handlers(app)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.json'  # Path to your API specification file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Task Management API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def home():
    return "Task Management API"

@app.route('/register', methods=['POST'])
def register():
    try:
        data = UserSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    username = data['username']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return jsonify({"message": "Username already exists"}), 400

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    try:
        data = UserSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    username = data['username']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user['id'])
    return jsonify({"access_token": access_token}), 200

@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    try:
        data = TaskSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    title = data['title']
    description = data.get('description')
    due_date = data.get('due_date')
    user_id = get_jwt_identity()

    cursor.execute(
        "INSERT INTO tasks (title, description, due_date, user_id) VALUES (%s, %s, %s, %s)",
        (title, description, due_date, user_id)
    )
    db.commit()
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cursor.fetchall()
    return jsonify(tasks), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        data = TaskSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    title = data['title']
    description = data.get('description')
    status = data.get('status')
    due_date = data.get('due_date')
    user_id = get_jwt_identity()

    cursor.execute(
        "UPDATE tasks SET title = %s, description = %s, status = %s, due_date = %s WHERE id = %s AND user_id = %s",
        (title, description, status, due_date, task_id, user_id)
    )
    db.commit()
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
    db.commit()
    return jsonify({"message": "Task deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)