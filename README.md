# Hybrid Ransomware Attack Simulation & Detection System

Educational sandbox project for understanding hybrid ransomware behavior and detection.

## Safety Rules

- Operates only on `test_folder`
- Does not touch system directories
- Intended only for controlled lab/learning environments

## Project Structure

HybridRansomware/
- simulator/encrypt.py
- simulator/decrypt.py
- detector/monitor.py
- ml/train_model.py
- ml/model.pkl
- dashboard/app.py
- dashboard/templates/index.html
- logs/activity_log.txt
- logs/stats.json
- test_folder/
- backup/

## Setup

1. Install dependencies:

   pip install -r requirements.txt

2. Add some sample files into `test_folder`

3. Train ML model:

   python ml/train_model.py

4. Start detector:

   python detector/monitor.py

5. In another terminal, run encryption simulation:

   python simulator/encrypt.py

6. Start dashboard:

   python dashboard/app.py

7. Recover files:

   python simulator/decrypt.py
