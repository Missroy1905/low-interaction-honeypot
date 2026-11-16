Low-Interaction Honeypot with Attack Dashboard

A Python-based low-interaction honeypot built for the Cyber Security Lab (7CIT4-22) mini project. It simulates SSH (port 2222) and HTTP (port 8080) decoy services, safely logs attacker credentials and commands into SQLite without executing them, and visualises live attack metrics on a Flask + Chart.js web dashboard (port 5000).

Key Features

Fake SSH Server (ssh_honeypot.py): Emulates an Ubuntu OpenSSH server on port 2222 using Paramiko, logs all login attempts, and provides a sandboxed fake shell with fixed replies.

Fake HTTP Login Portal (http_honeypot.py): Captures web probes and submitted credentials on port 8080 via a decoy Router Admin page.

SQLite Event Logger (db.py): Thread-safe, parameterised logging of source IPs, timestamps, usernames, passwords, and commands.

Live Attack Dashboard (dashboard.py & templates/index.html): Auto-refreshing (5s) analytics dashboard on port 5000 showing real-time counters, charts, and recent commands.

Snort IDS Integration: Custom TCP SYN rules (sid:1000002, sid:1000003) for network-level connection alerts.

How to Run & Verify (For Examiner / Demo)

1. Start All Honeypot Services

chmod +x run.sh
./run.sh


This launches the SSH honeypot (2222), HTTP honeypot (8080), and Web Dashboard (5000).

2. Run Automated Attack Simulation & Self-Check

Open a second terminal tab and run:

venv/bin/python check_project.py


This script verifies that all three ports are active, simulates SSH brute-force and HTTP login attacks via demo_attack.py, and confirms database & dashboard logging (RESULT: ALL CHECKS PASSED).

3. View the Live Dashboard & Decoys

Attack Dashboard: Open http://127.0.0.1:5000 in your browser.

Fake HTTP Login: Open http://127.0.0.1:8080/admin and submit test credentials.

Fake SSH Shell: Connect via ssh root@127.0.0.1 -p 2222 (weak password: 123456) and test commands like whoami, ls, or uname -a.

4. (Optional) Run Snort Network Alerts

sudo snort -A console -q -c /etc/snort/snort.conf -i lo


Project Structure

db.py — SQLite schema and thread-safe event logger

ssh_honeypot.py — Paramiko SSH decoy server

http_honeypot.py — Flask HTTP decoy login portal

dashboard.py — Flask REST API (/api/stats) & dashboard server

templates/index.html — Live Chart.js frontend

demo_attack.py — Automated attack simulator

check_project.py — End-to-end verification suite

run.sh — One-command environment setup and launcher

Disclaimer: Built strictly for educational and laboratory demonstration inside an isolated environment.
