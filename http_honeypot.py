from flask import Flask, request, render_template_string
from db import init_db, log_event

app = Flask(__name__)
PAGE = '''<!DOCTYPE html><html><head><title>Router Admin Panel</title><style>body{font-family:Arial,sans-serif;background:#eef;display:flex;justify-content:center;margin-top:80px}.box{background:#fff;padding:30px;border-radius:6px;box-shadow:0 0 8px #aaa;width:300px}input{width:100%;margin:6px 0;padding:8px;box-sizing:border-box}.err{color:#c00}</style></head><body><div class='box'><h2>Router Admin</h2>{% if error %}<p class='err'>{{ error }}</p>{% endif %}<form method='post'><input name='username' placeholder='Username'><input name='password' type='password' placeholder='Password'><button type='submit'>Log in</button></form></div></body></html>'''

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')[:200]
    error = None
    if request.method == 'POST':
        log_event('http', ip, 'login_attempt',
                  username=request.form.get('username', '')[:100],
                  password=request.form.get('password', '')[:100],
                  extra=f'path=/{path} ua={ua}')
        error = 'Invalid username or password'
    else:
        log_event('http', ip, 'request', extra=f'path=/{path} ua={ua}')
    return render_template_string(PAGE, error=error)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
