import streamlit as st

class BmiRdaCalculator:
    def __init__(self, gender, age, height_cm, weight_kg, is_pregnant=False):
        self.gender = gender
        self.age = age
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.is_pregnant = is_pregnant
        self.height_m = height_cm / 100

    def calculate_bmi(self):
        return self.weight_kg / (self.height_m ** 2)

    def calculate_ideal_weight(self):
        lower_weight = 18.5 * (self.height_m ** 2)
        upper_weight = 24.9 * (self.height_m ** 2)
        return lower_weight, upper_weight

    def calculate_calcium_rda(self):
        if self.age <= 18:
            base = 1300
            factor = 5
        elif self.gender == "여성" and self.age > 50:
            base = 1200
            factor = 2
        else:
            base = 1000
            factor = 3 if self.age < 65 else 2
        return base + (self.weight_kg * factor)

    def calculate_iron_rda(self):
        if self.is_pregnant:
            base = 27
            factor = 0.3
        elif self.gender == "여성" and 19 <= self.age <= 50:
            base = 18
            factor = 0.1
        elif self.age <= 18:
            base = 11 if self.gender == "남성" else 15
            factor = 0.2
        else:
            base = 8
            factor = 0.1
        return base + (self.weight_kg * factor)

    def calculate_protein_rda(self):
        if self.age <= 18:
            factor = 1.0
        elif self.age > 65:
            factor = 1.2
        else:
            factor = 0.8
        return self.weight_kg * factor

    def show(self):
        st.title("🧮 BMI 및 RDA 자동 계산기 ")
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
            font-size: 22px;
            font-weight: bold;
            color: #0b5394;
            display: flex;
            align-items: center;
        }
        .result-title::before {
            content: '🔹';
            margin-right: 10px;
            font-size: 24px;
        }
        .result-value {
            font-size: 18px;
            color: #333;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        # key 값 추가하여 중복 방지
        gender = st.selectbox("성별을 선택하세요", ["남성", "여성"], key="gender_select")
        age = st.number_input("나이를 입력하세요", min_value=1, max_value=120, key="age_input")
        height_cm = st.number_input("키를 입력하세요 (cm)", min_value=50, max_value=250, key="height_input")
        weight_kg = st.number_input("몸무게를 입력하세요 (kg)", min_value=1, max_value=300, key="weight_input")
        is_pregnant = st.checkbox("임신 여부 (해당 시 체크)", key="pregnant_checkbox")

        # 실시간 계산 수행
        calculator = BmiRdaCalculator(gender, age, height_cm, weight_kg, is_pregnant)
        
        st.session_state["nutrition_results"] = {
            "bmi": calculator.calculate_bmi(),
            "ideal_weight": calculator.calculate_ideal_weight(),
            "calcium_rda": calculator.calculate_calcium_rda(),
            "iron_rda": calculator.calculate_iron_rda(),
            "protein_rda": calculator.calculate_protein_rda()
        }
        
        # 결과 출력
        bmi = st.session_state["nutrition_results"]["bmi"]
        lower, upper = st.session_state["nutrition_results"]["ideal_weight"]
        calcium_rda = st.session_state["nutrition_results"]["calcium_rda"]
        iron_rda = st.session_state["nutrition_results"]["iron_rda"]
        protein_rda = st.session_state["nutrition_results"]["protein_rda"]

        st.markdown(f"""
        <div class='result-card'>
            <div class='result-title'>📘 BMI 결과</div>
            <div class='result-value'>당신의 BMI는 <strong>{bmi:.2f}</strong>입니다.</div>
        </div>
        <div class='result-card'>
            <div class='result-title'>📘 적정 체중 범위</div>
            <div class='result-value'>당신의 키에 맞는 적정 체중 범위는 <strong>{lower:.1f}kg ~ {upper:.1f}kg</strong> 입니다.</div>
        </div>
        <div class='result-card'>
            <div class='result-title'>📘 칼슘 권장 섭취량</div>
            <div class='result-value'>{calcium_rda:.1f}mg</div>
        </div>
        <div class='result-card'>
            <div class='result-title'>📘 철분 권장 섭취량</div>
            <div class='result-value'>{iron_rda:.1f}mg</div>
        </div>
        <div class='result-card'>
            <div class='result-title'>📘 단백질 권장 섭취량</div>
            <div class='result-value'>{protein_rda:.1f}g</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = BmiRdaCalculator("남성", 30, 175, 70)
    app.show()