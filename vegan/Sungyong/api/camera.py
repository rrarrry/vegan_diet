import streamlit as st
st.set_page_config(page_title="비건 영양소 대시보드", layout="wide")  # 최상단으로 이동
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image
import warnings
import datetime
import google.generativeai as genai  # Gemini API




class Nutrient:
    def __init__(self, model_path="best.pt", nutrition_data_path="FDDB.xlsx"):
        """
        Nutrient 클래스 생성자
        """
        try:
            self.model = YOLO(model_path)
            st.info("커스텀 학습 모델 로드 완료")
        except Exception as e:
            st.error(f"초기화 오류: {e}")
            raise e

        try:
            self.nutrition_df = pd.read_excel(nutrition_data_path)
            # 불필요한 컬럼 매핑 제거, 원본 컬럼명 사용
            self.nutrition_df = self.nutrition_df.set_index('식품명')
            st.info("영양정보 데이터 로드 완료")
        except FileNotFoundError:
            st.error(f"Excel 파일이 '{nutrition_data_path}' 경로에 없습니다.")
            raise
        except Exception as e:
            st.error(f"Excel 파일 로드 중 오류 발생: {e}")
            raise
    
    def check_vegetarian(self, food_name):
        """
        LLM을 사용하여 음식이 채식 식단에 포함되는지 판별
        """
        try:
            question = f"Is {food_name} a vegetarian food?"
            model = genai.GenerativeModel("gemini-1.5-flash")  # GEMINI API 모델
            response = model.generate_content(question)  # 질문 생성 및 응답 받기

            if "yes" in response.text.lower():
                return True
            else:
                return False
        except Exception as e:
            st.error(f"채식 판별 중 오류 발생: {str(e)}")
            return None


    def analyze_food(self, image):
        """
        업로드된 음식 이미지를 분석하여 탐지된 음식 항목 및 확률 반환
        :param image: PIL 이미지 객체
        :return: 탐지된 음식 목록 [(음식명, 확률)]
        """
        img_array = np.array(image)
        try:
            results = self.model.predict(img_array)

            detected_foods = st.session_state.get("detected_foods", [])
                
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls)
                    class_name = self.model.names[class_id]
                    confidence = box.conf.item()
                    detected_foods.append((class_name, confidence))
                    
                    # 중복 데이터 방지
                    if (class_name, confidence) not in detected_foods:
                        detected_foods.append((class_name, confidence))

            # 세션 상태에 중복 없이 저장
            st.session_state["detected_foods"] = list(set(detected_foods))

            return detected_foods
        except Exception as e:
            st.error(f"분석 오류: {e}")
            return []

    def get_nutritional_info(self, detected_foods):
        """
        YOLO로 탐지된 음식들의 합산 영양소 정보를 반환
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

    def calculate_nutrition(self, food_name, quantity):
        """100g 기준 및 입력 양에 따른 영양정보 계산"""
        try:
            if food_name in self.nutrition_df.index:
                row = self.nutrition_df.loc[food_name]
                base_nutrition = {
                    "Calories": row['에너지(kcal)'],
                    "Protein": row['단백질(g)'],
                    "Carbs": row['탄수화물(g)'],
                    "Fat": row['지방(g)'],
                    "Iron": row['철(mg)'],
                    "Calc": row['칼슘(mg)']
                }
                
                # 입력된 양에 따른 영양정보 계산
                adjusted_nutrition = {
                    key: (value * quantity/100) if pd.notnull(value) else 0
                    for key, value in base_nutrition.items()
                }
                
                return {
                    "base": base_nutrition,
                    "adjusted": adjusted_nutrition
                }
            return None
        except Exception as e:
            st.error(f"영양정보 계산 오류: {e}")
            return None


    def show(self):
        """스트림릿 페이지 UI 구성 및 음식 분석"""
        st.title("🥗 음식 영양소 분석기")
        st.subheader("업로드 된 사진 또는 이미지 촬영 후 분석합니다..")

        # 1) 이미지 입력 방식
        input_method = st.radio("이미지 입력 방식 선택", ["파일 업로드", "카메라 촬영"])
        
        image = None
        if input_method == "파일 업로드":
            uploaded_file = st.file_uploader("음식 사진을 업로드하세요", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
        elif input_method == "카메라 촬영":
            image = st.camera_input("카메라로 사진을 찍어 업로드하세요")
            if image:
                image = Image.open(image)

            
        if image is not None:
            st.image(image, caption="입력된 이미지", use_container_width=True)
            
            detected_foods = self.analyze_food(image)

            if detected_foods:
                st.write("**📋 탐지된 음식:**")
                for food, confidence in detected_foods:
                    st.write(f"- {food}: {confidence * 100:.1f}% 확률")

                food_name = st.selectbox("음식명", [food for food, _ in detected_foods])
                quantity = st.number_input("양 (그램 단위)", min_value=1, value=100, step=1)
                
                # 채식 여부 판별 추가
                is_vegetarian = self.check_vegetarian(food)
                if is_vegetarian is not None:
                    if is_vegetarian:
                        st.markdown(
                            f"""
                            <div style="background-color:#e8f5e9; padding:10px; border-radius:5px; border: 1px solid #4caf50; margin-top:10px;">
                                ✅ <strong>{food}</strong>은(는) 채식 식단에 포함됩니다.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="background-color:#ffebee; padding:10px; border-radius:5px; border: 1px solid #f44336; margin-top:10px;">
                                ❌ <strong>{food}</strong>은(는) 채식 식단이 아닙니다.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"""
                        <div style="background-color:#fffde7; padding:10px; border-radius:5px; border: 1px solid #fbc02d; margin-top:10px;">
                            ⚠️ <strong>{food}</strong>에 대한 채식 여부를 확인할 수 없습니다.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # 여백 추가
                st.markdown("<br>", unsafe_allow_html=True)  # HTML로 여백 추가
                st.markdown("---")  # 구분선 추가

                if food_name and quantity:
                    nutrition = self.calculate_nutrition(food_name, quantity)
                    if nutrition:
                        st.write("### 기준 영양정보 (100g 기준)")
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        base = nutrition['base']
                        col1.metric("열량", f"{base['Calories']:.1f} kcal")
                        col2.metric("단백질", f"{base['Protein']:.1f} g")
                        col3.metric("탄수화물", f"{base['Carbs']:.1f} g")
                        col4.metric("지방", f"{base['Fat']:.1f} g")
                        col5.metric("철분", f"{base['Iron']:.1f} mg")
                        col6.metric("칼슘", f"{base['Calc']:.1f} mg")

                        st.write(f"### 조정된 영양정보 ({quantity}g 기준)")
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        adjusted = nutrition['adjusted']
                        col1.metric("열량", f"{adjusted['Calories']:.1f} kcal")
                        col2.metric("단백질", f"{adjusted['Protein']:.1f} g")
                        col3.metric("탄수화물", f"{adjusted['Carbs']:.1f} g")
                        col4.metric("지방", f"{adjusted['Fat']:.1f} g")
                        col5.metric("철분", f"{adjusted['Iron']:.1f} mg")
                        col6.metric("칼슘", f"{adjusted['Calc']:.1f} mg")

                        # 식단 저장 기능 추가
                        if st.button("식단 저장"):
                            try:
                                date_today = datetime.date.today()
                                saved_meals = {
                                    "Date": [date_today],
                                    "Meal": ["분석된 식단"],
                                    "Food": [food_name],
                                    "Quantity": [quantity],
                                    "Unit": ["g"],
                                    "Calories": [adjusted['Calories']],
                                    "Protein": [adjusted['Protein']],
                                    "Carbs": [adjusted['Carbs']],
                                    "Fat": [adjusted['Fat']],
                                    "Iron": [adjusted['Iron']],
                                    "Calc": [adjusted['Calc']]
                                }

                                df_new = pd.DataFrame(saved_meals, columns=['Date', 'Meal', 'Food', 'Quantity', 'Unit', 'Calories', 'Protein', 'Carbs', 'Fat', 'Iron', 'Calc'])

                                # 세션 상태 초기화 및 리스트 처리
                                if "saved_meals" not in st.session_state:
                                    st.session_state["saved_meals"] = df_new
                                else:
                                    if not isinstance(st.session_state["saved_meals"], pd.DataFrame):
                                        st.session_state["saved_meals"] = pd.DataFrame(columns=['Date', 'Meal', 'Food', 'Quantity', 'Unit', 'Calories', 'Protein', 'Carbs', 'Fat', 'Iron', 'Calc'])

                                
                                    # DataFrame 병합
                                    st.session_state["saved_meals"] = pd.concat(
                                        [st.session_state["saved_meals"], df_new], ignore_index=True
                                    )
                                
                                st.success("식단이 저장되었습니다!")
                            except Exception as e:
                                st.error(f"식단 저장 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.error("영양소 정보를 찾을 수 없습니다.")
            else:
                st.warning("음식이 감지되지 않았습니다. 다시 시도해주세요.")

        # 영양소 분석 완료 후 AI 메뉴 추천 섹션 추가    
        st.markdown("---")  # 구분선
        st.subheader("🤖 AI 메뉴 추천")
        
         # Gemini API 설정
        genai.configure(api_key="AIzaSyAOHLx3xEqreniNau4M_FbDXjurkx54cro")  # Gemini API 키 설정

        # 사용자 입력 UI
        user_input = st.text_input(
            "메뉴 추천을 위한 질문을 입력하세요 (예: 채식주의자를 위한 단백질 식단 추천)",
            key="menu_recommendation_input"
        )

        if st.button("추천 받기") and user_input:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(user_input)

                # 시각적으로 박스 처리된 답변 출력
                st.markdown(
                    f"""
                    <div style="background-color:#f0f8ff; padding:15px; border-radius:10px; border: 1px solid #d1e7ff; margin-top:15px;">
                        <h4 style="color:#0056b3;">추천 결과</h4>
                        <p style="color:#333;">{response.text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

 # Streamlit 앱 실행
if __name__ == "__main__":
    nutrient_app = Nutrient()
    nutrient_app.show()