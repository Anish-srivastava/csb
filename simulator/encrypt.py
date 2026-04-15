"""Encrypt files in ../test_folder using Fernet and rename them to .locked."""

import getpass
import hashlib
import os
from pathlib import Path
import sys

from cryptography.fernet import Fernet

# Build paths relative to this file so the script works from any current directory.
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


def ensure_test_folder_with_dummy_files() -> None:
    """Create test_folder and 5 dummy files when it is empty."""
    TEST_FOLDER.mkdir(parents=True, exist_ok=True)
    existing_files = [p for p in TEST_FOLDER.iterdir() if p.is_file()]
    if existing_files:
        return

    for index in range(1, 6):
        file_path = TEST_FOLDER / f"test{index}.txt"
        file_path.write_text(
            f"This is dummy test file {index}.\n",
            encoding="utf-8",
        )
    print("test_folder was empty. Created 5 dummy files.")


def get_key_password() -> str | None:
    """Get key password from env (dashboard) or auto-generate."""
    env_password = os.getenv("KEY_PASSWORD", "").strip()
    if env_password:
        return env_password

    # For direct CLI use, ask password interactively (only if running in terminal).
    try:
        password = getpass.getpass("Set password for key.key (or press Enter for auto-generate): ").strip()
        if password:
            confirm = getpass.getpass("Confirm password: ").strip()
            if password == confirm:
                return password
            else:
                print("Passwords do not match.")
                return None
    except (EOFError, KeyboardInterrupt):
        pass

    # Auto-generate password if no input or error
    import random
    import string
    chars = string.ascii_letters + string.digits + "!@#$%"
    auto_password = ''.join(random.choice(chars) for _ in range(12))
    print(f"\n🔐 Auto-generated password: {auto_password}")
    print(f"   Keep this password safe! You'll need it to decrypt files.\n")
    return auto_password


def generate_new_key(password: str) -> bytes:
    """Generate a fresh key.key for every attack and save password hash."""
    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    KEY_PASSWORD_HASH_PATH.write_text(password_hash, encoding="utf-8")

    print(f"Generated new key file: {KEY_PATH}")
    print(f"Saved password hash file: {KEY_PASSWORD_HASH_PATH}")
    return key


def encrypt_files() -> int:
    # Step 1: make sure test data exists.
    ensure_test_folder_with_dummy_files()

    # Step 2: find files that can actually be encrypted now.
    encryptable_files: list[Path] = []
    for file_path in TEST_FOLDER.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix == ".locked":
            continue
        if not is_inside_test_folder(file_path):
            continue
        encryptable_files.append(file_path)

    # If there are only .locked files, do not rotate key.
    if not encryptable_files:
        print("No unlocked files found. Attack skipped and key.key was not changed.")
        return 0

    # Step 3: get password and generate a new key for this attack.
    password = get_key_password()
    if password is None:
        return 1

    key = generate_new_key(password)
    cipher = Fernet(key)

    encrypted_count = 0
    for file_path in encryptable_files:

        # Step 4: encrypt file bytes.
        plaintext = file_path.read_bytes()
        encrypted_data = cipher.encrypt(plaintext)
        file_path.write_bytes(encrypted_data)

        # Step 5: rename encrypted file to *.locked.
        locked_path = file_path.with_name(f"{file_path.name}.locked")
        file_path.rename(locked_path)

        encrypted_count += 1
        print(f"Encrypted: {file_path.name} -> {locked_path.name}")

    print(f"Encryption complete. Total files encrypted: {encrypted_count}")
    return 0


if __name__ == "__main__":
    sys.exit(encrypt_files())
