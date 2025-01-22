from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import json

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 로드
class FoodDetectionModel:
    def __init__(self, model_path="best.pt"):
        self.model = YOLO(model_path)
        self.class_names = self.model.names  # 클래스 이름 로드
        
    def predict(self, image):
        results = self.model.predict(image, conf=0.25)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0].cpu().numpy()
                c = box.cls.cpu().numpy()
                conf = box.conf.cpu().numpy()
                
                detections.append({
                    "bbox": b.tolist(),
                    "class": int(c.item()),
                    "class_name": self.class_names[int(c.item())],
                    "confidence": float(conf.item())
                })
                
        return detections

# 모델 인스턴스 생성
model = FoodDetectionModel("./best.pt")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 이미지 읽기
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # 예측 수행
    detections = model.predict(image)
    
    return {
        "status": "success",
        "detections": detections
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)