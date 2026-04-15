"""Decrypt .locked files in ../test_folder using simulator/key.key."""

import getpass
import hashlib
import os
from pathlib import Path
import sys

from cryptography.fernet import Fernet, InvalidToken

# Build paths relative to this file so script execution location does not matter.
SIMULATOR_DIR = Path(__file__).resolve().parent
TEST_FOLDER = (SIMULATOR_DIR / "../test_folder").resolve()
KEY_PATH = SIMULATOR_DIR / "key.key"
KEY_PASSWORD_HASH_PATH = SIMULATOR_DIR / "key_password.sha256"


def is_inside_test_folder(path: Path) -> bool:
    """Safety check: only allow operations inside test_folder."""
    try:
        path.resolve().relative_to(TEST_FOLDER)
        return True
    except ValueError:
        return False


def load_key() -> bytes | None:
    """Load key.key if available."""
    if not KEY_PATH.exists():
        print(f"Key file not found: {KEY_PATH}")
        print("Run encrypt.py first to create key.key")
        return None
    return KEY_PATH.read_bytes()


def get_entered_password() -> str | None:
    """Get password from env (dashboard) or terminal prompt."""
    env_password = os.getenv("KEY_PASSWORD", "").strip()
    if env_password:
        return env_password

    try:
        password = getpass.getpass("Enter password for key.key: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("Password input cancelled.")
        return None

    if not password:
        print("Password cannot be empty.")
        return None
    return password


def verify_password(password: str) -> bool:
    """Verify entered password against saved hash from encryption step."""
    if not KEY_PASSWORD_HASH_PATH.exists():
        print(f"Password hash file not found: {KEY_PASSWORD_HASH_PATH}")
        print("Run encrypt.py to generate key.key and password hash.")
        return False

    saved_hash = KEY_PASSWORD_HASH_PATH.read_text(encoding="utf-8").strip()
    entered_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return saved_hash == entered_hash


def decrypt_files() -> int:
    # Step 1: ensure test_folder exists.
    if not TEST_FOLDER.exists():
        print(f"test_folder not found: {TEST_FOLDER}")
        return 1

    # Step 2: load the same key used for encryption.
    key = load_key()
    if key is None:
        return 1

    # Step 3: ask and verify password for key.key.
    password = get_entered_password()
    if password is None:
        return 1
    if not verify_password(password):
        print("Incorrect password")
        return 1

    cipher = Fernet(key)
    decrypted_count = 0
    found_locked_files = 0

    for locked_file in TEST_FOLDER.rglob("*.locked"):
        if not locked_file.is_file():
            continue
        if not is_inside_test_folder(locked_file):
            continue

        found_locked_files += 1

        try:
            # Step 4: decrypt *.locked file bytes.
            encrypted_data = locked_file.read_bytes()
            plaintext = cipher.decrypt(encrypted_data)
        except InvalidToken:
            print(f"Skipped (invalid key or data): {locked_file.name}")
            continue

        # Step 5: restore original filename by removing .locked suffix.
        restored_path = locked_file.with_name(locked_file.name[: -len(".locked")])
        restored_path.write_bytes(plaintext)
        locked_file.unlink()

        decrypted_count += 1
        print(f"Restored: {locked_file.name} -> {restored_path.name}")

    if found_locked_files > 0 and decrypted_count == 0:
        print("Decryption failed. No files could be restored.")
        return 1

    print(f"Decryption complete. Total files restored: {decrypted_count}")
    return 0


if __name__ == "__main__":
    sys.exit(decrypt_files())
