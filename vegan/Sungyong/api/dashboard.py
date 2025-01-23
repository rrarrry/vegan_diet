import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import calendar
import datetime



class Dashboard:
    def __init__(self):
        self.data = self.load_dummy_data()
        self.set_font()

    def set_font(self):
        plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 환경
        plt.rcParams['axes.unicode_minus'] = False
        st.markdown("""
    <style>
        .reportview-container {
            max-width: 900px;
            margin: auto;
        }
        .stTitle {
            font-size: 22px !important;
            font-weight: bold;
            text-align: center;
        }
        .stSubheader {
            font-size: 18px !important;
        }
        .stTextInput, .stButton, .stSelectbox, .stNumberInput, .stMarkdown {
            font-size: 14px !important;
        }
        </style>
        """, unsafe_allow_html=True)


    # def load_data(self):
    #     try:
    #         conn = sqlite3.connect(self.db_path)
    #         query = "SELECT date, protein, calcium, iron, meals FROM nutrition_records"
    #         df = pd.read_sql_query(query, conn)
    #         conn.close()
    #         return df
    #     except Exception as e:
    #         st.error(f"데이터베이스 로드 실패: {e}")
    #         return pd.DataFrame(columns=['date', 'protein', 'calcium', 'iron', 'meals'])
    def nutrient_analysis(self):
        st.subheader("📊 영양소 분석 결과")
        st.write("영양소 목표 달성률 및 섭취량 시각화")

         # 세션에서 값 가져오기 (기본값 설정)
        nutrition_data = st.session_state.get("nutrition_results", {
            "calories": 2000,
            "protein_rda": 75,
            "calcium_rda": 1000,
            "iron_rda": 18
        })

        nutrients = {
            "칼로리": nutrition_data["calories"],
            "단백질": nutrition_data["protein_rda"],
            "칼슘": nutrition_data["calcium_rda"],
            "철분": nutrition_data["iron_rda"]
        }

        cols = st.columns(4)
        for i, (nutrient, value) in enumerate(dummy_data.items()):
            with cols[i]:
                if nutrient == "칼로리":
                    st.markdown(f"<div style='text-align: center; font-size: 26px; font-weight: bold;'>{value} kcal</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{nutrient}</div>", unsafe_allow_html=True)
                    st.progress(value)
                    st.markdown(f"<div style='text-align: center; font-size: 18px;'>{value}%</div>", unsafe_allow_html=True)
                    
                    # 도넛 차트 생성
                    fig, ax = plt.subplots(figsize=(3, 3))
                    ax.pie([value, 100 - value], labels=[nutrient, "남은량"], autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
                    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                    fig.gca().add_artist(centre_circle)
                    plt.axis('equal')  # 비율 유지
                    st.pyplot(fig)
            

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
                    cols[i].markdown(" ")
                else:
                    date_str = f"{today.year}-{today.month:02d}-{day:02d}"
                    meal_entry = self.data[self.data['date'].dt.strftime('%Y-%m-%d') == date_str]

                    with cols[i]:
                        st.markdown(
                            f"<div style='font-size: 12px; padding: 5px; border: 1px solid #ddd; border-radius: 5px;'>",
                            unsafe_allow_html=True
                        )
                        if not meal_entry.empty:
                            meals = meal_entry.iloc[0]['meals']
                            protein = meal_entry.iloc[0]['protein']
                            calcium = meal_entry.iloc[0]['calcium']
                            iron = meal_entry.iloc[0]['iron']

                            st.markdown(
                                f"**{day}일**\\n{meals}\\n"
                                f"단백질: {protein:.1f}%\\n칼슘: {calcium:.1f}%\\n철분: {iron:.1f}%",
                                unsafe_allow_html=True
                            )   
                        else:
                            st.markdown(f"**{day}일**\\n(식단 없음)")
                        st.markdown("</div>", unsafe_allow_html=True)


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
        self.nutrient_analysis()  # 추가하여 상단에 출력되도록 조정
        self.plot_weekly_trend()
        self.meal_calendar()

# Streamlit 인터페이스
if __name__ == "__main__":
    dashboard_instance = Dashboard()
    dashboard_instance.show_dashboard()