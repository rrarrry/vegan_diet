import streamlit as st
import os
import pandas as pd

# --- CSV 함수 임포트/정의 (위에서 소개한 함수들) ---
def load_user_data(name, file_path="user_data.csv"):
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    row = df[df["name"] == name]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

def save_user_data(user_info, file_path="user_data.csv"):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["name","gender","age","height_cm","weight_kg","is_pregnant"])
        df.to_csv(file_path, index=False)

    df = pd.read_csv(file_path)
    existing = df[df["name"] == user_info["name"]]
    if not existing.empty:
        idx = existing.index[0]
        df.update(pd.DataFrame([user_info]))
    else:
        df = pd.concat([df, pd.DataFrame([user_info])], ignore_index=True)

    df.to_csv(file_path, index=False)
    st.success(f"✅ {user_info['name']}님의 정보가 저장되었습니다!")


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
        
        # key 값 추가하여 중복 방지
        gender = st.selectbox("성별을 선택하세요", ["남성", "여성"], key="gender_select")
        age = st.number_input("나이를 입력하세요", min_value=1, max_value=120, key="age_input")
        height_cm = st.number_input("키를 입력하세요 (cm)", min_value=50, max_value=250, key="height_input")
        weight_kg = st.number_input("몸무게를 입력하세요 (kg)", min_value=1, max_value=300, key="weight_input")
        is_pregnant = st.checkbox("임신 여부 (해당 시 체크)", key="pregnant_checkbox")
         
         # [추가] 이름 입력
        name = st.text_input("이름을 입력하세요", key="user_name")

        # [추가] "불러오기" 버튼
        if st.button("불러오기"):
            user_dict = load_user_data(name)
            if user_dict is not None:
                st.success(f"**{name}**님의 정보를 불러왔습니다.")
                # 세션에 저장하여 아래 number_input 등에 반영
                st.session_state["gender_select"] = user_dict["gender"]
                st.session_state["age_input"] = user_dict["age"]
                st.session_state["height_input"] = user_dict["height_cm"]
                st.session_state["weight_input"] = user_dict["weight_kg"]
                st.session_state["pregnant_checkbox"] = bool(user_dict["is_pregnant"])
                st.rerun()  # UI 업데이트 강제 실행
            else:
                st.warning(f"**{name}**님의 정보가 없습니다. 새로 입력하세요.")

        st.markdown("""---""")

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

         # [추가] "저장" 버튼
        if st.button("저장"):
            user_info = {
                "name": name,
                "gender": gender,
                "age": age,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "is_pregnant": is_pregnant
            }
            save_user_data(user_info)
            
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

        st.session_state["bmi_data"] = {
            "bmi": bmi,
            "ideal_weight_range": (lower, upper),
            "protein_rda": protein_rda,
            "calcium_rda": calcium_rda,
            "iron_rda": iron_rda
        }


if __name__ == "__main__":
     # 세션 상태 초기화 확인
    if "nutrition_results" not in st.session_state:
        st.session_state["nutrition_results"] = {}

    if "bmi_data" not in st.session_state:
        st.session_state["bmi_data"] = {}

    app = BmiRdaCalculator("남성", 30, 175, 70)
    app.show()