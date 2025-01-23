import streamlit as st
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image

class Nutrient:
    def __init__(self, model_path="best.pt", nutrition_data_path="FDDB.xlsx"):
        """
        Nutrient 클래스 생성자
        :param model_path: 학습된 YOLO 모델 경로
        :param nutrition_data_path: 영양소 데이터 Excel 파일 경로
        """
        try:
            self.model = YOLO(model_path)
            st.info("커스텀 학습 모델 로드 완료")
        except Exception as e:
            st.error(f"YOLO 모델 로드 실패: {e}")
            raise e

        try:
            self.nutrition_df = pd.read_excel(nutrition_data_path)
            # 불필요한 컬럼 매핑 제거, 원본 컬럼명 사용
            self.nutrition_df = self.nutrition_df.set_index('식품명')
            st.info("영양정보 데이터 로드 완료")
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

    def get_nutritional_info(self, detected_items):
        """
        탐지된 음식의 영양소 정보를 추출
        :param detected_items: 탐지된 음식 목록 [(음식명, 확률)]
        :return: 영양소 요약 데이터
        """
        nutrient_summary = {
            "영양성분함량기준량": {"value": "", "unit": ""},
            "열량": {"value": 0, "unit": "kcal"},
            "단백질": {"value": 0, "unit": "g"},
            "지방": {"value": 0, "unit": "g"},
            "탄수화물": {"value": 0, "unit": "g"},
            "칼슘": {"value": 0, "unit": "mg"},
            "철": {"value": 0, "unit": "mg"}
        }

        for food, _ in detected_items:
            if food in self.nutrition_df.index:
                row = self.nutrition_df.loc[food]
                nutrient_summary["영양성분함량기준량"]["value"] = str(row['영양성분함량기준량'])
                nutrient_summary["열량"]["value"] += float(row['에너지(kcal)']) if pd.notnull(row['에너지(kcal)']) else 0
                nutrient_summary["단백질"]["value"] += float(row['단백질(g)']) if pd.notnull(row['단백질(g)']) else 0
                nutrient_summary["지방"]["value"] += float(row['지방(g)']) if pd.notnull(row['지방(g)']) else 0
                nutrient_summary["탄수화물"]["value"] += float(row['탄수화물(g)']) if pd.notnull(row['탄수화물(g)']) else 0
                nutrient_summary["칼슘"]["value"] += float(row['칼슘(mg)']) if pd.notnull(row['칼슘(mg)']) else 0
                nutrient_summary["철"]["value"] += float(row['철(mg)']) if pd.notnull(row['철(mg)']) else 0

        return nutrient_summary

    def capture_from_camera(self):
        """카메라 캡처 함수는 원본과 동일"""
        # 기존 코드 유지
        ...

    def show(self):
        """스트림릿 페이지 UI 구성 및 음식 분석"""
        st.title("🍗 한식 영양소 분석기")
        st.subheader("사진을 업로드하면 한식의 영양소 정보를 분석합니다.")

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

                st.write("🔍 음식 분석 중...")
                detected_items = self.analyze_food(image)

                if detected_items:
                    st.write("**📋 탐지된 음식:**")
                    for food, confidence in detected_items:
                        st.write(f"- {food}: {confidence:.2f} 확률")

                    st.write("📊 **영양 성분 정보**")
                    nutrient_info = self.get_nutritional_info(detected_items)
                    
                    # 기준량 표시
                    st.write(f"기준량: {nutrient_info['영양성분함량기준량']['value']}")
                    
                    # 영양성분함량기준량을 제외한 나머지 영양소 정보를 테이블로 표시
                    nutrient_df = pd.DataFrame([
                        {"영양성분": name, "함량": f"{info['value']:.1f} {info['unit']}"} 
                        for name, info in nutrient_info.items()
                        if name != "영양성분함량기준량"
                    ])
                    
                    st.table(nutrient_df)
                    
                    # 영양소 분석 코멘트
                    st.write("💡 **영양소 분석**")
                    comments = []
                    if nutrient_info["단백질"]["value"] > 15:
                        comments.append("단백질이 풍부한 한식입니다.")
                    if nutrient_info["칼슘"]["value"] > 200:
                        comments.append("칼슘이 풍부하게 포함되어 있습니다.")
                    if nutrient_info["철"]["value"] > 2:
                        comments.append("철분이 풍부한 한식입니다.")
                    
                    if comments:
                        for comment in comments:
                            st.info(comment)
                else:
                    st.error("❌ 한식이 감지되지 않았습니다. 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"이미지 처리 중 오류 발생: {e}")

# Streamlit 앱 실행
if __name__ == "__main__":
    nutrient_app = Nutrient()
    nutrient_app.show()