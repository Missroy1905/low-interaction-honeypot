import json, socket, sqlite3, subprocess, sys, time, urllib.request
from db import DB_PATH, init_db

results = []
def check(name, ok, detail=''):
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")

def port_open(port):
    with socket.socket() as s:
        s.settimeout(2)
        return s.connect_ex(('127.0.0.1', port)) == 0

def counts():
    conn = sqlite3.connect(DB_PATH)
    def q(sql):
        return conn.execute(sql).fetchone()[0]
    out = {
        'ssh_logins': q("SELECT COUNT(*) FROM events WHERE service='ssh' AND event_type='login_attempt'"),
        'ssh_commands': q("SELECT COUNT(*) FROM events WHERE service='ssh' AND event_type='command'"),
        'http_requests': q("SELECT COUNT(*) FROM events WHERE service='http' AND event_type='request'"),
        'http_logins': q("SELECT COUNT(*) AS n FROM events WHERE service='http' AND event_type='login_attempt'"),
    }
    conn.close()
    return out

print('1. Are the services running?')
check('Fake SSH honeypot  (port 2222)', port_open(2222))
check('Fake HTTP honeypot (port 8080)', port_open(8080))
check('Dashboard          (port 5000)', port_open(5000))
if not all(results):
    print('\nStart the project first with ./run.sh in another terminal.')
    sys.exit(1)

print('\n2. Simulating an attack ...')
init_db()
before = counts()
subprocess.run([sys.executable, 'demo_attack.py'], check=False)
time.sleep(1)
after = counts()

print('\n3. Did the honeypot record everything in the database?')
needs = {'ssh_logins': 5, 'ssh_commands': 4, 'http_requests': 3, 'http_logins': 2}
for key, minimum in needs.items():
    gained = after[key] - before[key]
    check(f'{key}: +{gained} new (expected at least {minimum})', gained >= minimum)

print('\n4. Does the dashboard show the data?')
try:
    with urllib.request.urlopen('http://127.0.0.1:5000/api/stats', timeout=5) as r:
        stats = json.load(r)
    check('Dashboard API returns data', stats['total'] > 0, f"(total events: {stats['total']})")
    check('Top passwords chart has data', len(stats['passwords']) > 0)
    check('Top attacker IPs chart has data', len(stats['ips']) > 0)
    check('Recent commands table has data', len(stats['recent_commands']) > 0)
except Exception as exc:
    check('Dashboard API reachable', False, str(exc))

print()
if all(results):
    print('RESULT: ALL CHECKS PASSED. Now open http://127.0.0.1:5000 to see the charts.')
else:
    print('RESULT: SOME CHECKS FAILED. See the log files (ssh.log, http.log, dashboard.log).')
    sys.exit(1)
