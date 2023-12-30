from flask import Flask, request
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app) 


@app.route('/')
def home():
    return 'Home', 200

def _drop_table(cursor, table_name):
    cr = cursor
    cr.execute(f'''
        SELECT max(id) FROM {table_name}
        ORDER BY id ASC;
    ''')

def get_sequence_id(cursor, table_name):
    cr = cursor
    cr.execute(f'''
        SELECT max(id) FROM {table_name}
        ORDER BY id ASC;
    ''')
    last_id = cr.fetchall()[0]
    id = last_id[0]+1 if last_id[0] else 0 + 1
    return id

def check_exist(cursor, table_name, field, value):
    cr = cursor
    cr.execute(f'''
        SELECT {field} FROM {table_name}
        WHERE {field} = '{value}';
    ''')
    exists = cr.fetchall()
    if len(exists):
        return True
    return False


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
    id = get_sequence_id(cr, table_name="user")
    check_name = check_exist(cr, "user", "name", data['name'])
    check_email = check_exist(cr, "user", "email", data['email'])
    
    print("res", check_name, check_email)
    
    if check_email or check_name:
        return {'status': False, 'message': "Email or Username already exist."}
    
    cr.execute('''
        INSERT INTO user VALUES (?, ?, ?, ?, ?)
    ''', (id, data['name'], data['email'], data['password'], data.get('is_admin') or False))
    conn.commit()
    conn.close()
    
    return {'status': True, 'message': "Registered Successfully."}

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
        return {'status': False, 'message': "User not found."}
    
    

@app.route('/category')
def categories():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM category')
    categs = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'categories': categs}, 200

@app.route('/category/selection')
def categories_selection():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM category')
    categs = [{'value': row[0], 'label': row[1]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'categories': categs}, 200

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
    return {"message":"Created Successfully.", "status": True}


# ---------------------- EDIT Category
@app.route('/category/write', methods=['POST'])
def write_categories():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_write = data.get('id')

    if not to_write:
        return {"message":"Cannot Edit.", "status": False}
    cr.execute('''
        UPDATE category
            SET name = ?, detail = ?, image_url = ?
            WHERE id = ?;
    ''', (data['name'], data['detail'], data['image_url'], to_write))
    conn.commit()
    conn.close()
    return {"message":"Edit Successfully.", "status": True}

# ---------------------- DELETE Category
@app.route('/category/unlink', methods=['POST'])
def delete_categories():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_delete = data.get('id')

    if not to_delete:
        return {"message":"Cannot Delete.", "status": False}
    cr.execute('''
        DELETE FROM category WHERE id = ?;

    ''', (to_delete))
    conn.commit()
    conn.close()
    return {"message":"Deleted Successfully.", "status": True}


@app.route('/province')
def provinces():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM province')
    provinces = [{'id': row[0], 'name': row[1]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'provinces': provinces}, 200

@app.route('/province/create', methods=['POST'])
def create_provinces():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    id = get_sequence_id(cr, table_name="province")
    cr.execute('''
        INSERT INTO province VALUES (?, ?)
    ''', (id, data['name']))
    conn.commit()
    conn.close()
    return {"message":"Created Successfully.", "status": True}

@app.route('/province/write', methods=['POST'])
def write_provinces():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_write = data.get('id')

    if not to_write:
        return {"message":"Cannot Edit.", "status": False}
    cr.execute('''
        UPDATE province
            SET name = ?
            WHERE id = ?;
    ''', (data['name'], to_write))
    conn.commit()
    conn.close()
    return {"message":"Edit Successfully.", "status": True}

@app.route('/province/unlink', methods=['POST'])
def delete_provinces():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_delete = data.get('id')

    if not to_delete:
        return {"message":"Cannot Delete.", "status": False}
    cr.execute('''
        DELETE FROM province WHERE id = ?;

    ''', (to_delete))
    conn.commit()
    conn.close()
    return {"message":"Deleted Successfully.", "status": True}

@app.route('/province/selection')
def provinces_selection():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM province')
    provinces = [{'value': row[0], 'label': row[1]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'provinces': provinces}, 200

@app.route('/province/data')
def get_province_data():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()

    data = []
    cr.execute('SELECT * FROM province')
    provinces = [{'id': row[0], 'name': row[1]} for row in cr.fetchall()]
    for prov in provinces:
        
        cr.execute('SELECT * FROM place WHERE province_id = ' + str(prov['id']))
        places = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5], 'province_id': row[6]} for row in cr.fetchall()]
        
        cr.execute('SELECT * FROM accomodation WHERE province_id = ' + str(prov['id']))
        accomodations = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5], 'province_id': row[6]} for row in cr.fetchall()]
        
        cr.execute('SELECT * FROM transportation')
        transportations = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5]} for row in cr.fetchall()]
        
        data.append({
            'province': prov,
            'place': places,
            'accomodation': accomodations,
            'transportation': transportations
        })
    conn.commit()
    conn.close()
    return {'data': data}, 200

