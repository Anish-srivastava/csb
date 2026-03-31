"""Encrypt files in ../test_folder using Fernet and rename them to .locked."""

from pathlib import Path

from cryptography.fernet import Fernet

# simulator -> ../test_folder and ../logs style pathing from this script's folder.
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


def load_or_create_key() -> bytes:
    """Generate key.key once, then reuse it for all future runs."""
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()

    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    print(f"Created key file: {KEY_PATH}")
    return key


def encrypt_files() -> None:
    ensure_test_folder_with_dummy_files()
    key = load_or_create_key()
    cipher = Fernet(key)

    encrypted_count = 0
    for file_path in TEST_FOLDER.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix == ".locked":
            continue
        if not is_inside_test_folder(file_path):
            continue

        plaintext = file_path.read_bytes()
        encrypted_data = cipher.encrypt(plaintext)
        file_path.write_bytes(encrypted_data)

        locked_path = file_path.with_name(f"{file_path.name}.locked")
        file_path.rename(locked_path)

        encrypted_count += 1
        print(f"Encrypted: {file_path.name} -> {locked_path.name}")

    print(f"Encryption complete. Total files encrypted: {encrypted_count}")


if __name__ == "__main__":
    encrypt_files()
