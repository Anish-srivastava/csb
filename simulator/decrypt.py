"""
Hybrid Ransomware Recovery Script (Educational)

Safety notes:
- This script only decrypts files inside the local test_folder directory.
- It is intended for controlled lab environments only.
"""

from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FOLDER = BASE_DIR / "test_folder"
PRIVATE_KEY_PATH = BASE_DIR / "private.pem"
ENCRYPTED_AES_KEY_PATH = BASE_DIR / "simulator" / "encrypted_aes_key.bin"


def is_inside_test_folder(path: Path) -> bool:
    """Return True only when path is inside test_folder."""
    try:
        path.resolve().relative_to(TEST_FOLDER.resolve())
        return True
    except ValueError:
        return False


def decrypt_aes_key_with_rsa() -> bytes:
    """Recover AES key by decrypting it with the RSA private key."""
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(),
        password=None,
    )
    encrypted_aes_key = ENCRYPTED_AES_KEY_PATH.read_bytes()

    return private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def decrypt_files() -> None:
    """Decrypt every .locked file in test_folder and restore original names."""
    if not TEST_FOLDER.exists():
        print(f"test_folder not found: {TEST_FOLDER}")
        return

    if not PRIVATE_KEY_PATH.exists() or not ENCRYPTED_AES_KEY_PATH.exists():
        print("Missing private key or encrypted AES key. Run encrypt.py first.")
        return

    aes_key = decrypt_aes_key_with_rsa()
    cipher = Fernet(aes_key)

    decrypted_count = 0

    for locked_file in TEST_FOLDER.rglob("*.locked"):
        if not locked_file.is_file():
            continue
        if not is_inside_test_folder(locked_file):
            continue

        encrypted_data = locked_file.read_bytes()
        plaintext = cipher.decrypt(encrypted_data)

        restored_path = locked_file.with_name(locked_file.name[:-7])
        restored_path.write_bytes(plaintext)
        locked_file.unlink()

        decrypted_count += 1
        print(f"Decrypted: {locked_file.name} -> {restored_path.name}")

    print(f"Decryption complete. Total files restored: {decrypted_count}")


if __name__ == "__main__":
    decrypt_files()
