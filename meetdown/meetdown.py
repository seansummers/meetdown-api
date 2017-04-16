# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'meetdown.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('MEETDOWN_SETTINGS', silent=True)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    cur = db.execute("""select
            users.user_id,
            username,
            email,
            GROUP_CONCAT(DISTINCT events.title) as events,
            GROUP_CONCAT(groups.name) as groups
            from users
            LEFT OUTER JOIN memberships on users.user_id = memberships.user_id
            LEFT OUTER JOIN groups on memberships.group_id = groups.group_id
            LEFT OUTER JOIN signups on signups.user_id = users.user_id
            LEFT OUTER JOIN events on events.event_id = signups.event_id
            GROUP BY users.user_id, username, email
            """);
    users = [dict(u) for u in (cur.fetchall())]
    response = [{
        'user_id': u['user_id'],
        'username': u['username'],
        'email': u['email'],
        'events': list(set(u['events'].split(','))) if u['events'] else [],
        'groups': list(set(u['groups'].split(','))) if u['groups'] else []
        } for u in users]
    return jsonify(response)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    cur = db.execute('select user_id, username, email from users where user_id = ?', [user_id]);
    user = cur.fetchone()
    return jsonify(dict(user))


@app.route('/groups', methods=['GET'])
def get_groups():
    db = get_db()
    cur = db.execute('select group_id, name from groups order by group_id desc');
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])


@app.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    db = get_db()
    cur = db.execute('select group_id, name from groups where group_id = ?', [group_id]);
    row = cur.fetchone()
    return jsonify(dict(row))

