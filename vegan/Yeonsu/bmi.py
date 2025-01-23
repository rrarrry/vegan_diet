import streamlit as st

# BMI 계산 함수
def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    return bmi

# 적정 체중 계산 함수
def calculate_ideal_weight(height):
    # BMI 18.5와 24.9일 때의 체중 계산
    lower_weight = 18.5 * (height ** 2)
    upper_weight = 24.9 * (height ** 2)
    return lower_weight, upper_weight

# 스트림릿 UI 설정
st.title("🧮BMI 계산기")

# 사용자 입력 받기
gender = st.selectbox("성별을 선택하세요", ["남성", "여성"])
age = st.number_input("나이를 입력하세요", min_value=1, max_value=120)
height_cm = st.number_input("키를 입력하세요 (cm)", min_value=50, max_value=250)
weight_kg = st.number_input("몸무게를 입력하세요 (kg)", min_value=1, max_value=300)

# 키(cm)를 미터로 변환
height_m = height_cm / 100

# 버튼 클릭 시 BMI 계산
if st.button("BMI 계산"):
    if height_cm > 0 and weight_kg > 0:
        # BMI 계산
        bmi = calculate_bmi(weight_kg, height_m)
        st.write(f"당신의 BMI는 {bmi:.2f}입니다.")
        
        # BMI 상태 출력
        if bmi < 18.5:
            st.write("저체중입니다.")
        elif 18.5 <= bmi < 24.9:
            st.write("정상 체중입니다.")
        elif 25 <= bmi < 29.9:
            st.write("과체중입니다.")
        else:
            st.write("비만입니다.")
        
        # 적정 체중 계산
        lower_weight, upper_weight = calculate_ideal_weight(height_m)
        st.write(f"당신의 키에 맞는 적정 체중 범위는 {lower_weight:.1f}kg ~ {upper_weight:.1f}kg 입니다.")
    else:
        st.error("올바른 값을 입력해주세요.")
