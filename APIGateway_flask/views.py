#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth,HTTPDigestAuth
from APIGateway_flask import app
from backend import tasks, users 

digest_auth = HTTPDigestAuth()

@digest_auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@digest_auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
basic_auth = HTTPBasicAuth()

@basic_auth.get_password
def get_password(username):
    if username in users:
        return users.get(username)
    return None

@basic_auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@basic_auth.login_required
def get_tasks():
    app.logger.info('IP=' + request.remote_addr + ',HTTP=GET' + ',method=get_tasks' + ',description=return_all_tasks')
    app.logger.debug('task_count=' + str(len(tasks)))
    if len(tasks) == 0: app.logger.warning('message=no_tasks_found')
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    app.logger.info('IP=' + request.remote_addr + ',HTTP=GET' + ',method=get_task' + ',description=return_task_for_given_id')
    app.logger.debug('task_id=' + str(task_id))
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    app.logger.info('IP=' + request.remote_addr + ',HTTP=POST' + ',method=create_task' + ',description=create_task_with_given_data')
    if not request.json or not 'title' in request.json:
        app.logger.warning('message=missing_title_or_no_data')
        abort(400)
    app.logger.debug('data='+str(request.json))
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    app.logger.info('IP=' + request.remote_addr + ',HTTP=PUT' + ',method=update_task' + ',description=update_task_with_given_data_and_task_id')
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    app.logger.debug('task_id=' + str(task_id) + ',data='+str(request.json))
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    app.logger.info('IP=' + request.remote_addr + ',HTTP=DELETE' + ',method=delete_task' + ',description=delete_task_with_given_task_id')
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    app.logger.debug('task_id=' + str(task_id))
    tasks.remove(task[0])
    return jsonify({'result': True})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)