"""Flask dashboard for a sandbox ransomware simulation project."""

import os
from pathlib import Path
import subprocess
import sys
from flask import Flask, redirect, render_template, request, url_for, jsonify

app = Flask(__name__, template_folder="templates")

# Ensure relative paths like ../simulator/encrypt.py resolve from dashboard folder.
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DASHBOARD_DIR)

# Required script paths (relative to dashboard/).
ENCRYPT_SCRIPT = "../simulator/encrypt.py"
DECRYPT_SCRIPT = "../simulator/decrypt.py"
LOG_FILE = "../logs/activity_log.txt"


def resolve_python_executable() -> str:
    """Pick a Python executable that can run simulator scripts reliably."""
    # Prefer the current interpreter first.
    candidates = [Path(sys.executable)]

    # Also try a nearby workspace virtual environment when present.
    workspace_venv = (Path(DASHBOARD_DIR).parent.parent / ".venv" / "Scripts" / "python.exe").resolve()
    candidates.append(workspace_venv)

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    # Final fallback.
    return sys.executable


def run_script(script_path: str, extra_env: dict | None = None) -> tuple[bool, str, str]:
    """Run a Python script and return (success, message, details)."""
    python_exe = resolve_python_executable()
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    result = subprocess.run(
        [python_exe, script_path],
        cwd=DASHBOARD_DIR,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    if result.returncode == 0:
        return True, "", result.stdout.strip()

    # Return stderr (or stdout fallback) to help debugging in dashboard.
    error_text = (result.stderr or result.stdout).strip()
    if not error_text:
        error_text = "Unknown execution error"
    return False, error_text, result.stdout.strip()


def read_logs() -> list[dict]:
    """Read activity_log.txt and return rows for table display."""
    if not os.path.exists(LOG_FILE):
        return []

    rows: list[dict] = []
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    # Skip header line if present.
    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split("|", maxsplit=4)
        if len(parts) != 5:
            continue

        rows.append(
            {
                "timestamp": parts[0],
                "event": parts[1],
                "path": parts[2],
                "classification": parts[3],
                "message": parts[4],
            }
        )

    # Show newest entries first.
    rows.reverse()
    return rows 


@app.route("/")
def index():
    """Render the main dashboard page."""
    status = request.args.get("status", "")
    message = request.args.get("message", "")
    logs = read_logs()
    return render_template("index.html", status=status, message=message, logs=logs)


@app.route("/start_attack", methods=["POST"])
def start_attack():
    """Run the encryption simulation and return JSON response."""
    # Safety reminder: encrypt.py is designed to affect only test_folder.
    success, error, output = run_script(ENCRYPT_SCRIPT)
    
    if success:
        # Extract password from output if present
        password_message = ""
        if "Auto-generated password:" in output:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if "Auto-generated password:" in line:
                    password_message = f"\n🔐 {line.strip()}"
                    if i + 1 < len(lines):
                        password_message += f"\n   {lines[i+1].strip()}"
        
        message = f"Attack simulation completed.{password_message}"
        return jsonify({"success": True, "message": message, "status": "success"})
    
    return jsonify({
        "success": False,
        "message": f"Failed to run attack simulation. {error}",
        "status": "error"
    })


@app.route("/decrypt_files", methods=["POST"])
def decrypt_files():
    """Decrypt files using password (POST only - forms are in index.html modal)."""
    entered_password = request.form.get("password", "")
    if not entered_password.strip():
        return jsonify({"success": False, "message": "Password is required"})

    # Safety reminder: decrypt.py is designed to affect only test_folder.
    # Pass password securely through environment variable for this process only.
    success, error, output = run_script(DECRYPT_SCRIPT, extra_env={"KEY_PASSWORD": entered_password})
    
    if success:
        return jsonify({"success": True, "message": "Files decrypted successfully!"})
    
    if "Incorrect password" in error:
        return jsonify({"success": False, "message": "Incorrect password"})
    
    return jsonify({"success": False, "message": f"Decryption failed. {error}"})


@app.route("/get_logs", methods=["GET"])
def get_logs():
    """API endpoint that returns logs as JSON for AJAX updates."""
    logs = read_logs()
    return jsonify({"logs": logs})


@app.route("/view_log_file", methods=["GET"])
def view_log_file():
    """API endpoint to get raw log file contents."""
    if not os.path.exists(LOG_FILE):
        return jsonify({"content": "", "filename": "activity_log.txt", "lines": 0})
    
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    
    lines = len(content.splitlines())
    return jsonify({
        "content": content,
        "filename": "activity_log.txt",
        "lines": lines
    })


@app.route("/decrypt_with_key", methods=["POST"])
def decrypt_with_key():
    """Decrypt files using a provided encryption key (user enters key manually)."""
    from pathlib import Path
    from cryptography.fernet import Fernet, InvalidToken
    
    try:
        # Get key from POST request
        provided_key = request.form.get('key', '').strip()
        
        if not provided_key:
            return jsonify({"success": False, "message": "No encryption key provided"})
        
        # Verify key format and validity
        try:
            cipher = Fernet(provided_key.encode() if isinstance(provided_key, str) else provided_key)
        except Exception:
            return jsonify({"success": False, "message": "Invalid key format. Please check your encryption key."})
        
        SIMULATOR_DIR = Path(DASHBOARD_DIR).parent / "simulator"
        TEST_FOLDER = SIMULATOR_DIR.parent / "test_folder"
        
        # Find all .locked files
        locked_files = list(TEST_FOLDER.glob('*.locked'))
        if not locked_files:
            return jsonify({"success": False, "message": "No encrypted files found to decrypt"})
        
        decrypted_count = 0
        failed_count = 0
        
        for locked_file in locked_files:
            try:
                # Read encrypted content
                encrypted_data = locked_file.read_bytes()
                
                # Try to decrypt with provided key
                try:
                    decrypted_data = cipher.decrypt(encrypted_data)
                except InvalidToken:
                    failed_count += 1
                    continue
                
                # Get original filename (remove .locked)
                original_filename = locked_file.stem
                original_path = TEST_FOLDER / original_filename
                
                # Write decrypted content
                original_path.write_bytes(decrypted_data)
                
                # Delete the locked file
                locked_file.unlink()
                
                decrypted_count += 1
            except Exception:
                failed_count += 1
        
        if decrypted_count > 0:
            msg = f"✅ Successfully decrypted {decrypted_count} file(s)!"
            if failed_count > 0:
                msg += f" ({failed_count} file(s) could not be decrypted with this key)"
            return jsonify({"success": True, "message": msg})
        else:
            return jsonify({"success": False, "message": f"❌ Could not decrypt any files. The key may be incorrect or files are already decrypted."})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)[:100]}"})



if __name__ == "__main__":
    # Run with: python app.py
    # Open in browser: http://127.0.0.1:5000
    app.run(debug=False, use_reloader=False, host="127.0.0.1", port=5000)
