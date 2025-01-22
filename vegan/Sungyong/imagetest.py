import requests
import json
from pathlib import Path

def test_food_detection(image_path):
    # API 엔드포인트 URL
    url = "http://127.0.0.1:8000/predict"
    
    # 이미지 파일 열기
    with open(image_path, "rb") as image_file:
        # 멀티파트 폼 데이터로 파일 전송
        files = {"file": (Path(image_path).name, image_file, "image/jpeg")}
        
        # API 호출
        response = requests.post(url, files=files)
        
    # 응답 확인
    if response.status_code == 200:
        result = response.json()
        print("\n=== 감지된 음식 ===")
        for detection in result["detections"]:
            print(f"음식명: {detection['class_name']}")
            print(f"신뢰도: {detection['confidence']:.2f}")
            print("-" * 20)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # 테스트할 이미지 경로
    image_path = "C:/Users/Admin/Documents/GitHub/vegan_diet/vegan/Sungyong/api/testimage.jpg"  # 실제 이미지 경로로 수정하세요
    test_food_detection(image_path)