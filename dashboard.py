import sqlite3
from flask import Flask, jsonify, render_template
from db import DB_PATH, init_db

app = Flask(__name__)

def query(sql, args=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return rows

def top(column, limit=10):
    return query(f'SELECT {column} AS label, COUNT(*) AS n FROM events '
                 f'WHERE {column} IS NOT NULL AND {column} != "" '
                 f'GROUP BY {column} ORDER BY n DESC LIMIT {limit}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    over_time = query(
        'SELECT substr(timestamp, 1, 16) AS label, COUNT(*) AS n FROM events '
        'GROUP BY label ORDER BY label DESC LIMIT 30')[::-1]
    return jsonify({
        'total': query('SELECT COUNT(*) AS n FROM events')[0]['n'],
        'logins': query("SELECT COUNT(*) AS n FROM events WHERE event_type='login_attempt'")[0]['n'],
        'unique_ips': query('SELECT COUNT(DISTINCT src_ip) AS n FROM events')[0]['n'],
        'commands': query("SELECT COUNT(*) AS n FROM events WHERE event_type='command'")[0]['n'],
        'by_service': top('service'),
        'usernames': top('username'),
        'passwords': top('password'),
        'ips': top('src_ip'),
        'over_time': over_time,
        'recent_commands': query(
            "SELECT timestamp, src_ip, command FROM events "
            "WHERE event_type='command' ORDER BY id DESC LIMIT 15"),
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
