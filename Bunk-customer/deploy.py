from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
from keras.models import load_model
from typing import Annotated
import joblib

app = FastAPI()

# Load the trained model and scaler
model = load_model('best_model.h5')
scaler = joblib.load('scaler.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Define the Pydantic model for input validation
class Item(BaseModel):
    CreditScore: int = Field(..., gt=0, description="Credit score of the individual")
    Geography: str = Field(..., description="Geographical location, must be encoded")
    Gender: int = Field(..., ge=0, le=1, description="Gender encoded as 0 or 1")
    Age: int = Field(..., gt=0, description="Age of the individual")
    Tenure: int = Field(..., ge=0, description="Tenure in years")
    Balance: float = Field(..., description="Account balance")
    NumOfProducts: int = Field(..., ge=0, description="Number of products")
    HasCrCard: int = Field(..., ge=0, le=1, description="Has credit card (0 or 1)")
    IsActiveMember: int = Field(..., ge=0, le=1, description="Active member (0 or 1)")
    EstimatedSalary: float = Field(..., description="Estimated salary of the individual")
@app.post("/predict")
async def predict(item: Item):
    # Create DataFrame from input
    input_data = pd.DataFrame([item.dict()])

    # Handle unseen Geography labels
    if item.Geography not in label_encoder.classes_:
        raise HTTPException(status_code=400, detail=f"Geography '{item.Geography}' is not recognized.")

    # Label encode the 'Geography' feature
    input_data['Geography'] = label_encoder.transform(input_data['Geography'])

    # Scale the features
    input_scaled = scaler.transform(input_data)

    # Make prediction
    prediction = model.predict(input_scaled)
    predicted_class = (prediction > 0.5).astype(int)[0][0]  # Assuming binary classification

    return {
        'prediction': int(predicted_class)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
