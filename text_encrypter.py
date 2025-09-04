#!/usr/bin/env python3
"""
text-encrypter — Encrypt & decrypt text or files using Fernet encryption.
"""

import argparse
import os
import platform
import sys
from pathlib import Path
from cryptography.fernet import Fernet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

PROGRAM = "text-encrypter"
VERSION = "0.1.0"
DESCRIPTION = "A simple tool to lock and unlock text or files using Fernet encryption."

console = Console()

# ---------- Key management ----------
def default_key_path() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.getenv("APPDATA") or Path.home() / "AppData/Roaming")
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux and others
        base = Path.home() / ".local" / "share"
    path = base / PROGRAM
    path.mkdir(parents=True, exist_ok=True)
    return path / "fernet.key"


def generate_key() -> bytes:
    return Fernet.generate_key()


def save_key(key: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)
    console.print(f"[green]✔ Saved key to {path}[/]")


def load_key(path: Path) -> bytes:
    return path.read_bytes()


# ---------- Crypto ----------
def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)


def decrypt_bytes(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


def encrypt_file(path: Path, key: bytes):
    data = path.read_bytes()
    enc = encrypt_bytes(data, key)
    out = path.with_suffix(path.suffix + ".enc")
    out.write_bytes(enc)
    console.print(f"[cyan]Encrypted → {out}[/]")


def decrypt_file(path: Path, key: bytes):
    data = path.read_bytes()
    dec = decrypt_bytes(data, key)
    out = path.with_suffix("") if path.suffix == ".enc" else path.with_suffix(path.suffix + ".dec")
    out.write_bytes(dec)
    console.print(f"[cyan]Decrypted → {out}[/]")


# ---------- CLI ----------
def build_parser():
    p = argparse.ArgumentParser(prog=PROGRAM, description=DESCRIPTION, add_help=False)
    p.add_argument("-h", "--help", action="store_true", help="Show help message")
    p.add_argument("-v", "--version", action="store_true", help="Show version")
    p.add_argument("-g", "--generate", nargs="?", const=str(default_key_path()),
                   help=f"Generate new key (default: {default_key_path()})")
    p.add_argument("-e", "--encrypt", action="store_true", help="Encrypt file or text")
    p.add_argument("-d", "--decrypt", action="store_true", help="Decrypt file or text")
    p.add_argument("-f", "--file", type=str, help="Path to file")
    p.add_argument("-t", "--text", type=str, help="Text to encrypt or decrypt")
    p.add_argument("-k", "--key", type=str, help="Path to key file")
    return p


def print_help():
    console.print(Panel(Text(
f"""
{PROGRAM} v{VERSION}
{DESCRIPTION}

Usage: {PROGRAM} [options]

Options:
  -h, --help         Show help message
  -v, --version      Show version
  -g, --generate     Generate new key
  -e, --encrypt      Encrypt file or text
  -d, --decrypt      Decrypt file or text
  -f, --file         Path to file
  -t, --text         Text to encrypt/decrypt
  -k, --key          Path to key file
""", justify="left"), border_style="dim"))


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.help or len(sys.argv) == 1:
        print_help()
        return

    if args.version:
        console.print(f"{PROGRAM} v{VERSION}")
        return

    if args.generate is not None:
        path = Path(args.generate)
        save_key(generate_key(), path)
        return

    key_path = Path(args.key) if args.key else default_key_path()
    if not key_path.exists():
        console.print(f"[yellow]! No key found, generating one at {key_path}[/]")
        save_key(generate_key(), key_path)
    key = load_key(key_path)

    if args.encrypt:
        if args.text:
            token = encrypt_bytes(args.text.encode(), key).decode()
            console.print(f"[green]Encrypted token:[/]\n{token}")
        elif args.file:
            encrypt_file(Path(args.file), key)
    elif args.decrypt:
        if args.text:
            plain = decrypt_bytes(args.text.encode(), key).decode()
            console.print(f"[green]Decrypted text:[/]\n{plain}")
        elif args.file:
            decrypt_file(Path(args.file), key)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print_exception()
        sys.exit(1)
