import streamlit as st

# BMI 계산 함수
def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    return bmi

# 적정 체중 계산 함수
def calculate_ideal_weight(height):
    lower_weight = 18.5 * (height ** 2)
    upper_weight = 24.9 * (height ** 2)
    return lower_weight, upper_weight

# 칼슘 권장 섭취량 계산 함수
def calculate_calcium_rda(age, gender, weight):
    if age <= 18:  # 성장기 아동/청소년
        base = 1300
        factor = 5
    elif gender == "여성" and age > 50:  # 폐경 이후 여성
        base = 1200
        factor = 2
    else:  # 일반 성인 및 노인
        base = 1000
        factor = 3 if age < 65 else 2
    return base + (weight * factor)

# 철분 권장 섭취량 계산 함수
def calculate_iron_rda(age, gender, weight, is_pregnant):
    if is_pregnant:  # 임신
        base = 27
        factor = 0.3
    elif gender == "여성" and 19 <= age <= 50:  # 가임기 여성
        base = 18
        factor = 0.1
    elif age <= 18:  # 성장기
        base = 11 if gender == "남성" else 15
        factor = 0.2
    else:  # 일반 성인 및 노인
        base = 8
        factor = 0.1
    return base + (weight * factor)

# 단백질 권장 섭취량 계산 함수
def calculate_protein_rda(age, weight):
    if age <= 18:  # 성장기 아동/청소년
        factor = 1.0
    elif age > 65:  # 노인
        factor = 1.2
    else:  # 일반 성인
        factor = 0.8
    return weight * factor

# 스트림릿 UI 설정
st.title("🧮 BMI 및 RDA 계산기")
st.markdown("""
<style>
.result-card {
    background-color: #e8f4f8;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}
.result-title {
    font-size: 20px;
    font-weight: bold;
    color: #0b5394;
}
.result-value {
    font-size: 18px;
    color: #333;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# 사용자 입력 받기
gender = st.selectbox("성별을 선택하세요", ["남성", "여성"])
age = st.number_input("나이를 입력하세요", min_value=1, max_value=120)
height_cm = st.number_input("키를 입력하세요 (cm)", min_value=50, max_value=250)
weight_kg = st.number_input("몸무게를 입력하세요 (kg)", min_value=1, max_value=300)
is_pregnant = st.checkbox("임신 여부 (해당 시 체크)")

# 키(cm)를 미터로 변환
height_m = height_cm / 100

# 버튼 클릭 시 계산 수행
if st.button("결과 계산"):
    if height_cm > 0 and weight_kg > 0:
        # BMI 계산
        bmi = calculate_bmi(weight_kg, height_m)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>➡️ BMI 결과</div>
            <div class='result-value'>당신의 BMI는 <strong>{bmi:.2f}</strong>입니다.</div>
        </div>
        """, unsafe_allow_html=True)

        # BMI 상태 출력
        if bmi < 18.5:
            status = "저체중입니다."
        elif 18.5 <= bmi < 24.9:
            status = "정상 체중입니다."
        elif 25 <= bmi < 29.9:
            status = "과체중입니다."
        else:
            status = "비만입니다."
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>➡️ BMI 상태</div>
            <div class='result-value'>{status}</div>
        </div>
        """, unsafe_allow_html=True)

        # 적정 체중 계산
        lower_weight, upper_weight = calculate_ideal_weight(height_m)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>➡️ 적정 체중 범위</div>
            <div class='result-value'>당신의 키에 맞는 적정 체중 범위는 <strong>{lower_weight:.1f}kg ~ {upper_weight:.1f}kg</strong> 입니다.</div>
        </div>
        """, unsafe_allow_html=True)

        # 칼슘 RDA 계산
        calcium_rda = calculate_calcium_rda(age, gender, weight_kg)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>➡️ 칼슘 권장 섭취량</div>
            <div class='result-value'><strong>{calcium_rda:.1f}mg</strong></div>
        </div>
        """, unsafe_allow_html=True)

        # 철분 RDA 계산
        iron_rda = calculate_iron_rda(age, gender, weight_kg, is_pregnant)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>➡️ 철분 권장 섭취량</div>
            <div class='result-value'><strong>{iron_rda:.1f}mg</strong></div>
        </div>
        """, unsafe_allow_html=True)

        # 단백질 RDA 계산
        protein_rda = calculate_protein_rda(age, weight_kg)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>➡️ 단백질 권장 섭취량</div>
            <div class='result-value'><strong>{protein_rda:.1f}g</strong></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("올바른 값을 입력해주세요.")
