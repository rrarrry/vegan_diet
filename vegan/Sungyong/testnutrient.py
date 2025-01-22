import streamlit as st
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image
import io

class Nutrient:
    def __init__(self, model_path="yolov8x.pt", nutrition_data_path="nutrition_data.csv"):
        """
        Nutrient 클래스 생성자
        :param model_path: YOLO 모델 경로
        :param nutrition_data_path: 영양소 데이터 CSV 파일 경로
        """
        self.model = YOLO(model_path)
        self.nutrition_df = pd.read_csv(nutrition_data_path).set_index("Food")

    def analyze_food(self, image):
        """
        업로드된 음식 이미지를 분석하여 탐지된 음식 항목 및 확률 반환
        :param image: PIL 이미지 객체
        :return: 탐지된 음식 목록 [(음식명, 확률)]
        """
        img_array = np.array(image)
        results = self.model.predict(img_array)

        detected_items = []
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls)
                class_name = self.model.names[class_id]
                confidence = box.conf.item()
                detected_items.append((class_name, confidence))

        return detected_items

    def get_nutritional_info(self, detected_items):
        """
        탐지된 음식의 영양소 정보를 추출
        :param detected_items: 탐지된 음식 목록 [(음식명, 확률)]
        :return: 영양소 요약 데이터
        """
        nutrient_summary = {
            "Calories": 0,
            "Protein": 0,
            "Carbs": 0,
            "Fat": 0
        }

        for food, _ in detected_items:
            if food in self.nutrition_df.index:
                nutrient_summary["Calories"] += self.nutrition_df.loc[food]["Calories"]
                nutrient_summary["Protein"] += self.nutrition_df.loc[food]["Protein"]
                nutrient_summary["Carbs"] += self.nutrition_df.loc[food]["Carbs"]
                nutrient_summary["Fat"] += self.nutrition_df.loc[food]["Fat"]

        return nutrient_summary

    def show(self):
        """스트림릿 페이지 UI 구성 및 음식 분석"""
        st.title("🥗 음식 영양소 분석기")
        st.subheader("사진을 업로드하면 음식의 영양소 정보를 분석합니다.")

        uploaded_file = st.file_uploader("음식 사진을 업로드하세요", type=["jpg", "png", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 이미지", use_column_width=True)

            # 음식 분석
            st.write("🔍 음식 분석 중...")
            detected_items = self.analyze_food(image)

            if detected_items:
                st.write("**📋 탐지된 음식:**")
                for food, confidence in detected_items:
                    st.write(f"- {food}: {confidence:.2f} 확률")

                # 영양소 정보 출력
                st.write("📊 **예상 영양소 정보:**")
                nutrient_info = self.get_nutritional_info(detected_items)

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Calories", f"{nutrient_info['Calories']} kcal")
                col2.metric("Protein", f"{nutrient_info['Protein']} g")
                col3.metric("Carbs", f"{nutrient_info['Carbs']} g")
                col4.metric("Fat", f"{nutrient_info['Fat']} g")

            else:
                st.error("❌ 음식이 감지되지 않았습니다. 다시 시도해 주세요.")
