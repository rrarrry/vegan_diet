import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import datetime

class Dashboard: 
    def __init__(self, nutrition_df=None):
        if nutrition_df is None:
            # 내부에서 FDDB.xlsx 로드
            try:
                df = pd.read_excel("FDDB.xlsx")
                df = df.set_index("식품명")
                self.nutrition_df = df
            except Exception as e:
                st.error(f"FDDB.xlsx 로드 오류: {e}")
                self.nutrition_df = pd.DataFrame()
        else:
            self.nutrition_df = nutrition_df
        
        self.set_font()

         # 식단/섭취 기록을 저장할 DataFrame을 초기화 (혹은 st.session_state 등에서 가져오기)
        if "meal_data" in st.session_state and not st.session_state["detected_foods"].empty:
            # 예: meal_data에서 date, protein, calcium, iron 등이 존재한다고 가정
            self.data = st.session_state["detected_foods"].copy()
        else:
            self.data = pd.DataFrame(columns=['date','protein','calcium','iron','meals'])

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

    def get_nutritional_info(self, detected_foods):
        """
        대시보드에서도 영양소 계산 가능하도록 동일 로직.
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

        for food, _ in detected_foods:
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
    
    def nutrient_analysis(self):
        st.subheader("📊 주간 영양소 분석")
        st.write("영양소 목표 달성률 및 섭취량 시각화")

        # 1) BMI 기반 데이터 로드
        bmi_data = st.session_state.get("bmi_data", {})
        detected_foods = st.session_state.get("detected_foods", [])

        if not detected_foods:
            st.warning("아직 음식 분석 결과가 없습니다. 먼저 음식 이미지를 업로드하세요.")
            return


        # 2) 대시보드 측에서 영양소 재계산
        nutrient_info = self.get_nutritional_info(detected_foods)

        if not nutrient_info:
            st.warning("아직 세션에 영양소 정보가 저장되지 않았습니다.")
            return  # 바로 함수 종료

        # 2) 실제 분석 결과: 사용자가 섭취한 영양소 양
        actual_calories = nutrient_info.get("열량", {"value": 0})["value"]
        actual_protein  = nutrient_info.get("단백질", {"value": 0})["value"]
        actual_calcium  = nutrient_info.get("칼슘", {"value": 0})["value"]
        actual_iron     = nutrient_info.get("철", {"value": 0})["value"]

        
        # 3) 일일권장섭취량(RDA) 또는 목표치(예시 값)
        rda_calories = 2000     # kcal
        rda_protein  = 60       # g
        rda_calcium  = 1000     # mg
        rda_iron     = 15       # mg

        # 4) 시각화에 필요한 % 계산 (예: 실제 섭취량 / RDA * 100)
        pct_calories = (actual_calories / rda_calories * 100) if rda_calories else 0
        pct_protein  = (actual_protein / rda_protein * 100)  if rda_protein else 0
        pct_calcium  = (actual_calcium / rda_calcium * 100) if rda_calcium else 0
        pct_iron     = (actual_iron / rda_iron * 100)       if rda_iron else 0
        
        # 5. UI용 딕셔너리 구성
        #    - "칼로리"는 그대로 kcal 출력
        #    - 나머지 3개는 %로 표시
        nutrient_data = {
            "칼로리": actual_calories,  # 정수 or 소수 표시
            "단백질": pct_protein,
            "칼슘": pct_calcium,
            "철분": pct_iron
        }

        # 6. 4개의 열을 생성하여 각각 시각화
        cols = st.columns(4)
        for i, (nutrient, value) in enumerate(nutrient_data.items()):
            with cols[i]:
                if nutrient == "칼로리":
                    st.markdown(f"<div style='text-align: center; font-size: 26px; font-weight: bold;'>{value:.0f} kcal</div>", unsafe_allow_html=True)
                else:
                    pct_value = min(100, value)  # 100% 초과 방지
                    st.markdown(
                        f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{nutrient}</div>",
                        unsafe_allow_html=True
                    )
                    st.progress(int(pct_value))  # Streamlit progress()는 정수만
                    st.markdown(
                        f"<div style='text-align: center; font-size: 18px;'>{pct_value:.1f}%</div>",
                        unsafe_allow_html=True
                    )
                    
                    # 도넛 차트
                    fig, ax = plt.subplots(figsize=(3, 3))
                    ax.pie(
                        [pct_value, 100 - pct_value],
                        labels=[nutrient, "남은량"],
                        autopct='%1.1f%%',
                        startangle=90,
                        wedgeprops={'edgecolor': 'white'}
                    )
                    centre_circle = plt.Circle((0,0), 0.70, fc='white')
                    fig.gca().add_artist(centre_circle)
                    plt.axis('equal')
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

    def show_dashboard(self):
        st.title("📊 대시보드")
        self.nutrient_analysis()  # 추가하여 상단에 출력되도록 조정
        self.plot_weekly_trend()
        self.meal_calendar()

# Streamlit 인터페이스
if __name__ == "__main__":
    if "detected_foods" not in st.session_state:
        st.session_state["detected_foods"] = []  # 빈 리스트로 초기화

    dashboard_instance = Dashboard()
    dashboard_instance.show_dashboard()