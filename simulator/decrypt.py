"""Decrypt .locked files in ../test_folder using simulator/key.key."""

from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

SIMULATOR_DIR = Path(__file__).resolve().parent
TEST_FOLDER = (SIMULATOR_DIR / "../test_folder").resolve()
KEY_PATH = SIMULATOR_DIR / "key.key"


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


def decrypt_files() -> None:
    if not TEST_FOLDER.exists():
        print(f"test_folder not found: {TEST_FOLDER}")
        return

    key = load_key()
    if key is None:
        return

    cipher = Fernet(key)
    decrypted_count = 0

    for locked_file in TEST_FOLDER.rglob("*.locked"):
        if not locked_file.is_file():
            continue
        if not is_inside_test_folder(locked_file):
            continue

        try:
            encrypted_data = locked_file.read_bytes()
            plaintext = cipher.decrypt(encrypted_data)
        except InvalidToken:
            print(f"Skipped (invalid key or data): {locked_file.name}")
            continue

        restored_path = locked_file.with_name(locked_file.name[: -len(".locked")])
        restored_path.write_bytes(plaintext)
        locked_file.unlink()

        decrypted_count += 1
        print(f"Restored: {locked_file.name} -> {restored_path.name}")

    print(f"Decryption complete. Total files restored: {decrypted_count}")


if __name__ == "__main__":
    decrypt_files()
