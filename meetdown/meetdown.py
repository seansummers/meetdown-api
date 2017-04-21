# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, jsonify
from flask_graphql import GraphQLView
import graphene

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
            users.id as user_id,
            username,
            email,
            GROUP_CONCAT(DISTINCT events.title) as events,
            GROUP_CONCAT(groups.name) as groups
            from users
            LEFT OUTER JOIN memberships on memberships.user_id = users.id
            LEFT OUTER JOIN groups on groups.id = memberships.group_id
            LEFT OUTER JOIN signups on signups.user_id = users.id
            LEFT OUTER JOIN events on events.id = signups.event_id
            GROUP BY users.id, username, email
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
    cur = db.execute('select id, username, email from users where id = ?', [user_id]);
    user = cur.fetchone()
    return jsonify(dict(user))


@app.route('/groups', methods=['GET'])
def get_groups():
    db = get_db()
    cur = db.execute('select id, name from groups order by id desc');
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])


@app.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    db = get_db()
    cur = db.execute('select id, name from groups where id = ?', [group_id]);
    row = cur.fetchone()
    return jsonify(dict(row))


#class Query(graphene.ObjectType):
    #hello = graphene.String()

    #def resolve_hello(self, args, context, info):
        #return 'World'

class Group(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class Event(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    location = graphene.String()


class User(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    events = graphene.List(Event, args=dict(id=graphene.ID(), event_id=graphene.ID()))
    groups = graphene.List(Group)

    def resolve_events(self, args, context, info):
        db = get_db()
        cur = db.execute("""
            SELECT title, location
            FROM events
            INNER JOIN signups
            WHERE events.id = signups.event_id
            AND signups.user_id = ? """, [self.id])
        events = [dict(event) for event in (cur.fetchall())]
        return [Event(**event) for event in events]

    def resolve_groups(self, args, context, info):
        db = get_db()
        cur = db.execute("""
            SELECT name
            FROM groups
            INNER JOIN memberships
            WHERE memberships.group_id = groups.id
            AND memberships.user_id = ? """, [self.id])
        groups = [dict(group) for group in (cur.fetchall())]
        return [Group(**group) for group in groups]

class Query(graphene.ObjectType):
    users = graphene.List(User, args=dict(id=graphene.ID()))
    groups = graphene.List(Group, args=dict(id=graphene.ID()))

    def resolve_users(self, args, context, info):
        db = get_db()
        if 'id' not in args:
            cur = db.execute("SELECT id, username, email from users");
            users = [dict(u) for u in (cur.fetchall())]
            return [User(**u) for u in users]

        cur = db.execute("SELECT id, username, email from users where users.id = ?", [args['id']]);
        users = [dict(u) for u in (cur.fetchall())]
        return [User(**u) for u in users]

    def resolve_groups(self, args, context, info):
        db = get_db()
        if 'id' not in args:
            cur = db.execute("SELECT id, name from groups");
            groups = [dict(g) for g in (cur.fetchall())]
            return [Group(**g) for g in groups]

        cur = db.execute("SELECT id, name from groups where groups.id = ?", [args['id']]);
        users = [dict(u) for u in (cur.fetchall())]
        return [Group(**u) for u in users]


schema = graphene.Schema(query=Query)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
