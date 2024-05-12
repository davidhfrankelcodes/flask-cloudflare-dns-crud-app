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

ZONES_ENDPOINT = 'https://api.cloudflare.com/client/v4/zones'

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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if request.method == 'POST':
        action = request.form.get('action')
        record_id = request.form.get('record_id')
        if action == 'create':
            create_dns_record(zone_id, request.form)
        elif action == 'update':
            update_dns_record(zone_id, record_id, request.form)
        elif action == 'delete':
            delete_dns_record(zone_id, record_id)

    records, total_records = list_dns_records(zone_id, page, per_page)
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    return render_template('dns_records.html', 
                           records=records, 
                           page=page, 
                           per_page=per_page, 
                           total_pages=total_pages)

def get_zone_id(domain):
    url = f'{ZONES_ENDPOINT}?name={domain}'
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['success']:
        return data['result'][0]['id']
    return None

def list_dns_records(zone_id, page, per_page):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records?page={page}&per_page={per_page}'
    response = requests.get(url, headers=headers)
    data = response.json()
    total_records = data['result_info']['total_count'] if data['success'] else 0
    return data['result'], total_records if data['success'] else []

def create_dns_record(zone_id, form):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records'
    payload = {
        'type': form['type'],
        'name': form['name'],
        'content': form['content'],
        'ttl': int(form['ttl']),
        'proxied': form.get('proxied') == 'on'
    }
    requests.post(url, headers=headers, json=payload)

def update_dns_record(zone_id, record_id, form):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records/{record_id}'
    payload = {
        'type': form['type'],
        'name': form['name'],
        'content': form['content'],
        'ttl': int(form['ttl']),
        'proxied': form.get('proxied') == 'on'
    }
    requests.put(url, headers=headers, json=payload)

def delete_dns_record(zone_id, record_id):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records/{record_id}'
    requests.delete(url, headers=headers)

if __name__ == '__main__':
    app.run(
        debug=True if 'true' in os.getenv(
            "FLASK_DEBUG", "").lower() else False,
        host=os.getenv("FLASK_HOST", "localhost"),
        port=os.getenv("FLASK_PORT", 5000)
        )
