# accounts/views.py
from dotenv import load_dotenv
import qrcode
import pyotp
import base64
import requests
import string
from io import BytesIO
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from allauth.account.views import LoginView
from allauth.account.views import SignupView
from .forms import CustomLoginForm, CustomSignupForm
from django.http import HttpResponse
from .models import CustomUser
from django.contrib.auth import authenticate, login
from .cipher_text import atbash_cipher, caesar_cipher, vigenere_cipher
from .jokeapi import get_joke_and_encrypt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
import smtplib
import threading
import time
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import sqlite3


def home(request):
    return render(request, "home.html")


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = CustomLoginForm


class CustomSignupView(SignupView):
    template_name = "accounts/signup.html"
    form_class = CustomSignupForm


@login_required
def custom_logout_view(request):
    return render(request, "account/logout.html")


# --- SQLite setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    blocked INTEGER DEFAULT 0
)
""")
conn.commit()


def atbash(text):
    result = ''
    for char in text:
        if char.isalpha():
            if char.isupper():
                result += chr(90 - (ord(char) - 65))
            else:
                result += chr(122 - (ord(char) - 97))
        else:
            result += char
    return result


def caesar_encrypt(text, shift):
    result = ''
    for char in text:
        if char.isalpha():
            base = 65 if char.isupper() else 97
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result


def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)


def vigenere_encrypt(text, key):
    result = ''
    key = key.lower()
    i = 0
    for char in text:
        if char.isalpha():
            base = 65 if char.isupper() else 97
            shift = ord(key[i % len(key)]) - 97
            result += chr((ord(char) - base + shift) % 26 + base)
            i += 1
        else:
            result += char
    return result


def vigenere_decrypt(text, key):
    result = ''
    key = key.lower()
    i = 0
    for char in text:
        if char.isalpha():
            base = 65 if char.isupper() else 97
            shift = ord(key[i % len(key)]) - 97
            result += chr((ord(char) - base - shift) % 26 + base)
            i += 1
        else:
            result += char
    return result


@csrf_exempt
def security_auth_panel(request):
    context = {}
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "register":
            username = request.POST.get("username")
            password = request.POST.get("password")
            cursor.execute(
                "SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                context["error"] = "Username already exists!"
            else:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                context["success"] = "Registration successful! Please log in."
        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            cursor.execute(
                "SELECT password, attempts, blocked FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                context["error"] = "User not found!"
            else:
                db_password, attempts, blocked = row
                if blocked:
                    context["error"] = "User is blocked!"
                elif password == db_password:
                    cursor.execute(
                        "UPDATE users SET attempts = 0 WHERE username = ?", (username,))
                    conn.commit()
                    request.session["auth_user"] = username
                    return redirect("cipher_panel")
                else:
                    attempts += 1
                    if attempts >= 3:
                        cursor.execute(
                            "UPDATE users SET blocked = 1 WHERE username = ?", (username,))
                        context["error"] = "Too many attempts. User is blocked!"
                    else:
                        cursor.execute(
                            "UPDATE users SET attempts = ? WHERE username = ?", (attempts, username))
                        context["error"] = "Wrong password!"
                    conn.commit()
    return render(request, "pages/security_auth.html", context)


@csrf_exempt
def cipher_panel(request):
    if not request.session.get("auth_user"):
        return redirect("security_auth_panel")
    context = {"user": request.session["auth_user"]}
    if request.method == "POST":
        cipher = request.POST.get("cipher")
        text = request.POST.get("text", "")
        result = ""
        if cipher == "atbash":
            result = atbash(text)
        elif cipher == "caesar":
            shift = int(request.POST.get("shift", 0))
            mode = request.POST.get("mode")
            if mode == "encrypt":
                result = caesar_encrypt(text, shift)
            else:
                result = caesar_decrypt(text, shift)
        elif cipher == "vigenere":
            key = request.POST.get("key", "")
            mode = request.POST.get("mode")
            if mode == "encrypt":
                result = vigenere_encrypt(text, key)
            else:
                result = vigenere_decrypt(text, key)
        context["result"] = result
        context["cipher"] = cipher

    return render(request, "pages/cipher_panel.html", context)


def QR_view(request):
    qr_img = None
    joke = None

    if request.method == "POST":
        action = request.POST.get("action")

        # --- Register user ---
        if action == "register":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

            # Create new user with OTP secret
            if not CustomUser.objects.filter(username=username).exists():
                secret = pyotp.random_base32()
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    secret=secret
                )
                # Generate QR code for MFA
                uri = pyotp.TOTP(secret).provisioning_uri(
                    name=email, issuer_name="IT312_OTP_Django"
                )
                img = qrcode.make(uri)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_img = base64.b64encode(buffer.getvalue()).decode()
            else:
                return HttpResponse("❌ Username already exists")

        # --- Login user ---
        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            otp = request.POST.get("otp")

            user = authenticate(request, username=username, password=password)
            if user:
                totp = pyotp.TOTP(user.secret)
                if totp.verify(otp):
                    login(request, user)
                    # Fetch joke + QR
                    joke_data = requests.get(
                        "https://v2.jokeapi.dev/joke/Any?safe-mode").json()
                    if joke_data["type"] == "single":
                        joke = joke_data["joke"]
                    else:
                        joke = f"{joke_data['setup']} {joke_data['delivery']}"

                    img = qrcode.make(joke)
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    qr_img = base64.b64encode(buffer.getvalue()).decode()
                else:
                    return HttpResponse("❌ Invalid OTP")
            else:
                return HttpResponse("❌ Invalid credentials")

    return render(request, "pages/Qr.html", {"qr_img": qr_img, "joke": joke})


def cipher_encryption(request):
    result = None
    text = ""
    if request.method == "POST":
        text = request.POST.get("text")
        cipher_type = request.POST.get("cipher")
        shift = int(request.POST.get("shift", 3))  # default for Caesar
        key = request.POST.get("key", "LEMON")     # default for Vigenère

        if cipher_type == "atbash":
            result = atbash_cipher(text)
        elif cipher_type == "caesar_encrypt":
            result = caesar_cipher(text, shift)
        elif cipher_type == "caesar_decrypt":
            result = caesar_cipher(text, -shift)
        elif cipher_type == "vigenere_encrypt":
            result = vigenere_cipher(text, key, "encrypt")
        elif cipher_type == "vigenere_decrypt":
            result = vigenere_cipher(text, key, "decrypt")

    return render(request, "pages/CipherEncryption.html", {
        "original": text,
        "result": result
    })


def joke_api_page(request):
    url = "https://v2.jokeapi.dev/joke/Any?type=single"
    response = requests.get(url).json()
    joke = response.get(
        "joke", "Why do programmers prefer dark mode? Because light attracts bugs!")

    return render(request, "joke_api_page.html", {"joke": joke})


def panel6_page(request):
    return render(request, 'pages/panel6.html')


# Api section

def api_integration_panel(request):
    definition = None
    error = None

    if request.method == "POST":
        word = request.POST.get("word", "").strip()
        if word:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            try:
                response = requests.get(url)
                data = response.json()
                if isinstance(data, dict) and data.get("title") == "No Definitions Found":
                    error = f"No definition found for '{word}'."
                else:
                    meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
                    definition = f"{data[0]['word']}: {meaning}"
            except Exception as e:
                error = f"Error fetching definition: {e}"

    return render(request, "pages/api.html", {
        "definition": definition,
        "error": error
    })


load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAILS = os.getenv("TO_EMAILS", "").split(",")


def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(TO_EMAILS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAILS, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# -------------------- Fetch Random Daily Quote --------------------
def fetch_quote():
    """Fetch a motivational quote from APIs (fallback if one fails)."""
    try:
        response = requests.get(
            "https://api.quotable.io/random?tags=motivational|inspirational",
            timeout=10
        )
        data = response.json()
        return f"💡 {data['content']} — {data['author']}"
    except Exception:
        try:
            r = requests.get("https://zenquotes.io/api/random", timeout=10)
            data = r.json()[0]
            return f"💡 {data['q']} — {data['a']}"
        except Exception:
            return "🌟 Stay positive, stay consistent, and keep moving forward!"


# -------------------- Daily Job --------------------
def daily_job():
    """Fetch a quote and send it by email automatically."""
    quote = fetch_quote()
    subject = "🌅 Your Daily Motivation"
    send_email(subject, quote)


# -------------------- Background Scheduler --------------------
def start_scheduler():
    """Run the daily email job automatically at a specific time."""
    def run_schedule():
        # Schedule at 08:00 AM every day (you can change the time below)
        schedule.every().day.at("08:00").do(daily_job)
        print("🕒 Daily Motivation Scheduler started (08:00 AM every day).")
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()


# Start scheduler only once (when Django starts)
if not hasattr(settings, 'SCHEDULER_STARTED'):
    start_scheduler()
    settings.SCHEDULER_STARTED = True


# -------------------- Django View for Manual Trigger --------------------
@csrf_exempt
def automation_panel(request):
    status = None
    if request.method == "POST":
        if "send_test" in request.POST:
            # Fetch a live quote for manual testing
            quote = fetch_quote()
            subject = "💫 Daily Motivation"
            if send_email(subject, quote):
                status = "✅ email sent successfully with a real quote!"
            else:
                status = "❌ Failed to send  email. Check your SMTP settings."
    return render(request, "pages/automation.html", {"status": status})


def atbash(text):
    alphabet = string.ascii_lowercase
    atbash_map = {c: alphabet[::-1][i] for i, c in enumerate(alphabet)}
    result = []
    for ch in text.lower():
        if ch in atbash_map:
            result.append(atbash_map[ch])
        else:
            result.append(ch)
    return "".join(result)


def caesar(text, shift=3):
    result = []
    for ch in text.lower():
        if ch.isalpha():
            shifted = chr(((ord(ch) - 97 + shift) % 26) + 97)
            result.append(shifted)
        else:
            result.append(ch)
    return "".join(result)


def vigenere(text, key):
    text = text.lower()
    key = key.lower().replace(" ", "")
    result = []
    key_index = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_index % len(key)]) - 97
            encrypted = chr(((ord(ch) - 97 + shift) % 26) + 97)
            result.append(encrypted)
            key_index += 1
        else:
            result.append(ch)
    return "".join(result)


def make_qr(text):
    img = qrcode.make(text)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


@csrf_exempt
def jokeapi_encrypt_qr_panel(request):
    joke = None
    atbash_joke = caesar_joke = vigenere_joke = ""
    qr_plain = qr_atbash = qr_caesar = qr_vigenere = ""
    caesar_shift = 6
    vigenere_key = "MANGO"

    if request.method == "POST":
        caesar_shift = int(request.POST.get("caesar_shift", 6))
        vigenere_key = request.POST.get("vigenere_key", "MANGO")
        # Fetch joke
        url = "https://v2.jokeapi.dev/joke/Any?type=single"
        try:
            response = requests.get(url, timeout=10).json()
            joke = response.get(
                "joke", "Why do programmers prefer dark mode? Because light attracts bugs!")
        except Exception:
            joke = "Why do programmers prefer dark mode? Because light attracts bugs!"

        atbash_joke = atbash(joke)
        caesar_joke = caesar(joke, shift=caesar_shift)
        vigenere_joke = vigenere(joke, key=vigenere_key)

        qr_plain = make_qr(joke)
        qr_atbash = make_qr(atbash_joke)
        qr_caesar = make_qr(caesar_joke)
        qr_vigenere = make_qr(vigenere_joke)

    return render(request, "pages/Joke_encrypt_qr.html", {
        "joke": joke,
        "atbash_joke": atbash_joke,
        "caesar_joke": caesar_joke,
        "vigenere_joke": vigenere_joke,
        "qr_plain": qr_plain,
        "qr_atbash": qr_atbash,
        "qr_caesar": qr_caesar,
        "qr_vigenere": qr_vigenere,
        "caesar_shift": caesar_shift,
        "vigenere_key": vigenere_key,
    })
