import pytest
import time
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# 1. Ensure the project root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Import from main (since we renamed app.py to main.py to fix conflicts)
from main import app 
client = TestClient(app)

@pytest.fixture
def valid_payload():
    """Matches the exact 16 feature_cols required by the RandomForestRegressor."""
    return {
        "Momentum_7d": 0.01, "Momentum_30d": 0.02, "Momentum_60d": 0.03, "Momentum_90d": 0.04,
        "Volatility_30d": 0.15, "Mom_30_90_ratio": 0.8, "RangePos_30d": 0.5, "RangePos_90d": 0.6,
        "MA_7_30_ratio": 1.02, "Mom30_vol30": 0.5, "Volume_z30": 1.2, "VolMom_30": 0.3,
        "Momentum_30d_rank": 0.75, "Momentum_90d_rank": 0.82, "Volatility_30d_rank": 0.45,
        "ma_spread_pct": 0.05
    }

class TestPredictionAPI:
    
    def test_predict_success(self, valid_payload):
        """Tests successful prediction with all 16 features."""
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200
        assert "prediction" in response.json()
        assert isinstance(response.json()["prediction"], float)

    def test_predict_invalid_data_count(self):
        """Tests failure when sending only partial features (e.g., just 4)."""
        # Sending only the ranks will now trigger a 422 because 16 are required
        partial_payload = {
            "Momentum_30d_rank": 0.75, 
            "Momentum_90d_rank": 0.82, 
            "Volatility_30d_rank": 0.45,
            "ma_spread_pct": 0.05
        }
        response = client.post("/predict", json=partial_payload)
        assert response.status_code == 422

    @patch("main.model.predict") # Updated path to main.model
    def test_model_crash_behavior(self, mock_predict, valid_payload):
        """Tests that a model exception triggers a 500 error."""
        mock_predict.side_effect = Exception("Model Inference Error")
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 500

    def test_latency_performance(self, valid_payload):
        """Ensures prediction returns in under 500ms."""
        start = time.time()
        client.post("/predict", json=valid_payload)
        latency = (time.time() - start) * 1000
        assert latency < 500