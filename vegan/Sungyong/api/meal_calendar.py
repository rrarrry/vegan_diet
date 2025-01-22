import streamlit as st
import pandas as pd
import datetime
from streamlit_calendar import st_calendar

class CalendarApp:
    def __init__(self):
        # 스트림릿 앱 초기 설정
        
        self.calendar_options = {
            "editable": True,
            "selectable": True,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,listMonth",
            },
            "initialView": "dayGridMonth",
        }

        self.data_file = "meal_data.csv"
        self.init_data()

    def init_data(self):
        """ CSV 파일이 없으면 초기 생성 """
        try:
            self.df = pd.read_csv(self.data_file, parse_dates=["Date"])
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["Date", "Meal", "Calories", "Protein", "Carbs", "Fat"])
            self.df.to_csv(self.data_file, index=False)

    def save_meal(self, date, meal, calories, protein, carbs, fat):
        """ 식단 데이터를 CSV에 저장 """
        new_data = pd.DataFrame({
            "Date": [date],
            "Meal": [meal],
            "Calories": [calories],
            "Protein": [protein],
            "Carbs": [carbs],
            "Fat": [fat]
        })
        self.df = pd.concat([self.df, new_data], ignore_index=True)
        self.df.to_csv(self.data_file, index=False)
        st.success("식단이 저장되었습니다!")

    def show_meal_input(self):
        """ 식단 입력 UI """
        st.subheader("🍽️ 오늘의 식단 입력")

        date = st.date_input("날짜 선택", datetime.date.today())
        meal_type = st.selectbox("식사 종류", ["아침", "점심", "저녁", "간식"])
        calories = st.number_input("칼로리 (kcal)", min_value=0)
        protein = st.number_input("단백질 (g)", min_value=0)
        carbs = st.number_input("탄수화물 (g)", min_value=0)
        fat = st.number_input("지방 (g)", min_value=0)

        if st.button("식단 저장"):
            self.save_meal(date, meal_type, calories, protein, carbs, fat)

    def show_nutrient_stats(self):
        """ 주간 및 월간 영양소 통계 시각화 """
        st.subheader("📊 주간 및 월간 영양소 분석")

        if not self.df.empty:
            self.df["Date"] = pd.to_datetime(self.df["Date"])
            period = st.selectbox("조회 기간", ["최근 7일", "최근 30일"])
            days = 7 if period == "최근 7일" else 30

            filtered_df = self.df[self.df["Date"] >= (datetime.datetime.today() - pd.Timedelta(days=days))]

            if not filtered_df.empty:
                summary = filtered_df.groupby("Date").sum()[["Calories", "Protein", "Carbs", "Fat"]]
                st.line_chart(summary)
            else:
                st.warning("해당 기간의 데이터가 없습니다.")
        else:
            st.warning("저장된 식단 데이터가 없습니다.")

    def show_recommendations(self):
        """ 추천 식단 제공 """
        st.subheader("🔍 추천 식단")

        if not self.df.empty:
            avg_calories = self.df["Calories"].mean()
            avg_protein = self.df["Protein"].mean()
            avg_carbs = self.df["Carbs"].mean()
            avg_fat = self.df["Fat"].mean()

            st.write(f"📈 평균 칼로리 섭취: {avg_calories:.2f} kcal")
            st.write(f"💪 평균 단백질 섭취: {avg_protein:.2f} g")
            st.write(f"🍚 평균 탄수화물 섭취: {avg_carbs:.2f} g")
            st.write(f"🛢 평균 지방 섭취: {avg_fat:.2f} g")

            if avg_protein < 50:
                st.info("🥩 단백질이 부족합니다. 닭가슴살, 두부 등의 섭취를 추천합니다.")
            if avg_carbs < 200:
                st.info("🍞 탄수화물이 부족합니다. 현미밥, 고구마 등을 추천합니다.")
            if avg_fat < 50:
                st.info("🥑 지방이 부족합니다. 아보카도, 견과류 등을 추천합니다.")
        else:
            st.warning("식단 데이터를 입력한 후 추천을 받을 수 있습니다.")

    def render(self):
        """ 스트림릿 대시보드 구성 """
        st.title("📅 식단 및 영양소 분석 캘린더")

        menu = ["식단 입력", "주간 분석", "추천 메뉴"]
        choice = st.sidebar.radio("메뉴 선택", menu)

        if choice == "식단 입력":
            self.show_meal_input()
        elif choice == "주간 분석":
            self.show_nutrient_stats()
        elif choice == "추천 메뉴":
            self.show_recommendations()

def show():
    app = CalendarApp()
    app.render()

if __name__ == "__main__":
    show()
