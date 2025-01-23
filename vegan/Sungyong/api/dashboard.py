import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import calendar
import datetime

class Dashboard:
    def __init__(self, db_path="nutrition.db"):
        self.db_path = db_path
        self.data = self.load_data()
        self.set_font()

    def set_font(self):
        plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 환경
        plt.rcParams['axes.unicode_minus'] = False

    def load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT date, protein, calcium, iron, meals FROM nutrition_records"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"데이터베이스 로드 실패: {e}")
            return pd.DataFrame(columns=['date', 'protein', 'calcium', 'iron', 'meals'])

    def plot_weekly_trend(self):
        st.subheader("주간 영양소 트렌드")
        fig, ax = plt.subplots()
        protein_goal, calcium_goal, iron_goal = 70, 1000, 25

        self.data['protein_percent'] = (self.data['protein'] / protein_goal) * 100
        self.data['calcium_percent'] = (self.data['calcium'] / calcium_goal) * 100
        self.data['iron_percent'] = (self.data['iron'] / iron_goal) * 100

        ax.plot(self.data['date'], self.data['protein_percent'], label='단백질 (%)', marker='o', linewidth=2)
        ax.plot(self.data['date'], self.data['calcium_percent'], label='칼슘 (%)', marker='o', linewidth=2)
        ax.plot(self.data['date'], self.data['iron_percent'], label='철분 (%)', marker='o', linewidth=2)

        ax.set_xlabel('날짜')
        ax.set_ylabel('섭취량 (%)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)

    def meal_calendar(self):
        st.subheader("📅 월간 식단 기록")
        today = datetime.date.today()
        month_days = calendar.monthcalendar(today.year, today.month)
        for week in month_days:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown("** **")
                else:
                    date_str = f"{today.year}-{today.month:02d}-{day:02d}"
                    meal_entry = self.data[self.data['date'] == date_str]
                    if not meal_entry.empty:
                        meals = meal_entry.iloc[0]['meals']
                        protein = meal_entry.iloc[0]['protein_percent']
                        calcium = meal_entry.iloc[0]['calcium_percent']
                        iron = meal_entry.iloc[0]['iron_percent']
                        cols[i].markdown(f"**{day}일**\n{meals}\n단백질: {protein:.1f}%\n칼슘: {calcium:.1f}%\n철분: {iron:.1f}%")
                        new_meal = cols[i].text_input(f"{day}일 식단", value=meals, key=f"meal_{day}")
                        if cols[i].button(f"수정 {day}일", key=f"edit_{day}"):
                            self.update_meal(date_str, new_meal)
                    else:
                        cols[i].markdown(f"**{day}일**\n(식단 없음)")
                        new_meal = cols[i].text_input(f"{day}일 식단", key=f"meal_{day}")
                        if cols[i].button(f"저장 {day}일", key=f"save_{day}"):
                            self.update_meal(date_str, new_meal)

    def update_meal(self, date, meal):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO nutrition_records (date, meals)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET meals=?
            """, (date, meal, meal))
            conn.commit()
            conn.close()
            st.success(f"{date}의 식단이 업데이트되었습니다.")
        except Exception as e:
            st.error(f"식단 업데이트 실패: {e}")

    def show_dashboard(self):
        st.title("📊 내 대시보드")
        self.plot_weekly_trend()
        self.meal_calendar()

# Streamlit 인터페이스
if __name__ == "__main__":
    dashboard_instance = Dashboard()
    dashboard_instance.show_dashboard()