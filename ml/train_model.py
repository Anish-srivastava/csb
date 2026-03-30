"""
Train a simple ransomware behavior classifier.

Features:
- file_change_rate
- extension_change_count

Output:
- model.pkl
"""

from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"


def build_synthetic_dataset(n_samples: int = 1000):
    """Generate beginner-friendly synthetic data for behavior classification."""
    rng = np.random.default_rng(seed=42)

    file_change_rate = rng.uniform(0, 20, n_samples)
    extension_change_count = rng.integers(0, 15, n_samples)

    # Basic rule with small random noise to mimic real-world variance.
    labels = (
        (file_change_rate > 8) & (extension_change_count > 3)
    ).astype(int)

    noise_idx = rng.choice(n_samples, size=int(0.08 * n_samples), replace=False)
    labels[noise_idx] = 1 - labels[noise_idx]

    X = np.column_stack([file_change_rate, extension_change_count])
    y = labels
    return X, y


def train_and_save_model():
    X, y = build_synthetic_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=120,
        random_state=42,
        max_depth=8,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print("Model evaluation:\n")
    print(classification_report(y_test, predictions, target_names=["Normal", "Ransomware"]))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()
