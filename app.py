from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for tasks (no database yet).
tasks = []
next_id = 1


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required"}), 400

    task = {"id": next_id, "title": title.strip(), "done": False}
    tasks.append(task)
    next_id += 1

    return jsonify(task), 201


if __name__ == "__main__":
    app.run(debug=True)
