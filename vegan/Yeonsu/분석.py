import streamlit as st
import pandas as pd
import datetime
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="영양소 분석 & 식단 관리", layout="wide")

# 경고 무시 설정
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# 데이터 로드 함수
@st.cache_data
def load_meal_data(file_path):
    """CSV 데이터 로드 및 캐싱"""
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Meal", "Food", "Quantity", "Unit", "Calories", "Protein", "Carbs", "Fat", "Iron"])
    return df

# 데이터 저장 함수
def save_meal_data(df, file_path):
    """CSV 데이터 저장"""
    df.to_csv(file_path, index=False)

class NutrientAnalyzer:
    def analyze_food(self, image):
        """이미지에서 음식 감지"""
        return [("샐러드", 0.95), ("닭가슴살", 0.85)]

    def show(self):
        """영양소 분석기 UI"""
        st.subheader("🥗 음식 영양소 분석기")
        st.write("사진을 업로드하거나 카메라로 찍은 이미지를 분석합니다.")

        input_method = st.radio("이미지 입력 방식 선택", ["파일 업로드", "카메라 촬영"])

        image = None
        if input_method == "파일 업로드":
            uploaded_file = st.file_uploader("음식 사진을 업로드하세요", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
        elif input_method == "카메라 촬영":
            image = st.camera_input("카메라로 사진을 찍어 업로드하세요")

        if image is not None:
            st.image(image, caption="입력된 이미지", use_column_width=True)
            st.write("🔍 음식 분석 중...")

            detected_foods = self.analyze_food(image)

            st.write("**📋 탐지된 음식:**")
            for food, confidence in detected_foods:
                st.write(f"- {food}: {confidence * 100:.1f}% 확률")

            # 음식 양을 입력할 수 있도록 추가
            food_name = st.selectbox("음식명", [food for food, _ in detected_foods])
            quantity = st.number_input("양 (그램 단위)", min_value=1, value=100, step=1)

            if food_name and quantity:
                nutrition = self.calculate_nutrition(food_name, quantity)
                if nutrition:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("열량", f"{nutrition['Calories']} kcal")
                    col2.metric("단백질", f"{nutrition['Protein']} g")
                    col3.metric("탄수화물", f"{nutrition['Carbs']} g")
                    col4.metric("지방", f"{nutrition['Fat']} g")
                    col5.metric("철분", f"{nutrition['Iron']} mg")
                else:
                    st.error("영양소 정보를 찾을 수 없습니다.")

    def calculate_nutrition(self, food_name, quantity):
        # 기본 영양소 데이터 (지방 포함, 철분 포함)
        nutrition_data = {
            '샐러드': {'Calories': 15, 'Protein': 1.5, 'Carbs': 2.0, 'Fat': 0.2, 'Iron': 0.8},
            '닭가슴살': {'Calories': 165, 'Protein': 31, 'Carbs': 0, 'Fat': 3.6, 'Iron': 1.2},
            '연어': {'Calories': 208, 'Protein': 22, 'Carbs': 0, 'Fat': 13, 'Iron': 0.5},
            '사과': {'Calories': 52, 'Protein': 0.3, 'Carbs': 14, 'Fat': 0.2, 'Iron': 0.1},
            '바나나': {'Calories': 89, 'Protein': 1.1, 'Carbs': 23, 'Fat': 0.3, 'Iron': 0.3},
            '우유': {'Calories': 42, 'Protein': 3.4, 'Carbs': 5, 'Fat': 1, 'Iron': 0.1},
            '요구르트': {'Calories': 59, 'Protein': 3.6, 'Carbs': 5, 'Fat': 3.3, 'Iron': 0.1},
            '고구마': {'Calories': 130, 'Protein': 1.5, 'Carbs': 30, 'Fat': 0.1, 'Iron': 0.7},
            '감자': {'Calories': 76, 'Protein': 2.0, 'Carbs': 17, 'Fat': 0.1, 'Iron': 0.6},
            '두부': {'Calories': 76, 'Protein': 8.1, 'Carbs': 1.9, 'Fat': 4.8, 'Iron': 2.7},
            '돼지고기': {'Calories': 242, 'Protein': 27, 'Carbs': 0, 'Fat': 15, 'Iron': 2.5},
            '소고기': {'Calories': 250, 'Protein': 26, 'Carbs': 0, 'Fat': 15, 'Iron': 2.5}
        }
        
        if food_name in nutrition_data:
            food_data = nutrition_data[food_name]
            multiplier = quantity / 100  # 100g 기준으로 계산
            return {
                "Calories": food_data['Calories'] * multiplier,
                "Protein": food_data['Protein'] * multiplier,
                "Carbs": food_data['Carbs'] * multiplier,
                "Fat": food_data['Fat'] * multiplier,
                "Iron": food_data['Iron'] * multiplier
            }
        return None

class CalendarApp:
    default_nutrition_data = {
        'Food': [
            '밥', '김치', '계란', '닭가슴살', '연어', 
            '사과', '바나나', '우유', '요구르트', '샐러드',
            '고구마', '감자', '두부', '돼지고기', '소고기'
        ],
        'Calories': [
            130, 15, 68, 165, 208,
            52, 89, 42, 59, 15,
            130, 76, 76, 242, 250
        ],
        'Protein': [
            2.4, 1.5, 5.5, 31, 22,
            0.3, 1.1, 3.4, 3.6, 1.5,
            1.5, 2.0, 8.1, 27, 26
        ],
        'Carbs': [
            28, 2.0, 0.6, 0, 0,
            14, 23, 5, 5, 2.9,
            30, 17, 1.9, 0, 0
        ],
        'Fat': [
            0.3, 0.2, 4.7, 3.6, 13,
            0.2, 0.3, 1, 3.3, 0.2,
            0.1, 0.1, 4.8, 15, 15
        ],
        'Iron': [
            0.2, 0.0, 1.0, 1.2, 0.5, 0.5, 0.6, 0.1, 0.1, 0.8, 0.4, 0.5, 0.7, 2.7, 2.5
        ]
    }

    def __init__(self):
        self.data_file = "meal_data.csv"
        self.df = load_meal_data(self.data_file)
        self.nutrition_df = pd.DataFrame(self.default_nutrition_data)
        self.available_foods = sorted(self.nutrition_df['Food'].unique())

    def show_meal_input(self):
        """식단 입력 UI"""
        st.subheader("🍽️ 식단 입력")

        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜 선택", datetime.date.today())
            meal_type = st.selectbox("식사 종류", ["아침", "점심", "저녁", "간식"])

        with col2:
            food_name = st.selectbox("음식명", self.available_foods)
            quantity = st.number_input("양", min_value=0.0, value=100.0, step=10.0)
            unit = st.selectbox("단위", ["g", "ml"])

        if st.button("식단 저장"):
            if food_name and quantity > 0:
                nutrition = self.calculate_nutrition(food_name, quantity)
                if nutrition:
                    new_data = {
                        "Date": [date],
                        "Meal": [meal_type],
                        "Food": [food_name],
                        "Quantity": [quantity],
                        "Unit": [unit],
                        "Calories": [nutrition['Calories']],
                        "Protein": [nutrition['Protein']],
                        "Carbs": [nutrition['Carbs']],
                        "Fat": [nutrition['Fat']],
                        "Iron": [nutrition['Iron']]
                    }
                    self.df = pd.concat([self.df, pd.DataFrame(new_data)], ignore_index=True)
                    save_meal_data(self.df, self.data_file)
                    st.success("식단이 저장되었습니다!")
                else:
                    st.error("영양소 정보를 찾을 수 없습니다.")
            else:
                st.error("올바른 음식명과 양을 입력해주세요.")

    def calculate_nutrition(self, food_name, quantity):
        if food_name in self.nutrition_df['Food'].values:
            food_data = self.nutrition_df[self.nutrition_df['Food'] == food_name].iloc[0]
            multiplier = quantity / 100
            return {
                "Calories": food_data['Calories'] * multiplier,
                "Protein": food_data['Protein'] * multiplier,
                "Carbs": food_data['Carbs'] * multiplier,
                "Fat": food_data['Fat'] * multiplier,
                "Iron": food_data['Iron'] * multiplier
            }
        return None

    def show_nutrient_stats(self):
        """주간 영양소 통계 시각화"""
        st.subheader("📊 주간 영양소 분석")

        if not self.df.empty:
            # 최근 7일간 데이터 필터링
            start_date = datetime.datetime.today() - datetime.timedelta(days=7)
            filtered_df = self.df[self.df['Date'] >= start_date]

            if not filtered_df.empty:
                # 일별 합계 계산
                daily_summary = filtered_df.groupby(filtered_df['Date'].dt.date).sum(numeric_only=True)

                # 영양소 그래프
                st.line_chart(daily_summary[['Calories', 'Protein', 'Carbs', 'Fat', 'Iron']])

                # 평균 섭취량 표시
                st.write("📈 평균 섭취량:")
                cols = st.columns(5)
                cols[0].metric("칼로리", f"{daily_summary['Calories'].mean():.1f} kcal")
                cols[1].metric("단백질", f"{daily_summary['Protein'].mean():.1f} g")
                cols[2].metric("탄수화물", f"{daily_summary['Carbs'].mean():.1f} g")
                cols[3].metric("지방", f"{daily_summary['Fat'].mean():.1f} g")
                cols[4].metric("철분", f"{daily_summary['Iron'].mean():.1f} mg")
            else:
                st.warning("최근 7일간의 데이터가 없습니다.")
        else:
            st.warning("저장된 식단 데이터가 없습니다.")

# 메인 함수
def main():
    st.title("🍽️ 영양소 분석 & 식단 관리 시스템")

    st.sidebar.markdown("### 메뉴 선택")
    menus = {
        "음식 영양소 분석": "🥗",
        "식단 입력": "📝",
        "주간 분석": "📊"
    }

    if 'current_menu' not in st.session_state:
        st.session_state.current_menu = "음식 영양소 분석"

    for menu, icon in menus.items():
        if st.sidebar.button(f"{icon} {menu}"):
            st.session_state.current_menu = menu

    analyzer = NutrientAnalyzer()
    app = CalendarApp()

    if st.session_state.current_menu == "음식 영양소 분석":
        analyzer.show()
    elif st.session_state.current_menu == "식단 입력":
        app.show_meal_input()
    elif st.session_state.current_menu == "주간 분석":
        app.show_nutrient_stats()

if __name__ == "__main__":
    main()
