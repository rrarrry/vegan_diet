import requests
import json
from pathlib import Path

def test_food_detection(image_path):
    # API 엔드포인트 URL
    url = "http://127.0.0.1:8000/predict"
    
    # 이미지 파일 열기
    with open(image_path, "rb") as image_file:
        files = {"file": (Path(image_path).name, image_file, "image/jpeg")}
        
        try:
            # API 호출
            response = requests.post(url, files=files, timeout=10)

            if response.status_code == 200:
                result = response.json()
                
                # 감지된 음식이 있는 경우 출력
                if "detections" in result and result["detections"]:
                    print("\n=== 감지된 음식 ===")
                    for detection in result["detections"]:
                        class_name = detection.get('class_name', '알 수 없음')
                        confidence = detection.get('confidence', 0.0)
                        print(f"음식명: {class_name}")
                        print(f"신뢰도: {confidence:.2f}")
                        print("-" * 20)
                else:
                    print("\n❌ 음식이 감지되지 않았습니다.")

            else:
                print(f"⚠️ 서버 오류 발생: {response.status_code}")
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 실패: {e}")
            print("서버가 실행 중인지 확인하세요.")

if __name__ == "__main__":
    # 테스트할 이미지 경로
    image_path = "C:/Users/Admin/Documents/GitHub/vegan_diet/vegan/Sungyong/api/testimage.jpg"
    
    # 테스트 실행
    test_food_detection(image_path)
