import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bmi import BmiRdaCalculator
from camera import Nutrient
from dashboard import Dashboard

if "detected_foods" not in st.session_state:
    st.session_state["detected_foods"] = []  # 빈 리스트로 초기화


# 사이드바 네비게이션
def show_sidebar_navigation():  
    """사이드바 네비게이션"""
    st.sidebar.title("메뉴")
    # 섹션 이동 버튼
    if st.sidebar.button("🏢 BMI 계산"):
        st.session_state["section"] = "BMI 계산"
    if st.sidebar.button("🤖영양소 분석"):
        st.session_state["section"] = "영양소 분석"
    if st.sidebar.button("📈대시 보드"):
        st.session_state["section"] = "대시 보드"
    #if st.sidebar.button("📅 월별 식단"):
    #   st.session_state["section"] = "월별 식단"
    #if st.sidebar.button("🔍 메뉴 추천"):
    #    st.session_state["section"] = "메뉴 추천"    

# 메인 실행 함수
def main():
    # Streamlit 앱
    #t.set_page_config(page_title="비건 영양소 대시보드", layout="wide")     # 화면 상단 메인 타이틀
    st.title("🥗 Veggie Bites")          # 화면 상단 메인 타이틀
    
    # 기본 섹션 설정
    if "section" not in st.session_state:
        st.session_state["section"] = "BMI 계산"

    # 사이드바 네비게이션
    show_sidebar_navigation()

    # 입력 값 유지 및 공유를 위한 세션 상태 설정
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = {
            "gender": "남성",
            "age": 30,
            "height_cm": 175,
            "weight_kg": 70,
            "is_pregnant": False
        }

    # 현재 활성화된 섹션에 따라 해당 함수 호출
    if st.session_state.get("section", "BMI 계산") == "BMI 계산":
        # 입력 없이 바로 BMI 계산 클래스를 호출
        bmi_calculator = BmiRdaCalculator(**st.session_state["user_data"])
        bmi_calculator.show()
    elif st.session_state["section"] == "영양소 분석":     
        nutrient_instance = Nutrient()
        nutrient_instance.show()  # 인스턴스를 통해 메서드 호출        # class를 만들고 class 호출 후 보여주는 코드
    elif st.session_state["section"] == "대시 보드":
        detected_foods = st.session_state.get("detected_foods", [])       
        dashboard_instance = Dashboard()
        dashboard_instance.show_dashboard()
    #elif st.session_state["section"] == "월별 식단":       # 달력형식으로 그날 무엇을 먹었는지 기록하는 함수
    #    meal_calendar.show()
    #elif st.session_state["section"] == "메뉴 추천":       # 기타 비건식 추천?? 만들면 좋을듯 
    #    recommend_menu.show()  

# 앱 실행
if __name__ == "__main__":
    main()