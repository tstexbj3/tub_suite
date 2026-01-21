#!/bin/bash
# Clear database locks from stuck transactions

echo "Clearing database locks..."

cd /home/user/frappe-bench

# Kill all bench processes first
pkill -9 -f "bench start" 2>/dev/null
pkill -9 -f "frappe" 2>/dev/null
pkill -9 -f "gunicorn" 2>/dev/null
pkill -9 -f "node socketio" 2>/dev/null
pkill -9 -f "redis" 2>/dev/null

sleep 2

# Connect to MariaDB and kill locks
./env/bin/python3 << 'PYTHON_EOF'
import os
os.chdir('/home/user/frappe-bench')

import frappe
frappe.init(site='tub')
frappe.connect()

# Kill all sleeping connections
print("Killing sleeping connections...")
processes = frappe.db.sql("""
    SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE
    FROM information_schema.PROCESSLIST
    WHERE DB = '_8d57297098fac5bd'
    AND COMMAND = 'Sleep'
    AND TIME > 10
""", as_dict=True)

for proc in processes:
    try:
        print(f"Killing process {proc.ID}: {proc.USER}@{proc.HOST} - {proc.STATE}")
        frappe.db.sql(f"KILL {proc.ID}")
    except Exception as e:
        print(f"Failed to kill {proc.ID}: {e}")

frappe.db.commit()
print("✓ Database locks cleared")
PYTHON_EOF

echo "✓ Done - restart bench now"