@app.route('/province/data/filtered', methods=['POST'])
def get_province_filtered_data():
    datas = []
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    
    filters = data.get('filter')
    filter_category = filters['categories'][0] if filters['categories'] else None
    filter_location = filters['locations'][0] if filters['locations'] else None
    filter_min = filters.get('minBudget')
    filter_max = filters.get('maxBudget')

    if not filter_location:
        cr.execute('SELECT * FROM province')
        provinces = [{'id': row[0], 'name': row[1]} for row in cr.fetchall()]
    else:
        cr.execute('SELECT * FROM province WHERE id=' + str(filter_location))
        provinces = [{'id': row[0], 'name': row[1]} for row in cr.fetchall()]
    
    cr.execute('SELECT SUM(price) FROM place')
    place_domain = cr.fetchall()[0][0]
    cr.execute('SELECT SUM(price) FROM accomodation')
    acco_domain = cr.fetchall()[0][0]
    cr.execute('SELECT SUM(price) FROM transportation')
    transp_domain = cr.fetchall()[0][0]
    total = place_domain + acco_domain + transp_domain
    rate_place = place_domain / total
    rate_acco = acco_domain / total + 1
    rate_transp = transp_domain / total + 1
            
    for prov in provinces:
        
        place_filter = filter_max * rate_place
        acco_filter = filter_max * rate_acco
        transp_filter = filter_max * rate_transp
        
        
        cr.execute('SELECT * FROM place WHERE province_id = ' + str(prov['id']) + ' AND price < ' + str(place_filter))
        places = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5], 'province_id': row[6]} for row in cr.fetchall()]
        
        cr.execute('SELECT * FROM accomodation WHERE province_id = ' + str(prov['id']) + ' AND price < ' + str(acco_filter))
        accomodations = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5], 'province_id': row[6]} for row in cr.fetchall()]
        
        cr.execute('SELECT * FROM transportation' + ' WHERE price < ' + str(transp_filter))
        transportations = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5]} for row in cr.fetchall()]
        
        datas.append({
            'province': prov,
            'place': places,
            'accomodation': accomodations,
            'transportation': transportations
        })
    conn.commit()
    conn.close()
    return {'data': datas, 'status': True}, 200



@app.route('/place')
def places():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM place')
    places = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5], 'province_id': row[5]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'places': places}, 200

@app.route('/place/create', methods=['POST'])
def create_places():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    id = get_sequence_id(cr, table_name="place")
    cr.execute('''
        INSERT INTO place VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (id, data['name'], data['detail'], data['image'], data['image_url'], data['price'], data['province_id']))
    conn.commit()
    conn.close()
    return {"message":"Created Successfully.", "status": True}

@app.route('/place/write', methods=['POST'])
def write_places():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_write = data.get('id')

    if not to_write:
        return {"message":"Cannot Edit.", "status": False}
    cr.execute('''
        UPDATE place
            SET name = ?, detail = ?, image_url = ?, price = ?, province_id = ?
            WHERE id = ?;
    ''', (data['name'], data['detail'], data['image_url'], data['price'], data['province_id'], to_write))
    conn.commit()
    conn.close()
    return {"message":"Edit Successfully.", "status": True}

@app.route('/place/unlink', methods=['POST'])
def delete_places():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_delete = data.get('id')

    if not to_delete:
        return {"message":"Cannot Delete.", "status": False}
    cr.execute('''
        DELETE FROM place WHERE id = ?;

    ''', (to_delete))
    conn.commit()
    conn.close()
    return {"message":"Deleted Successfully.", "status": True}


@app.route('/accomodation')
def accomodations():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM accomodation')
    accomodations = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5], 'province_id': row[5]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'accomodations': accomodations}, 200

@app.route('/accomodation/create', methods=['POST'])
def create_accomodation():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    id = get_sequence_id(cr, table_name="accomodation")
    cr.execute('''
        INSERT INTO accomodation VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (id, data['name'], data['detail'], data['image'], data['image_url'], data['price'], data['province_id']))
    conn.commit()
    conn.close()
    return {"message":"Created Successfully.", "status": True}

