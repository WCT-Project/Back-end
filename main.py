from flask import Flask, request
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app) 


@app.route('/')
def home():
    return 'Home', 200

def get_sequence_id(cursor, table_name):
    cr = cursor
    cr.execute(f'''
        SELECT max(id) FROM {table_name};
    ''')
    last_id = cr.fetchall()[0]
    id = last_id[0]+1 if last_id[0] else 0  + 1
    return id

@app.route('/category')
def categories():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM category')
    categs = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'categories': categs}, 200

@app.route('/category/write/')

@app.route('/category/create', methods=['POST'])
def create_categories():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    id = get_sequence_id(cr, table_name="category")
    cr.execute('''
        INSERT INTO category VALUES (?, ?, ?, ?, ?)
    ''', (id, data['name'], data['detail'], data['image'], data['image_url']))
    conn.commit()
    conn.close()
    return "Created Successfully.", 200

@app.route('/user')
def users():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM user')
    users = [{'id': row[0], 'name': row[1], 'email': row[2], 'password': row[3], 'is_admin': row[4]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'users': users}, 200

@app.route('/user/create', methods=['POST'])
def create_users():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    id = get_sequence_id(cr, table_name="category")
    cr.execute('''
        INSERT INTO user VALUES (?, ?, ?, ?, ?)
    ''', (id, data['name'], data['email'], data['password'], data['is_admin']))
    conn.commit()
    conn.close()
    return "Created Successfully.", 200

@app.route('/user/authenticate', methods=['POST'])
def login_users():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute(f'''
        SELECT * FROM user
        WHERE email = '{data['email']}'
        
    ''')
    queried_data = cr.fetchone()
    users = {'id': queried_data[0], 'name': queried_data[1], 'email': queried_data[2], 'password': queried_data[3], 'is_admin': queried_data[4]}
    conn.commit()
    conn.close()
    if users and data['password'] == users['password']:
        return {'status': True, 'message': "Login was successful", 'user': users}
    else:
        return {'status': False, 'message': "User not found."}, 401



if __name__ == '__main__':
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            detail TEXT,
            image TEXT,
            image_url TEXT
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            is_admin BOOLEAN
        )''')
    conn.commit()
    conn.close()
    app.run(debug=True)