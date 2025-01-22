import streamlit as st
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image

class Nutrient:
    def __init__(self, model_path="yolov8x.pt", nutrition_data_path="FDDB.xlsx"):
        """
        Nutrient 클래스 생성자
        :param model_path: YOLO 모델 경로
        :param nutrition_data_path: 영양소 데이터 Excel 파일 경로
        """
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            st.error(f"YOLO 모델 로드 실패: {e}")
            raise e

        try:
            # [수정된 부분 시작] - 엑셀 파일 읽기 및 컬럼 매핑 수정
            self.nutrition_df = pd.read_excel(nutrition_data_path)
            self.nutrition_df = self.nutrition_df.rename(columns={
                '식품명': 'Food',
                '에너지(kcal)': 'Calories',
                '단백질(g)': 'Protein',
                '탄수화물(g)': 'Carbs',
                '지방(g)': 'Fat',
                '칼슘(mg)': 'Calcium',
                '철분(mg)': 'Iron'
            })
            self.nutrition_df = self.nutrition_df.set_index('Food')
            # [수정된 부분 끝]
        except FileNotFoundError:
            st.error(f"Excel 파일이 '{nutrition_data_path}' 경로에 없습니다.")
            raise
        except Exception as e:
            st.error(f"Excel 파일 로드 중 오류 발생: {e}")
            raise

    def analyze_food(self, image):
        """
        업로드된 음식 이미지를 분석하여 탐지된 음식 항목 및 확률 반환
        :param image: PIL 이미지 객체
        :return: 탐지된 음식 목록 [(음식명, 확률)]
        """
        img_array = np.array(image)
        try:
            results = self.model.predict(img_array)

            detected_items = []
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls)
                    class_name = self.model.names[class_id]
                    confidence = box.conf.item()
                    detected_items.append((class_name, confidence))

            return detected_items
        except Exception as e:
            st.error(f"YOLO 예측 실패: {e}")
            return []

    # [수정된 부분 시작] - 영양소 정보 추출 함수 수정
    def get_nutritional_info(self, detected_items):
        """
        탐지된 음식의 영양소 정보를 추출
        :param detected_items: 탐지된 음식 목록 [(음식명, 확률)]
        :return: 영양소 요약 데이터
        """
        nutrient_summary = {
            "열량": {"value": 0, "unit": "kcal"},
            "단백질": {"value": 0, "unit": "g"},
            "탄수화물": {"value": 0, "unit": "g"},
            "지방": {"value": 0, "unit": "g"},
            "칼슘": {"value": 0, "unit": "mg"},
            "철분": {"value": 0, "unit": "mg"}
        }

        for food, _ in detected_items:
            if food in self.nutrition_df.index:
                nutrient_summary["열량"]["value"] += self.nutrition_df.loc[food]["Calories"]
                nutrient_summary["단백질"]["value"] += self.nutrition_df.loc[food]["Protein"]
                nutrient_summary["탄수화물"]["value"] += self.nutrition_df.loc[food]["Carbs"]
                nutrient_summary["지방"]["value"] += self.nutrition_df.loc[food]["Fat"]
                nutrient_summary["칼슘"]["value"] += self.nutrition_df.loc[food]["Calcium"]
                nutrient_summary["철분"]["value"] += self.nutrition_df.loc[food]["Iron"]

        return nutrient_summary
    # [수정된 부분 끝]

    def capture_from_camera(self):
        """
        카메라로부터 이미지를 캡처하는 함수
        :return: 캡처된 이미지 (PIL Image 객체) 또는 None
        """
        try:
            # 카메라 초기화
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("카메라를 열 수 없습니다.")
                return None

            # Streamlit에 카메라 미리보기 표시
            camera_placeholder = st.empty()
            capture_button = st.button("사진 촬영")

            while not capture_button:
                ret, frame = cap.read()
                if ret:
                    # BGR을 RGB로 변환
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    camera_placeholder.image(frame_rgb, channels="RGB", caption="카메라 미리보기")
                else:
                    st.error("프레임을 읽을 수 없습니다.")
                    break

            if capture_button:
                ret, frame = cap.read()
                if ret:
                    # BGR을 RGB로 변환하고 PIL Image로 변환
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    cap.release()
                    return image
                else:
                    st.error("이미지 캡처에 실패했습니다.")

            cap.release()
        except Exception as e:
            st.error(f"카메라 캡처 중 오류 발생: {e}")
            return None
        
        return None

    def show(self):
        """스트림릿 페이지 UI 구성 및 음식 분석"""
        st.title("🍗 음식 영양소 분석기")
        st.subheader("사진을 업로드하면 음식의 영양소 정보를 분석합니다.")

        input_method = st.radio("이미지 입력 방식 선택", ["파일 업로드", "카메라 촬영"])
        
        image = None
        if input_method == "파일 업로드":
            uploaded_file = st.file_uploader("음식 사진을 업로드하세요", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
        else:
            if st.button("카메라 켜기"):
                image = self.capture_from_camera()

        if image is not None:
            try:
                st.image(image, caption="입력된 이미지", use_column_width=True)

                # 음식 분석
                st.write("🔍 음식 분석 중...")
                detected_items = self.analyze_food(image)

                if detected_items:
                    st.write("**📋 탐지된 음식:**")
                    for food, confidence in detected_items:
                        st.write(f"- {food}: {confidence:.2f} 확률")

                    # [수정된 부분 시작] - 영양소 정보 출력 방식 변경
                    st.write("📊 **영양 성분 정보**")
                    st.write("기준량: 100ml/100g")
                    
                    nutrient_info = self.get_nutritional_info(detected_items)
                    
                    # 데이터프레임으로 변환하여 테이블 형식으로 표시
                    nutrient_df = pd.DataFrame([
                        {"영양성분": name, "함량": f"{info['value']:.1f} {info['unit']}"} 
                        for name, info in nutrient_info.items()
                    ])
                    
                    st.table(nutrient_df)
                    
                    # 영양소 분석 코멘트 추가
                    st.write("💡 **영양소 분석**")
                    comments = []
                    if nutrient_info["단백질"]["value"] > 15:
                        comments.append("단백질이 풍부한 식사입니다.")
                    if nutrient_info["칼슘"]["value"] > 200:
                        comments.append("칼슘이 풍부하게 포함되어 있습니다.")
                    if nutrient_info["철분"]["value"] > 2:
                        comments.append("철분이 풍부한 식사입니다.")
                    
                    if comments:
                        for comment in comments:
                            st.info(comment)
                    # [수정된 부분 끝]
                else:
                    st.error("❌ 음식이 감지되지 않았습니다. 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"이미지 처리 중 오류 발생: {e}")

# Streamlit 앱 실행
if __name__ == "__main__":
    nutrient_app = Nutrient()
    nutrient_app.show()