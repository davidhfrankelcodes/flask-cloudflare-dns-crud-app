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

    valid_record_types = ['A', 'CNAME', 'TXT', 'MX', 'AAAA', 'SRV', 'NS']
    domain = app.config['DOMAIN']

    # Grab URL parameters (GET)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    record_type = request.args.get('record_type', '', type=str)

    records = []
    total_records = 0
    error_message = None

    try:
        zone_id = get_zone_id(domain)
        if not zone_id:
            raise ValueError("Could not fetch zone ID. Check your domain or API token.")

        if request.method == 'POST':
            action = request.form.get('action')
            record_id = request.form.get('record_id')

            if action == 'create':
                create_dns_record(zone_id, request.form)
                flash("DNS record created successfully!", 'success')
            elif action == 'update':
                update_dns_record(zone_id, record_id, request.form)
                flash("DNS record updated successfully!", 'success')
            elif action == 'delete':
                delete_dns_record(zone_id, record_id)
                flash("DNS record deleted successfully!", 'success')

            # **Redirect here after handling POST** to avoid double-post on page refresh
            return redirect(url_for('dns_records',
                                    page=page,
                                    per_page=per_page,
                                    search=search,
                                    record_type=record_type))

        # For GET requests, list records as usual
        records, total_records = list_dns_records(zone_id, search, record_type)

    except Exception as e:
        error_message = f"Unable to load DNS records: {str(e)}"
        flash(error_message, 'danger')

    total_pages = (total_records + per_page - 1) // per_page
    paginated_records = records[(page - 1) * per_page : page * per_page]

    return render_template(
        'dns_records.html',
        records=paginated_records,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        search=search,
        record_type=record_type,
        valid_record_types=valid_record_types
    )


def get_zone_id(domain):
    url = f'{ZONES_ENDPOINT}?name={domain}'
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['success'] and data['result']:
        return data['result'][0]['id']
    return None

def list_dns_records(zone_id, search, record_type):
    # Retrieve up to 1000 records
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records?per_page=1000'
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data['success']:
        return [], 0
    records = data['result']
    if record_type:
        records = [r for r in records if r['type'] == record_type]
    if search:
        records = [r for r in records if (search.lower() in r['name'].lower()
                                          or search.lower() in r['content'].lower())]
    total_records = len(records)
    return records, total_records

def create_dns_record(zone_id, form):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records'
    payload = {
        'type': form['type'],
        'name': form['name'],
        'content': form['content'],
        'ttl': int(form['ttl']),
        'proxied': form.get('proxied') == 'true'
    }
    requests.post(url, headers=headers, json=payload)

def update_dns_record(zone_id, record_id, form):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records/{record_id}'
    payload = {
        'type': form['type'],
        'name': form['name'],
        'content': form['content'],
        'ttl': int(form['ttl']),
        'proxied': form.get('proxied') == 'true'
    }
    requests.put(url, headers=headers, json=payload)

def delete_dns_record(zone_id, record_id):
    url = f'{ZONES_ENDPOINT}/{zone_id}/dns_records/{record_id}'
    requests.delete(url, headers=headers)

if __name__ == '__main__':
    app.run(
        debug=True if 'true' in os.getenv("FLASK_DEBUG", "").lower() else False,
        host=os.getenv("FLASK_HOST", "localhost"),
        port=os.getenv("FLASK_PORT", 5000)
    )
