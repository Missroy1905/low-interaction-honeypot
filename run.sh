#!/usr/bin/env bash
cd "$(dirname "$0")"
if [ ! -d venv ]; then
    python3 -m venv venv || { echo 'Install first: sudo apt install python3-venv -y'; exit 1; }
fi
source venv/bin/activate
pip install -q -r requirements.txt
python ssh_honeypot.py  > ssh.log 2>&1 &
python http_honeypot.py > http.log 2>&1 &
python dashboard.py     > dashboard.log 2>&1 &
trap 'echo; echo Stopping...; kill $(jobs -p) 2>/dev/null' INT TERM EXIT
sleep 3
echo '=========================================='
echo ' Honeypot is running'
echo '   Fake SSH   : port 2222'
echo '   Fake HTTP  : http://127.0.0.1:8080'
echo '   Dashboard  : http://127.0.0.1:5000'
echo ' Open a NEW terminal and run:'
echo '   venv/bin/python check_project.py'
echo ' Press Ctrl+C here to stop.'
echo '=========================================='
wait
