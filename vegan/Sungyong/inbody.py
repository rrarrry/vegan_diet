import streamlit as st
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image


class InBody:
    def __init__(self, gender=None, weight=None, height=None, age=None, activity_level=None):
        self.gender = gender
        self.weight = weight  # kg 단위
        self.height = height  # cm 단위
        self.age = age
        self.activity_level = activity_level

    def calculate_bmi(self):
        """BMI 계산"""
        height_m = self.height / 100  # cm -> m 변환
        bmi = self.weight / (height_m ** 2)
        return round(bmi, 2)

    def interpret_bmi(self):
        """BMI 해석"""
        bmi = self.calculate_bmi()
        if self.gender == "여성":
            if bmi < 18.5:
                return "저체중입니다."
            elif 18.5 <= bmi < 24.9:
                return "정상 체중입니다."
            elif 25 <= bmi < 29.9:
                return "과체중입니다."
            else:
                return "비만입니다."
        else:
            if bmi < 18.5:
                return "저체중입니다."
            elif 18.5 <= bmi < 24.9:
                return "정상 체중입니다."
            elif 25 <= bmi < 29.9:
                return "과체중입니다."
            else:
                return "비만입니다."

    def get_nutrient_recommendations(self):
        """하루 권장 영양소 섭취량 계산"""
        base_calories = 2000 if self.gender == "남성" else 1800
        protein_ratio = 1.0 if self.gender == "남성" else 0.8

        # 활동 수준에 따른 보정
        activity_multiplier = {
            "low": 1.2,
            "moderate": 1.5,
            "high": 1.8
        }

        calorie_needs = base_calories * activity_multiplier[self.activity_level]
        protein_needs = self.weight * protein_ratio
        carbs_needs = calorie_needs * 0.5 / 4  # 50% 탄수화물, 4kcal/g
        fat_needs = calorie_needs * 0.3 / 9  # 30% 지방, 9kcal/g

        return {
            "칼로리": f"{calorie_needs:.0f} kcal",
            "단백질": f"{protein_needs:.1f} g",
            "탄수화물": f"{carbs_needs:.1f} g",
            "지방": f"{fat_needs:.1f} g"
        }

    @staticmethod
    def show():
        """스트림릿을 통한 신체 분석 인터페이스"""
        st.subheader("📈 신체 분석")

        gender = st.radio("성별을 선택하세요", ("여성", "남성"))
        height = st.number_input("키 (cm 단위)", min_value=100, max_value=250, value=170)
        weight = st.number_input("몸무게 (kg 단위)", min_value=30, max_value=200, value=70)
        age = st.number_input("나이 (세)", min_value=1, max_value=100, value=25)
        activity_level = st.selectbox("활동 수준", ["low", "moderate", "high"])

        if st.button("BMI 및 영양소 분석"):
            inbody_instance = InBody(gender, weight, height, age, activity_level)

            # BMI 계산 및 출력
            bmi = inbody_instance.calculate_bmi()
            interpretation = inbody_instance.interpret_bmi()
            st.write(f"당신의 BMI는 **{bmi:.2f}** 입니다.")
            st.write(f"체중 상태: **{interpretation}**")

            # 영양소 권장량 출력
            st.subheader("📊 하루 권장 영양소 섭취량")
            recommendations = inbody_instance.get_nutrient_recommendations()

            for nutrient, value in recommendations.items():
                st.write(f"- {nutrient}: {value}")

if __name__ == "__main__":
    InBody.show()
