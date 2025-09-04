# 🔐 Text Encrypter
A simple tool to lock and unlock text or files using Fernet encryption.

<img width="958" height="182" alt="image" src="https://github.com/user-attachments/assets/67f92a28-d404-4493-906e-6cefb0802830" />



---

### 📦 Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/4yzz/text-encrypter.git
cd text-encrypter
python -m pip install -r requirements.txt
```

### 🚀 Usage
```bash
# Generate key
> python text_encrypter.py --generate

# Encrypt text
> python text_encrypter.py --encrypt --text "hello"

# Decrypt text
> python text_encrypter.py --decrypt --text "gAAAAABk..."

# Encrypt file
> python text_encrypter.py --encrypt --file secret.txt

# Decrypt file
> python text_encrypter.py --decrypt --file secret.txt.enc

# Use custom key
> python text_encrypter.py --encrypt --file secret.txt --key my_custom.key
```
# 📄 Documentation
[Fernet](https://cryptography.io/en/latest/fernet/)

