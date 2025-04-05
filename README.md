# 🛠️ Flask Cloudflare DNS CRUD App

Tired of clicking through Cloudflare’s bloated web UI just to tweak a record? This self-hostable Flask app gives you a **minimalist, fast interface** to manage your DNS zones without the bloat.

<p align="center">
  <img src="https://github.com/user-attachments/assets/06d07b4d-9497-45be-b8bd-35a6cf525ad1" alt="UI Screenshot" width="700"/>
</p>

---

## 🏠 Who's this for?

Anyone self-hosting with domains on Cloudflare who wants:
- A **lightweight** and **responsive** UI for managing DNS records.
- An alternative to the memory-hungry Cloudflare dashboard.
- A self-contained app deployable via Docker in seconds.

---

## ✨ Features

- 🔐 Password-protected interface
- ➕ Add DNS records
- ✏️ Edit DNS records
- ❌ Delete DNS records
- 🔍 Search & filter by type and content
- 🧾 Supports A, CNAME, TXT, MX, AAAA, SRV, NS

---

## 🚀 Quick Start (with Docker)

1. Copy `.env.template` to `.env` and fill in your details:
    ```bash
    cp .env.template .env
    ```

2. Generate a [Cloudflare API token](#how-to-generate-a-cloudflare-api-token).

3. Then spin it up:
    ```bash
    docker compose up -d
    ```

4. Visit `http://localhost:5001`, log in with your password from `.env`, and you're in!

---

## 🔐 Security

- App is secured with a password (set via `.env`)
- Uses a **read/edit-only Cloudflare token** (no account-wide privileges)
- Deploy behind your reverse proxy of choice (NGINX, Traefik, etc.) for HTTPS

---

## 🛠️ How to Generate a Cloudflare API Token

1. Go to [Cloudflare's API Tokens page](https://dash.cloudflare.com/profile/api-tokens)
2. Click **Create Token**
3. Use the **Custom Token** template:
   - **Zone:Read**
   - **DNS:Edit**
4. Set the token scope to either **All Zones** or a specific zone
5. Copy and paste it into your `.env` file:
    ```
    CLOUDFLARE_API_TOKEN=your_token_here
    ```

---

## 🧪 Example `.env`

```dotenv
APP_PASSWORD=supersecret
CLOUDFLARE_API_TOKEN=your_cloudflare_token
DOMAIN=yourdomain.com
FLASK_DEBUG=true
HOST_PORT=5001
```

---

## 📦 Tech Stack

- Python + Flask
- Cloudflare API v4
- Docker / Docker Compose

---

## 🧼 Clean & Lightweight

- No database required
- Just one screenshot, because it really is that simple
- Customize via volume-mounted templates and CSS

---
