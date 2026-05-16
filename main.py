import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. Matches your 16 feature_cols exactly
class InputData(BaseModel):
    Momentum_7d: float
    Momentum_30d: float
    Momentum_60d: float
    Momentum_90d: float
    Volatility_30d: float
    Mom_30_90_ratio: float
    RangePos_30d: float
    RangePos_90d: float
    MA_7_30_ratio: float
    Mom30_vol30: float
    Volume_z30: float
    VolMom_30: float
    Momentum_30d_rank: float
    Momentum_90d_rank: float
    Volatility_30d_rank: float
    ma_spread_pct: float

class OutputData(BaseModel):
    prediction: float

app = FastAPI()

# Load the model
base_path = os.path.dirname(__file__)
model_path = os.path.join(base_path, "model.joblib")
model = joblib.load(model_path) #

@app.post("/predict", response_model=OutputData)
async def predict(data: InputData):
    try:
        # 2. Extract values in the specific order the model expects
        input_list = [
            data.Momentum_7d, data.Momentum_30d, data.Momentum_60d, data.Momentum_90d,
            data.Volatility_30d, data.Mom_30_90_ratio, data.RangePos_30d, data.RangePos_90d,
            data.MA_7_30_ratio, data.Mom30_vol30, data.Volume_z30, data.VolMom_30,
            data.Momentum_30d_rank, data.Momentum_90d_rank, data.Volatility_30d_rank,
            data.ma_spread_pct
        ]
        
        input_array = np.array([input_list])
        
        # Now X has 16 features, matching the RandomForestRegressor requirements
        prediction = model.predict(input_array)
        
        return {"prediction": float(prediction[0])}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))