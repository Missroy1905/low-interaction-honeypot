import sys
import time
import urllib.parse
import urllib.request
import paramiko

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'

def ssh_attempt(user, password, commands=()):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, port=2222, username=user, password=password,
                       timeout=5, allow_agent=False, look_for_keys=False)
    except paramiko.AuthenticationException:
        print(f'  ssh {user}/{password}: rejected')
        return
    except Exception as exc:
        print(f'  ssh {user}/{password}: error ({exc})')
        return
    print(f'  ssh {user}/{password}: accepted, typing commands')
    chan = client.invoke_shell()
    time.sleep(0.5)
    chan.recv(4096)
    for cmd in commands:
        chan.send(cmd + '\n')
        time.sleep(0.4)
        if chan.recv_ready():
            chan.recv(4096)
    time.sleep(0.5)
    chan.close()
    client.close()

def http_get(path):
    urllib.request.urlopen(f'http://{HOST}:8080{path}', timeout=5).read()
    print(f'  http GET {path}')

def http_post(user, password):
    data = urllib.parse.urlencode({'username': user, 'password': password}).encode()
    urllib.request.urlopen(f'http://{HOST}:8080/', data=data, timeout=5).read()
    print(f'  http POST login {user}/{password}')

if __name__ == '__main__':
    print(f'Simulating attacker against {HOST} ...')
    print('SSH brute force:')
    ssh_attempt('root', 'letmein')
    ssh_attempt('root', 'qwerty')
    ssh_attempt('admin', 'admin123')
    ssh_attempt('root', '123456', ['whoami', 'ls', 'uname -a', 'cat /etc/passwd'])
    ssh_attempt('admin', 'password', ['id', 'pwd'])
    print('Web probing:')
    for p in ('/admin', '/wp-login.php', '/phpmyadmin'):
        http_get(p)
    http_post('admin', 'admin123')
    http_post('root', 'toor')
    print('Done. Refresh the dashboard at http://127.0.0.1:5000')
