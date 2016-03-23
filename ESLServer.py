#!flask/bin/python
from flask import Flask, jsonify, make_response, abort, request, url_for
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash


auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'eslpod':
        return 'jude1023'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


app = Flask(__name__)

mysql = MySQL()


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Crdc12fb'
app.config['MYSQL_DATABASE_DB'] = 'eslpod'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

conn = mysql.connect()

item_jason = []


@app.route('/esl/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
        global item_jason
#        item_jason = get_items()
        return jsonify({'tasks': item_jason})

def get_items():
    cursor = conn.cursor()
    #return jsonify({'tasks': map(make_public_task, data)})
    cursor.execute(''' select * from items ''')

    data = cursor.fetchall()
    cursor.close()

    if len(data) is 0:
        abort(404)
    local_jason = []

    for i in data:
        item_data = {'id': i[0],
                     'title': i[1],
                     'mp3url': i[2],
                     'imgurl': i[3],
                     'pubdate': i[4],
                     'durarion': i[5],
                     'description': i[6],
                     'done': i[7],
                     'likes': i[8],
                     'comments': i[9],
                     'downloads': i[10],
                     'plays': i[11],
                     'shares': i[12]}
        local_jason.append(item_data)
    return local_jason

item_jason = get_items()

@app.route('/esl/api/v1.0/tasks/<int:item_id>', methods=['GET'])
def get_task(item_id):
    task = filter(lambda t: t['id'] == item_id, item_jason)
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/esl/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        #        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': request.json.get('done', 0),
        'pubdate': request.json.get('pubdate', ""),
        'downloads': request.json.get('downloads', ""),
        'likes': request.json.get('likes', 0),
        'durarion': request.json.get('durarion', ""),
        'plays': request.json.get('plays', 0),
        'comments': request.json.get('comments', 0),
        'mp3url': request.json.get('mp3url', ""),
        'imgurl': request.json.get('imgurl', ""),
        'shares': request.json.get('shares', 0)
    }
    #    tasks.append(task)
    add_item(task)
    return jsonify({'task': task}), 201


def add_item(data):
    cursor = conn.cursor()
    cursor.callproc('sp_createItem', (data['title'],
                                      data['mp3url'],
                                      data['imgurl'],
                                      data['pubdate'],
                                      data['durarion'],
                                      data['description'],
                                      data['done']))
    cursor.close()
    conn.commit()


def update_item(task_id, data):
    cursor = conn.cursor()
    sqlstr = 'update items set likes=' + str(data['likes']) + ', comments=' + str(data['comments']) + ', plays=' + str(data['plays']) + ', shares=' + str(data['shares']) + ', downloads=' + str(data['downloads']) + ' where id=' + str(task_id)
    cursor.execute(sqlstr)
    cursor.close()
    conn.commit()

# @app.route('/esl/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_item_func(task_id, data):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    update_item(task_id, data)
#    return jsonify({'task': task[0]})
    return task_id


@app.route('/esl/api/v1.0/tasks/<int:task_id>/like', methods=['PUT'])
def update_task_like(task_id):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    old = task[0]['likes']
    task[0]['likes'] = old + 1
    update_item_func(task_id, task[0])
    return jsonify({'task': task[0]})

@app.route('/esl/api/v1.0/tasks/<int:task_id>/play', methods=['PUT'])
def update_task_play(task_id):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    old = task[0]['plays']
    task[0]['plays'] = old + 1
    update_item_func(task_id, task[0])
    return jsonify({'task': task[0]})

@app.route('/esl/api/v1.0/tasks/<int:task_id>/share', methods=['PUT'])
def update_task_share(task_id):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    old = task[0]['shares']
    task[0]['shares'] = old + 1
    update_item_func(task_id, task[0])
    return jsonify({'task': task[0]})

@app.route('/esl/api/v1.0/tasks/<int:task_id>/comment', methods=['PUT'])
def update_task_comment(task_id):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    old = task[0]['comments']
    task[0]['comments'] = old + 1
    update_item_func(task_id, task[0])
    return jsonify({'task': task[0]})

@app.route('/esl/api/v1.0/tasks/<int:task_id>/download', methods=['PUT'])
def update_task_download(task_id):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    old = task[0]['downloads']
    task[0]['downloads'] = old + 1
    update_item_func(task_id, task[0])
    return jsonify({'task': task[0]})

# @app.route('/esl/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, item_jason)
    if len(task) == 0:
        abort(404)
    item_jason.remove(task[0])
    return jsonify({'result': True})


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=None)


