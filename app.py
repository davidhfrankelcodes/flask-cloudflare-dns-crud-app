from flask import Flask, request, redirect, url_for, render_template, session, flash
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PASSWORD'] = os.getenv('APP_PASSWORD')
app.config['CLOUDFLARE_API_TOKEN'] = os.getenv('CLOUDFLARE_API_TOKEN')
app.config['DOMAIN'] = os.getenv('DOMAIN')

headers = {
    'Authorization': f'Bearer {app.config["CLOUDFLARE_API_TOKEN"]}',
    'Content-Type': 'application/json'
}

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('dns_records'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == app.config['PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('dns_records'))
        else:
            flash('Invalid password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dns_records', methods=['GET', 'POST'])
def dns_records():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    domain = app.config['DOMAIN']
    zone_id = get_zone_id(domain)

    if request.method == 'POST':
        action = request.form.get('action')
        record_id = request.form.get('record_id')
        if action == 'create':
            create_dns_record(zone_id, request.form)
        elif action == 'update':
            update_dns_record(zone_id, record_id, request.form)
        elif action == 'delete':
            delete_dns_record(zone_id, record_id)

    records = list_dns_records(zone_id)
    return render_template('dns_records.html', records=records)

def get_zone_id(domain):
    url = f'https://api.cloudflare.com/client/v4/zones?name={domain}'
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['success']:
        return data['result'][0]['id']
    return None

def list_dns_records(zone_id):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['result'] if data['success'] else []

def create_dns_record(zone_id, form):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    payload = {
        'type': form['type'],
        'name': form['name'],
        'content': form['content'],
        'ttl': int(form['ttl']),
        'proxied': form.get('proxied') == 'on'
    }
    requests.post(url, headers=headers, json=payload)

def update_dns_record(zone_id, record_id, form):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    payload = {
        'type': form['type'],
        'name': form['name'],
        'content': form['content'],
        'ttl': int(form['ttl']),
        'proxied': form.get('proxied') == 'on'
    }
    requests.put(url, headers=headers, json=payload)

def delete_dns_record(zone_id, record_id):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    requests.delete(url, headers=headers)

if __name__ == '__main__':
    app.run(
        debug=True if 'true' in os.getenv(
            "FLASK_DEBUG", "").lower() else False,
        host=os.getenv("FLASK_HOST", "localhost"),
        port=os.getenv("FLASK_PORT", 5000)
        )
