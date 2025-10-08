# accounts/cipher_text.py

def atbash_cipher(text):
    result = []
    for char in text:
        if char.isalpha():
            if char.isupper():
                transformed = chr(65 + (25 - (ord(char) - 65)))
            else:
                transformed = chr(97 + (25 - (ord(char) - 97)))
            result.append(transformed)
        else:
            result.append(char)
    return ''.join(result)


def caesar_cipher(text, shift):
    result = ''
    for char in text:
        if char.isalpha():
            if char.islower():
                result += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            result += char
    return result


def vigenere_cipher(text, key, mode='encrypt'):
    result = ''
    key = key.lower()
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('a')
            if mode == 'decrypt':
                shift = -shift
            base = ord('a') if char.islower() else ord('A')
            result += chr((ord(char) - base + shift) % 26 + base)
            key_index += 1
        else:
            result += char
    return result