@app.route('/accomodation/write', methods=['POST'])
def write_accomodation():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_write = data.get('id')

    if not to_write:
        return {"message":"Cannot Edit.", "status": False}
    cr.execute('''
        UPDATE accomodation
            SET name = ?, detail = ?, image_url = ?, price = ?, province_id = ?
            WHERE id = ?;
    ''', (data['name'], data['detail'], data['image_url'], data['price'], data['province_id'], to_write))
    conn.commit()
    conn.close()
    return {"message":"Edit Successfully.", "status": True}

@app.route('/accomodation/unlink', methods=['POST'])
def delete_accomodations():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_delete = data.get('id')

    if not to_delete:
        return {"message":"Cannot Delete.", "status": False}
    cr.execute('''
        DELETE FROM accomodation WHERE id = ?;

    ''', (to_delete))
    conn.commit()
    conn.close()
    return {"message":"Deleted Successfully.", "status": True}

@app.route('/transportation')
def transportations():
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    cr.execute('SELECT * FROM transportation')
    transportations = [{'id': row[0], 'name': row[1], 'detail': row[2], 'image': row[3], 'image_url': row[4], 'price': row[5]} for row in cr.fetchall()]
    conn.commit()
    conn.close()
    return {'transportations': transportations}, 200

@app.route('/transportation/create', methods=['POST'])
def create_transportation():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    id = get_sequence_id(cr, table_name="transportation")
    cr.execute('''
        INSERT INTO transportation VALUES (?, ?, ?, ?, ?, ?)
    ''', (id, data['name'], data['detail'], data['image'], data['image_url'], data['price']))
    conn.commit()
    conn.close()
    return {"message":"Created Successfully.", "status": True}

@app.route('/transportation/write', methods=['POST'])
def transportation_places():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_write = data.get('id')

    if not to_write:
        return {"message":"Cannot Edit.", "status": False}
    cr.execute('''
        UPDATE place
            SET name = ?, detail = ?, image_url = ?, price = ?
            WHERE id = ?;
    ''', (data['name'], data['detail'], data['image_url'], data['price'], to_write))
    conn.commit()
    conn.close()
    return {"message":"Edit Successfully.", "status": True}

@app.route('/transportation/unlink', methods=['POST'])
def delete_transportations():
    data = request.get_json()
    conn = sqlite3.connect('data.db')
    cr = conn.cursor()
    to_delete = data.get('id')

    if not to_delete:
        return {"message":"Cannot Delete.", "status": False}
    cr.execute('''
        DELETE FROM transportation WHERE id = ?;

    ''', (to_delete))
    conn.commit()
    conn.close()
    return {"message":"Deleted Successfully.", "status": True}


if __name__ == '__main__':
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    
    # for table in ['place']:
    #     _drop_table(cur, table)
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            is_admin BOOLEAN
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            detail TEXT,
            image TEXT,
            image_url TEXT
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS province (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS place (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            detail TEXT,
            image TEXT,
            image_url TEXT,
            price FLOAT,
            province_id INT
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accomodation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            detail TEXT,
            image TEXT,
            image_url TEXT,
            price FLOAT,
            province_id INT
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transportation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            detail TEXT,
            image TEXT,
            image_url TEXT,
            price FLOAT
        )''')
    conn.commit()
    conn.close()
    app.run(debug=True)
