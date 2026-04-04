import os
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.pkl")
FEATURE_COLS_PATH = os.path.join(MODEL_DIR, "feature_cols.pkl")


class MLEngine:
    def __init__(self):
        self.model = None
        self.feature_cols = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.feature_cols = joblib.load(FEATURE_COLS_PATH)
            print("ML model loaded successfully")
        else:
            print("WARNING: ML model not found. Run ml/train_model.py first.")

    def predict(self, features):
        if not self.model or not self.feature_cols:
            return None, None

        feature_vector = np.array([[features.get(col, 0) for col in self.feature_cols]])

        prediction = self.model.predict(feature_vector)[0]

        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(feature_vector)[0]
            confidence = float(np.max(proba))
        else:
            confidence = 0.5

        return int(prediction), confidence


ml_engine = MLEngine()
