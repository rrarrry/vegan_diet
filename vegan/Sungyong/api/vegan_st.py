import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from inbody import InBody
from nutrient import Nutrient
#from diet import Diet
#from meal_calendar import MealCalendar
#from recommend_menu import RecommendMenu


# 사이드바 네비게이션
def show_sidebar_navigation():  
    """사이드바 네비게이션"""
    st.sidebar.title("메뉴")
    # 섹션 이동 버튼
    if st.sidebar.button("🏢 영양소 분석"):
        st.session_state["section"] = "영양소 분석"
    if st.sidebar.button("📈신체 분석"):
        st.session_state["section"] = "신체 분석"
    if st.sidebar.button("🤖 식단 조언"):
        st.session_state["section"] = "식단 조언"
    if st.sidebar.button("📅 월별 식단"):
        st.session_state["section"] = "월별 식단"
    if st.sidebar.button("🔍 메뉴 추천"):
        st.session_state["section"] = "메뉴 추천"    

# 메인 실행 함수
def main():
    # Streamlit 앱
    st.set_page_config(page_title="비건 영양소 대시보드", layout="wide")     # 화면 상단 메인 타이틀
    st.title("🥗비건 영양소 대시보드")          # 화면 상단 메인 타이틀
    
    # 사이드바 네비게이션
    show_sidebar_navigation()

    # 현재 활성화된 섹션에 따라 해당 함수 호출
    if st.session_state.get("section", "영양소 분석") == "영양소 분석":
        nutrient_instance = Nutrient()
        nutrient_instance.show()  # 인스턴스를 통해 메서드 호출
    elif st.session_state["section"] == "신체 분석":     
        InBody.show()        # class를 만들고 class 호출 후 보여주는 코드
    #elif st.session_state["section"] == "식단 조언":       # 최종? 조언해주는 창
    #    diet.show()
    #elif st.session_state["section"] == "월별 식단":       # 달력형식으로 그날 무엇을 먹었는지 기록하는 함수
    #    meal_calendar.show()
    #elif st.session_state["section"] == "메뉴 추천":       # 기타 비건식 추천?? 만들면 좋을듯 
    #    recommend_menu.show()  

# 앱 실행
if __name__ == "__main__":
    main()