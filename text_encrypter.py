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

# ---- Pretty CLI (rich) ----
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

PROGRAM = "text-encrypter"
VERSION = "0.1.0"
DESCRIPTION = "A simple tool to lock and unlock text or files using Fernet encryption."


# ---------- Key management ----------
def default_key_path() -> Path:
    """Return OS-specific default key path."""
    system = platform.system()
    if system == "Windows":
        base = Path(os.getenv("APPDATA") or Path.home() / "AppData/Roaming")
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux/other
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


def resolve_key(path_str: str | None) -> bytes:
    """Load a key from provided path or the default path (auto-create if missing)."""
    if path_str:
        p = Path(path_str)
        if not p.exists():
            console.print(f"[red]✘ Key not found:[/] {p}")
            sys.exit(1)
        return load_key(p)

    p = default_key_path()
    if not p.exists():
        console.print(f"[yellow]! No key found. Generating one at {p}[/]")
        save_key(generate_key(), p)
    return load_key(p)


# ---------- Crypto helpers ----------
def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)


def decrypt_bytes(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


def encrypt_file(path: Path, key: bytes) -> Path:
    data = path.read_bytes()
    enc = encrypt_bytes(data, key)
    out = path.with_suffix(path.suffix + ".enc")
    out.write_bytes(enc)
    console.print(f"[cyan]Encrypted →[/] {out}")
    return out


def decrypt_file(path: Path, key: bytes) -> Path:
    data = path.read_bytes()
    dec = decrypt_bytes(data, key)
    out = path.with_suffix("") if path.suffix == ".enc" else path.with_suffix(path.suffix + ".dec")
    out.write_bytes(dec)
    console.print(f"[cyan]Decrypted →[/] {out}")
    return out


# ---------- Fancy help ----------
def print_help():
    header = Text(
        f"{PROGRAM} v{VERSION}\n{DESCRIPTION}\n\nUsage: {PROGRAM} [options]",
        justify="center",
        style="bold magenta",
    )
    console.print(Panel(header, border_style="cyan"))

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_row("-h, --help",     "Show help message",            style="green")
    table.add_row("-v, --version",  "Show version",                  style="green")
    table.add_row("-g, --generate", "Generate new key (save to default path)", style="yellow")
    table.add_row("-e, --encrypt",  "Encrypt file or text",          style="cyan")
    table.add_row("-d, --decrypt",  "Decrypt file or text",          style="cyan")
    table.add_row("-f, --file",     "Path to file",                  style="blue")
    table.add_row("-t, --text",     "Text to encrypt/decrypt",       style="blue")
    table.add_row("-k, --key",      "Path to key file",              style="magenta")
    console.print(table)

    # Footer link (styled like your friend's)
    footer = Text("4yzz.github.io", style="bold #b169dd")
    # Make it clickable in terminals that support links
    footer.stylize("link https://4yzz.github.io", 0, len(footer))
    console.print(Panel(footer, border_style="#542c91", title="", title_align="right"))


# ---------- CLI ----------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=PROGRAM, description=DESCRIPTION, add_help=False)
    p.add_argument("-h", "--help", action="store_true", help="Show help message")
    p.add_argument("-v", "--version", action="store_true", help="Show version")
    p.add_argument(
        "-g", "--generate", action="store_true",
        help="Generate new key at default path",
    )
    p.add_argument("-e", "--encrypt", action="store_true", help="Encrypt file or text")
    p.add_argument("-d", "--decrypt", action="store_true", help="Decrypt file or text")
    p.add_argument("-f", "--file", type=str, help="Path to file")
    p.add_argument("-t", "--text", type=str, help="Text to encrypt/decrypt")
    p.add_argument("-k", "--key", type=str, help="Path to key file (optional)")
    return p


def main():
    args = build_parser().parse_args()

    if args.help or len(sys.argv) == 1:
        print_help()
        return

    if args.version:
        console.print(f"{PROGRAM} v{VERSION}")
        return

    if args.generate:
        save_key(generate_key(), default_key_path())
        return

    key = resolve_key(args.key)

    try:
        if args.encrypt:
            if args.text is not None:
                token = encrypt_bytes(args.text.encode("utf-8"), key).decode("utf-8")
                console.print("[green]Encrypted token (copy safely):[/]\n" + token)
            elif args.file:
                p = Path(args.file)
                if not p.exists():
                    console.print(f"[red]✘ File not found:[/] {p}")
                    sys.exit(1)
                encrypt_file(p, key)
            else:
                console.print("[yellow]! Provide --text or --file with --encrypt[/]")
        elif args.decrypt:
            if args.text is not None:
                try:
                    plain = decrypt_bytes(args.text.encode("utf-8"), key).decode("utf-8")
                    console.print("[green]Decrypted text:[/]\n" + plain)
                except Exception as e:
                    console.print(f"[red]✘ Failed to decrypt text:[/] {e}")
                    sys.exit(1)
            elif args.file:
                p = Path(args.file)
                if not p.exists():
                    console.print(f"[red]✘ File not found:[/] {p}")
                    sys.exit(1)
                try:
                    decrypt_file(p, key)
                except Exception as e:
                    console.print(f"[red]✘ Failed to decrypt file:[/] {e}")
                    sys.exit(1)
            else:
                console.print("[yellow]! Provide --text or --file with --decrypt[/]")
        else:
            print_help()
    except KeyboardInterrupt:
        console.print("[yellow]Cancelled.[/]")
        sys.exit(130)


if __name__ == "__main__":
    main()
