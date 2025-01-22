import streamlit as st
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image
import io

class InBody:
    def __init__(self, gender, weight, height, age, activity_level="moderate"):
        """
        사용자 정보를 입력받아 개인별 맞춤 영양소 필요량을 계산.
        
        Parameters:
        - gender (str): 성별 ('male', 'female')
        - weight (float): 몸무게 (kg)
        - height (float): 신장 (cm)
        - age (int): 나이 (세)
        - activity_level (str): 활동 수준 ('low', 'moderate', 'high')
        """
        self.gender = gender.lower()
        self.weight = weight
        self.height = height
        self.age = age
        self.activity_level = activity_level.lower()
        
        # 활동 수준에 따른 계수 (운동량이 많을수록 높아짐)
        self.activity_factors = {
            "low": 1.2,         # 비활동적 (앉아서 생활)
            "moderate": 1.55,   # 적당한 활동 (일반적인 운동량)
            "high": 1.9         # 매우 활동적 (운동이 많은 사람)
        }

    def calculate_bmr(self):
        """ Mifflin-St Jeor 공식에 기반한 기초대사량(BMR) 계산 """
        if self.gender == "male":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        elif self.gender == "female":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        else:
            raise ValueError("Invalid gender. Use 'male' or 'female'.")
        
        return bmr

    def calculate_daily_needs(self):
        """ 활동 수준을 고려한 총 에너지 필요량 계산 """
        bmr = self.calculate_bmr()
        tdee = bmr * self.activity_factors.get(self.activity_level, 1.55)
        return round(tdee, 2)

    def get_nutrient_recommendations(self):
        """
        칼로리 요구량을 바탕으로 3대 영양소(탄수화물, 단백질, 지방) 권장량 제공.
        
        비율 기준:
        - 탄수화물: 50-60%
        - 단백질: 15-25%
        - 지방: 20-30%
        """
        total_calories = self.calculate_daily_needs()

        # 탄수화물 50~60% (1g당 4kcal)
        carbs_min = round(total_calories * 0.50 / 4)
        carbs_max = round(total_calories * 0.60 / 4)

        # 단백질 15~25% (1g당 4kcal)
        protein_min = round(total_calories * 0.15 / 4)
        protein_max = round(total_calories * 0.25 / 4)

        # 지방 20~30% (1g당 9kcal)
        fat_min = round(total_calories * 0.20 / 9)
        fat_max = round(total_calories * 0.30 / 9)

        return {
            "Calories": f"{total_calories} kcal",
            "Carbs": f"{carbs_min}-{carbs_max} g",
            "Protein": f"{protein_min}-{protein_max} g",
            "Fat": f"{fat_min}-{fat_max} g"
        }

    def display_results(self):
        """ 사용자 맞춤 영양소 권장량 출력 """
        recommendations = self.get_nutrient_recommendations()
        print(f"권장 섭취 칼로리: {recommendations['Calories']}")
        print(f"탄수화물: {recommendations['Carbs']}")
        print(f"단백질: {recommendations['Protein']}")
        print(f"지방: {recommendations['Fat']}")

if __name__ == "__main__":
    show.inbody()