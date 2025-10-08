# accounts/jokeapi.py
import requests
import qrcode
import string
import base64
from io import BytesIO

# --- Encryption Functions ---


def atbash(text):
    alphabet = string.ascii_lowercase
    atbash_map = {c: alphabet[::-1][i] for i, c in enumerate(alphabet)}
    return "".join(atbash_map.get(ch, ch) for ch in text.lower())


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

# --- QR helper ---


def make_qr(text):
    img = qrcode.make(text)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# --- Main function ---


def get_joke_and_encrypt():
    # Fetch random joke
    url = "https://v2.jokeapi.dev/joke/Any?type=single"
    response = requests.get(url).json()
    joke = response.get(
        "joke", "Why do programmers prefer dark mode? Because light attracts bugs!")

    # Encryptions
    atbash_joke = atbash(joke)
    caesar_joke = caesar(joke, shift=6)
    vigenere_joke = vigenere(joke, key="MANGO")

    # QR Codes
    qr_plain = make_qr(joke)
    qr_atbash = make_qr(atbash_joke)
    qr_caesar = make_qr(caesar_joke)
    qr_vigenere = make_qr(vigenere_joke)

    return {
        "joke": joke,
        "atbash_joke": atbash_joke,
        "caesar_joke": caesar_joke,
        "vigenere_joke": vigenere_joke,
        "qr_plain": qr_plain,
        "qr_atbash": qr_atbash,
        "qr_caesar": qr_caesar,
        "qr_vigenere": qr_vigenere,
    }
