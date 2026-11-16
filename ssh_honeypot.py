import os
import socket
import threading
import paramiko
from db import init_db, log_event

PORT = 2222
BANNER = 'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6'
KEY_FILE = 'host_rsa.key'
WEAK_PASSWORDS = {'123456', 'password', 'admin', 'root', 'toor'}
FAKE_OUTPUT = {
    'whoami': 'root',
    'id': 'uid=0(root) gid=0(root) groups=0(root)',
    'pwd': '/root',
    'ls': 'backup.tar.gz  notes.txt  scripts',
    'uname -a': 'Linux server01 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux',
}

if os.path.exists(KEY_FILE):
    HOST_KEY = paramiko.RSAKey(filename=KEY_FILE)
else:
    HOST_KEY = paramiko.RSAKey.generate(2048)
    HOST_KEY.write_private_key_file(KEY_FILE)

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.shell_requested = threading.Event()
    def get_allowed_auths(self, username):
        return 'password'
    def check_auth_password(self, username, password):
        log_event('ssh', self.client_ip, 'login_attempt', username, password)
        if password in WEAK_PASSWORDS:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    def check_channel_shell_request(self, channel):
        self.shell_requested.set()
        return True

def fake_shell(chan, ip, user):
    prompt = f'{user}@server01:~# '
    chan.send('Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)\r\n\r\n')
    chan.send(prompt)
    buf = ''
    while True:
        data = chan.recv(1024)
        if not data:
            break
        for ch in data.decode(errors='ignore'):
            if ch in '\r\n':
                chan.send('\r\n')
                cmd = buf.strip()
                buf = ''
                if cmd:
                    log_event('ssh', ip, 'command', username=user, command=cmd[:500])
                    if cmd in ('exit', 'logout'):
                        chan.close()
                        return
                    out = FAKE_OUTPUT.get(cmd, f'bash: {cmd.split()[0]}: command not found')
                    chan.send(out + '\r\n')
                chan.send(prompt)
            elif ch == '\x7f':
                if buf:
                    buf = buf[:-1]
                    chan.send('\b \b')
            elif ch.isprintable():
                buf += ch
                chan.send(ch)

def handle_client(client, addr):
    ip = addr[0]
    log_event('ssh', ip, 'connection', extra=f'port={addr[1]}')
    transport = paramiko.Transport(client)
    transport.local_version = BANNER
    transport.add_server_key(HOST_KEY)
    server = FakeSSHServer(ip)
    try:
        transport.start_server(server=server)
        chan = transport.accept(30)
        if chan is None:
            return
        server.shell_requested.wait(10)
        fake_shell(chan, ip, transport.get_username() or 'root')
    except Exception as exc:
        log_event('ssh', ip, 'error', extra=str(exc)[:200])
    finally:
        transport.close()

def main():
    init_db()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', PORT))
    sock.listen(100)
    print(f'Fake SSH honeypot listening on port {PORT}')
    while True:
        client, addr = sock.accept()
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()

if __name__ == '__main__':
    main()
