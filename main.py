import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
import datetime
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from croniter import croniter

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)

scheduler = BackgroundScheduler()


def init_db():
    conn = sqlite3.connect('task.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS tasks '
                   '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                   'url TEXT, '
                   'method TEXT, '
                   'params TEXT, '
                   'interval INTEGER, '
                   'cron TEXT, '
                   'last_run_time DATETIME, '
                   'next_run_time DATETIME, '
                   'status INTEGER)')

    conn.commit()
    cursor.close()
    conn.close()

    # 查询所有的任务
    conn = sqlite3.connect('task.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()

    # 添加任务到APScheduler中
    for task in tasks:
        # 判断任务类型（固定时间间隔或cron表达式）
        if task[4]:
            # 固定时间间隔任务
            seconds = int(task[4])
            scheduler.add_job(send_request,
                              'interval',
                              seconds=seconds,
                              args=(task[1], task[2], task[3]))
        elif task[5]:
            # cron任务
            # 解析cron表达式
            cron = croniter(task[5], datetime.datetime.now())
            scheduler.add_job(send_request,
                              'cron',
                              id=str(task[0]),
                              args=(task[1], task[2], task[3]),
                              next_run_time=cron.get_next(datetime.datetime))

    scheduler.start()


def send_request(url, method, params):
    try:
        if method == 'GET':
            r = requests.get(url, params=params)
        elif method == 'POST':
            # 判断参数类型（JSON或x-www-form-urlencoded）
            if params.startswith('{'):
                r = requests.post(url, json=json.loads(params))
            else:
                r = requests.post(url, data=params)

        # 处理请求结果
        if r.status_code == 200:
            print('Request success: %s' % url)
        else:
            print('Request error: %s' % url)

    except Exception as e:
        print('Request error: %s, %s' % (url, str(e)))


@app.route('/')
def index():
    # 判断用户是否已经登录
    if 'token' in request.cookies:
        return render_template('tasks.html')
    else:
        return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # 校验用户名和密码
    if username == 'admin' and password == 'admin':
        # 生成token并返回给客户端
        expires = datetime.timedelta(days=7)
        access_token = create_access_token(identity=username,
                                           expires_delta=expires)
        response = jsonify({'access_token': access_token})
        response.set_cookie('token', access_token, httponly=True, secure=True)
        return response
    else:
        return jsonify({'msg': 'Invalid username or password'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    response = jsonify({'msg': 'Logout successful'})
    response.delete_cookie('token')
    return response


@app.route('/api/add', methods=['POST'])
@jwt_required()
def add_task():
    # 解析请求参数
    url = request.json.get('url', None)
    method = request.json.get('method', None)
    params = request.json.get('params', None)
    interval = request.json.get('interval', None)
    cron = request.json.get('cron', None)

    # 插入任务到数据库
    conn = sqlite3.connect('task.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (url, method, params, interval, cron, status) '
        'VALUES (?, ?, ?, ?, ?, ?)', (url, method, params, interval, cron, 1))
    task_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    # 根据任务的类型和要求添加到APScheduler中
    if interval:
        seconds = int(interval)
        scheduler.add_job(send_request,
                          'interval',
                          seconds=seconds,
                          args=(url, method, params))
    elif cron:
        scheduler.add_job(send_request,
                          'cron',
                          id=str(task_id),
                          args=(url, method, params),
                          minute=cron)

    return jsonify({'msg': 'Task added successfully'}), 201


@app.route('/api/remove', methods=['POST'])
@jwt_required()
def remove_task():
    task_id = request.json.get('id', None)

    # 从数据库中删除任务
    conn = sqlite3.connect('task.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id=?', (task_id, ))
    conn.commit()
    cursor.close()
    conn.close()

    # 从APScheduler中删除任务
    scheduler.remove_job(str(task_id))

    return jsonify({'msg': 'Task removed successfully'})


@app.route('/api/list', methods=['GET'])
@jwt_required()
def list_tasks():
    # 查询所有的任务
    conn = sqlite3.connect('task.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()

    # 构造返回结果
    result = []
    for task in tasks:
        result.append({
            'id': task[0],
            'url': task[1],
            'method': task[2],
            'params': task[3],
            'interval': task[4],
            'cron': task[5],
            'last_run_time': task[6],
            'next_run_time': task[7],
            'status': task[8]
        })

    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8848, debug=True)
