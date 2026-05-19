from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.dependencies import get_current_user
from app.services.model_service import model_service

router = APIRouter(tags=["prediction"])

class PredictionRequest(BaseModel):
    Company: str = Field(..., description="Laptop manufacturer brand", example="HP")
    TypeName: str = Field(..., description="Type category of laptop", example="Notebook")
    Ram: int = Field(..., description="RAM size in GB", ge=2, le=64, example=8)
    Weight: float = Field(..., description="Weight of the laptop in kg", ge=0.5, le=5.0, example=2.0)
    Touchscreen: str = Field(..., description="Whether it has touchscreen ('Yes' or 'No')", example="No")
    Ips: str = Field(..., description="Whether it has IPS panel ('Yes' or 'No')", example="No")
    Screen_size: float = Field(..., description="Diagonal screen size in inches", ge=10.0, le=20.0, example=15.6)
    Resolution: str = Field(..., description="Screen resolution string", example="1920x1080")
    Cpu_brand: str = Field(..., description="Processor brand name", example="Intel Core i5")
    Cpu_Speed: float = Field(..., description="Processor clock speed in GHz", ge=0.5, le=5.0, example=2.5)
    HDD: int = Field(..., description="HDD capacity in GB", example=0)
    SSD: int = Field(..., description="SSD capacity in GB", example=256)
    Gpu_brand: str = Field(..., description="Graphics card manufacturer", example="Intel")
    OS: str = Field(..., description="Operating System installed", example="Windows")

class PredictionResponse(BaseModel):
    success: bool
    predicted_price: int
    currency: str = "INR"

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_price(
    payload: PredictionRequest,
    current_user: str = Depends(get_current_user)
):
    # Convert request schema to dictionary of params expected by model_service
    specs_dict = payload.model_dump()
    predicted_price = model_service.predict_price(specs_dict)
    return PredictionResponse(success=True, predicted_price=predicted_price)
