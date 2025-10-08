import sqlite3
import bcrypt
import pyotp
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# --- SQLite setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL,
    email TEXT NOT NULL,
    secret TEXT NOT NULL
)
""")
conn.commit()


@csrf_exempt
def Qr_view(request):
    error = None
    qr_img = None

    if request.method == "POST":
        action = request.POST.get("action")

        # Register
        if action == "register":
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")

            cursor.execute(
                "SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                error = "Username already exists!"
            else:
                hashed_pw = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt())
                secret = pyotp.random_base32()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, email, secret) VALUES (?, ?, ?, ?)",
                    (username, hashed_pw, email, secret),
                )
                conn.commit()
                # Generate QR code for Google Authenticator
                uri = pyotp.TOTP(secret).provisioning_uri(
                    name=email, issuer_name="IT312_OTP_SQLLite"
                )
                img = qrcode.make(uri)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_img = base64.b64encode(buffer.getvalue()).decode()

        # Login
        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            otp_input = request.POST.get("otp")

            cursor.execute(
                "SELECT password_hash, secret FROM users WHERE username = ?", (
                    username,)
            )
            row = cursor.fetchone()
            if not row:
                error = "Invalid username or password"
            else:
                stored_pw, secret = row
                if not bcrypt.checkpw(password.encode("utf-8"), stored_pw):
                    error = "Invalid username or password"
                else:
                    totp = pyotp.TOTP(secret)
                    if totp.verify(otp_input):
                        return redirect("dashboard")
                    else:
                        error = "Invalid OTP"

    return render(request, "pages/SecureAuth.html", {"error": error, "qr_img": qr_img})
