#!/usr/bin/env python3
"""
text-encrypter — encrypt & decrypt text or files using Fernet (symmetric) encryption.
"""

import argparse
import os
import platform
import sys
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

# Optional: nice console output if rich is installed
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    def info(msg): console.print(f"[bold cyan]›[/] {msg}")
    def ok(msg): console.print(f"[bold green]✔[/] {msg}")
    def warn(msg): console.print(f"[bold yellow]![/] {msg}")
    def err(msg): console.print(f"[bold red]✘[/] {msg}")
    def banner():
        console.print(Panel(Text("text-encrypter", justify="center", style="bold"),
                            title="🔐 Fernet", border_style="dim"))
except Exception:
    console = None
    def info(msg): print(f"[i] {msg}")
    def ok(msg): print(f"[+] {msg}")
    def warn(msg): print(f"[!] {msg}")
    def err(msg): print(f"[x] {msg}")
    def banner(): print("=== text-encrypter (Fernet) ===")


PROGRAM = "text-encrypter"
DESCRIPTION = "Encrypt or decrypt TEXT or FILES with a single shared key."
VERSION = "0.2.0"


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
    ok(f"Saved key to {path}")


def load_key(path: Path) -> bytes:
    return path.read_bytes()


def resolve_key(user_path: Optional[str]) -> bytes:
    """
    Load key from user provided path, else default path.
    If missing, create a new one at default path.
    """
    if user_path:
        p = Path(user_path)
        if not p.exists():
            err(f"Key not found: {p}")
            sys.exit(1)
        return load_key(p)

    p = default_key_path()
    if not p.exists():
        warn(f"No key found at {p}. Generating a new one…")
        save_key(generate_key(), p)
    return load_key(p)


# ---------- Core crypto ----------
def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)


def decrypt_bytes(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


# ---------- Actions ----------
def do_encrypt_text(text: Optional[str], key: bytes) -> None:
    if text is None:
        text = input("Enter text to encrypt: ")
    token = encrypt_bytes(text.encode("utf-8"), key)
    ok("Encrypted token (copy this safely):")
    print(token.decode("utf-8"))


def do_decrypt_text(token_str: Optional[str], key: bytes) -> None:
    if token_str is None:
        token_str = input("Paste encrypted token: ")
    try:
        plain = decrypt_bytes(token_str.encode("utf-8"), key).decode("utf-8")
        ok("Decrypted text:")
        print(plain)
    except Exception as e:
        err(f"Failed to decrypt: {e}")
        sys.exit(1)


def do_encrypt_file(src: str, dst: Optional[str], key: bytes) -> None:
    src_p = Path(src)
    if not src_p.exists() or not src_p.is_file():
        err(f"File not found: {src}")
        sys.exit(1)

    data = src_p.read_bytes()
    token = encrypt_bytes(data, key)
    out = Path(dst) if dst else src_p.with_suffix(src_p.suffix + ".enc")
    out.write_bytes(token)
    ok(f"Encrypted → {out}")


def do_decrypt_file(src: str, dst: Optional[str], key: bytes) -> None:
    src_p = Path(src)
    if not src_p.exists() or not src_p.is_file():
        err(f"File not found: {src}")
        sys.exit(1)

    token = src_p.read_bytes()
    try:
        data = decrypt_bytes(token, key)
    except Exception as e:
        err(f"Failed to decrypt: {e}")
        sys.exit(1)

    if dst:
        out = Path(dst)
    else:
        # strip one .enc if present
        out = src_p
        if out.suffix == ".enc":
            out = out.with_suffix("")
        else:
            out = out.with_suffix(out.suffix + ".dec")

    out.write_bytes(data)
    ok(f"Decrypted → {out}")


# ---------- CLI ----------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=PROGRAM, description=DESCRIPTION)
    p.add_argument("-v", "--version", action="store_true", help="Show version")
    p.add_argument("-k", "--key", type=str, help="Path to key file (optional)")
    sub = p.add_subparsers(dest="cmd")

    g = sub.add_parser("genkey", help="Generate and save a new key")
    g.add_argument("--out", type=str, help="Where to save (default OS path)")

    et = sub.add_parser("enc-text", help="Encrypt a text string")
    et.add_argument("--text", type=str, help="Text to encrypt (or will prompt)")

    dt = sub.add_parser("dec-text", help="Decrypt a token string")
    dt.add_argument("--token", type=str, help="Token to decrypt (or will prompt)")

    ef = sub.add_parser("enc-file", help="Encrypt a file")
    ef.add_argument("--file", required=True, type=str, help="Path to input file")
    ef.add_argument("--out", type=str, help="Output path (default: input.ext.enc)")

    df = sub.add_parser("dec-file", help="Decrypt a file")
    df.add_argument("--file", required=True, type=str, help="Path to encrypted file")
    df.add_argument("--out", type=str, help="Output path (default: strip .enc)")

    return p


def main() -> None:
    banner()
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        ok(f"{PROGRAM} {VERSION}")
        return

    if args.cmd == "genkey":
        path = Path(args.out) if args.out else default_key_path()
        save_key(generate_key(), path)
        return

    # for all other commands we need a key
    key = resolve_key(args.key)

    if args.cmd == "enc-text":
        do_encrypt_text(args.text, key)
    elif args.cmd == "dec-text":
        do_decrypt_text(args.token, key)
    elif args.cmd == "enc-file":
        do_encrypt_file(args.file, args.out, key)
    elif args.cmd == "dec-file":
        do_decrypt_file(args.file, args.out, key)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        warn("Cancelled.")
        sys.exit(130)
