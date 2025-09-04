# 🔐 Text Encrypter
A simple tool to lock and unlock text or files using Fernet encryption.

<img width="958" height="188" alt="80e6070d-1bbd-4d85-b7ee-bdf4d75b7030" src="https://github.com/user-attachments/assets/5c853481-eec4-4367-9815-1d06cb29ee7c" />


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

