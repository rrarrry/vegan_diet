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
        if "saved_meals" not in st.session_state or not isinstance(st.session_state["saved_meals"], pd.DataFrame):
            # 세션에 값이 없거나, 리스트인 경우 초기화
            st.session_state["saved_meals"] = pd.DataFrame(columns=['Date', 'Meal', 'Food', 'Quantity', 'Unit', 'Calories', 'Protein', 'Carbs', 'Fat', 'Iron', 'Calc'])
    
        if not st.session_state["saved_meals"].empty:
            self.data = st.session_state["saved_meals"].copy()
        else:
            self.data = pd.DataFrame(columns=['Date', 'Meal', 'Food', 'Quantity', 'Unit', 'Calories', 'Protein', 'Carbs', 'Fat', 'Iron', 'Calc'])

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

    def get_nutritional_info(self, saved_meals):
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

        # DataFrame의 각 행을 반복
        for _, row in saved_meals.iterrows():
            food = row["Food"]
            if food in self.nutrition_df.index:
                row_data = self.nutrition_df.loc[food]
                nutrient_summary["영양성분함량기준량"]["value"] = str(row_data['영양성분함량기준량'])
                nutrient_summary["열량"]["value"] += float(row_data['에너지(kcal)']) if pd.notnull(row_data['에너지(kcal)']) else 0
                nutrient_summary["단백질"]["value"] += float(row_data['단백질(g)']) if pd.notnull(row_data['단백질(g)']) else 0
                nutrient_summary["지방"]["value"] += float(row_data['지방(g)']) if pd.notnull(row_data['지방(g)']) else 0
                nutrient_summary["탄수화물"]["value"] += float(row_data['탄수화물(g)']) if pd.notnull(row_data['탄수화물(g)']) else 0
                nutrient_summary["칼슘"]["value"] += float(row_data['칼슘(mg)']) if pd.notnull(row_data['칼슘(mg)']) else 0
                nutrient_summary["철"]["value"] += float(row_data['철(mg)']) if pd.notnull(row_data['철(mg)']) else 0

        return nutrient_summary

    def nutrient_analysis(self):
        st.subheader("📊 주간 영양소 분석")
        st.write("영양소 목표 달성률 및 섭취량 시각화")

        # 1) BMI 기반 데이터 로드
        bmi_data = st.session_state.get("bmi_data", {})
        saved_meals = st.session_state.get("saved_meals", [])

        if saved_meals.empty:
            st.warning("아직 음식 분석 결과가 없습니다. 먼저 음식 이미지를 업로드하세요.")
            return


        # 2) 대시보드 측에서 영양소 재계산
        nutrient_info = self.get_nutritional_info(saved_meals)

        if not nutrient_info:
            st.warning("아직 세션에 영양소 정보가 저장되지 않았습니다.")
            return  # 바로 함수 종료

        # 2) 실제 분석 결과: 사용자가 섭취한 영양소 양
        actual_calories = nutrient_info.get("열량", {"value": 0})["value"]
        actual_protein  = nutrient_info.get("단백질", {"value": 0})["value"]
        actual_calcium  = nutrient_info.get("칼슘", {"value": 0})["value"]
        actual_iron     = nutrient_info.get("철", {"value": 0})["value"]

        
        # 3) 일일권장섭취량(RDA) 또는 목표치(예시 값)
        rda_calories = bmi_data.get("calories_rda", 2000)
        rda_protein  = bmi_data.get("protein_rda", 60)     # g
        rda_calcium  = bmi_data.get("calcium_rda", 1000)   # mg
        rda_iron     = bmi_data.get("iron_rda", 15)        # mg

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
                # 칼로리 또는 기타 정보 추가
                if nutrient == "칼로리":
                    st.markdown(
                        f"<div style='text-align: center; font-size: 26px; font-weight: bold;'>{value:.0f} kcal</div>",
                        unsafe_allow_html=True
                    )    
                    
                # 도넛 차트
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(
                    [pct_value, 100 - pct_value],
                    labels=[nutrient, "남은량"],
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=["#4CAF50", "#BDBDBD"],  # 초록색(섭취량), 회색(남은량)
                    wedgeprops={'edgecolor': 'white'}
                )
                centre_circle = plt.Circle((0,0), 0.70, fc='white')
                fig.gca().add_artist(centre_circle)
                plt.axis('equal')
                st.pyplot(fig)
                
    
    
    def show_weekly_analysis(self):
        st.subheader("📊 주간 영양소 분석")
        
        df = st.session_state['saved_meals']

        # 초기 세션 상태 설정
        if 'saved_meals' not in st.session_state:
            st.session_state['saved_meals'] = pd.DataFrame(columns=[
            "Date", "Meal", "Food", "Quantity", "Unit", "Calories", "Protein", "Carbs", "Fat", "Iron", "Calc"
            ])

        if df.empty:
            st.warning("저장된 식단 데이터가 없습니다. 먼저 데이터를 저장하세요.")
        else:
            # 최근 7일 데이터 필터링
            start_date = datetime.datetime.now() - datetime.timedelta(days=7)
            df['Date'] = pd.to_datetime(df['Date'])  # Ensure the 'Date' column is in datetime format
            filtered_df = df[df['Date'] >= start_date]

            if filtered_df.empty:
                st.warning("최근 7일간 저장된 데이터가 없습니다.")
            else:
                # 날짜별 영양소 합계 계산
                daily_summary = filtered_df.groupby(filtered_df['Date'].dt.date).sum(numeric_only=True)

                # 테이블 표시
                st.write("### 최근 7일간 식단 요약")
                st.dataframe(filtered_df)

                # 날짜별 요약 표시
                st.write("### 날짜별 영양소 합계")
                st.dataframe(daily_summary)

                # 영양소 별 시각화
                st.write("### 영양소 섭취 추세")
                st.line_chart(daily_summary[['Calories', 'Protein', 'Carbs', 'Fat', 'Iron']])


    def show_dashboard(self):
        st.title("📊 대시보드")
        self.nutrient_analysis()  # 추가하여 상단에 출력되도록 조정
        self.show_weekly_analysis()
        ## 세션 상태에서 저장된 식단 데이터를 가져오기
        if "saved_meals" in st.session_state and isinstance(st.session_state["saved_meals"], pd.DataFrame):
            if not st.session_state["saved_meals"].empty:
                meal_data = st.session_state["saved_meals"]
                st.write("📸 저장된 식단 목록:")
                st.dataframe(meal_data)
            else:
                st.warning("저장된 식단 데이터가 없습니다.")
        else:
            st.warning("저장된 식단 데이터가 없습니다.")

# Streamlit 인터페이스
if __name__ == "__main__":
    dashboard_instance = Dashboard()
    dashboard_instance.show_dashboard()