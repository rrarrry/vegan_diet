import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bmi import BmiRdaCalculator
from camera import Nutrient
from dashboard import Dashboard


# 사이드바 네비게이션
def show_sidebar_navigation():  
    """사이드바 네비게이션"""
    st.sidebar.title("메뉴")
    # 섹션 이동 버튼
    if st.sidebar.button("🏢 BMI 계산"):
        st.session_state["section"] = "BMI 계산"
    if st.sidebar.button("📈영양소 분석"):
        st.session_state["section"] = "영양소 분석"
    if st.sidebar.button("🤖 대시 보드"):
        st.session_state["section"] = "대시 보드"
    #if st.sidebar.button("📅 월별 식단"):
    #   st.session_state["section"] = "월별 식단"
    #if st.sidebar.button("🔍 메뉴 추천"):
    #    st.session_state["section"] = "메뉴 추천"    

# 메인 실행 함수
def main():
    # Streamlit 앱
    st.set_page_config(page_title="비건 영양소 대시보드", layout="wide")     # 화면 상단 메인 타이틀
    st.title("🥗비건 영양소 대시보드")          # 화면 상단 메인 타이틀
    
    # 사이드바 네비게이션
    show_sidebar_navigation()

    # 현재 활성화된 섹션에 따라 해당 함수 호출
    # BMI 계산 섹션에서 사용자 입력을 받아 클래스 생성
    if st.session_state.get("section", "BMI 계산") == "BMI 계산":
        gender = st.selectbox("성별을 선택하세요", ["남성", "여성"])
        age = st.number_input("나이를 입력하세요", min_value=1, max_value=120)
        height_cm = st.number_input("키를 입력하세요 (cm)", min_value=50, max_value=250)
        weight_kg = st.number_input("몸무게를 입력하세요 (kg)", min_value=1, max_value=300)
        is_pregnant = st.checkbox("임신 여부 (해당 시 체크)")

        if st.button("결과 계산"):
            bmirdacalculator_instance = BmiRdaCalculator(gender, age, height_cm, weight_kg, is_pregnant)
            bmirdacalculator_instance.show()

    elif st.session_state["section"] == "영양소 분석":     
        inbody_instance = Nutrient()
        inbody_instance.show()  # 인스턴스를 통해 메서드 호출        # class를 만들고 class 호출 후 보여주는 코드
    elif st.session_state["section"] == "대시 보드":       
        dashboard_instance = Dashboard()
        dashboard_instance.show_dashboard()
    #elif st.session_state["section"] == "월별 식단":       # 달력형식으로 그날 무엇을 먹었는지 기록하는 함수
    #    meal_calendar.show()
    #elif st.session_state["section"] == "메뉴 추천":       # 기타 비건식 추천?? 만들면 좋을듯 
    #    recommend_menu.show()  

# 앱 실행
if __name__ == "__main__":
    main()