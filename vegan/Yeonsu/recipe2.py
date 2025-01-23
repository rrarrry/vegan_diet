import streamlit as st
import openai

# OpenAI API 키 설정
openai.api_key = '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'

# 함수: 비건 음식의 영양소와 레시피 정보 요청
def get_food_info_and_recipe(food_name):
    # 요청 메시지 정의 (한국어로 변경)
    prompt = f"비건 음식 {food_name}에 대한 100g당 영양소 정보와 추천 요리를 제공해주세요. 칼로리, 단백질, 탄수화물, 지방, 철분을 포함해주세요. 영양소와 레시피를 구분해서 항목별로 출력해 주세요."

    # Chat 모델을 위한 요청
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 또는 "gpt-4"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500  # 최대 토큰 수 확장
    )

    # 응답 반환
    return response['choices'][0]['message']['content'].strip()

# 타이틀 및 설명
st.markdown(
    """
    <h1 style="text-align:center; font-size: 2.5em; color: #2c3e50;">👨‍🍳 비건 음식 영양소 계산기 및 추천 요리</h1>
    """, unsafe_allow_html=True)

st.write("비건 음식을 선택하고 그에 대한 영양소와 추천 요리를 확인해 보세요!")

# 음식 선택
food_name = st.text_input("음식 이름을 입력하세요 (예: 아보카도, 바나나 등)", "아보카도")

# 계산 버튼
if st.button("영양소 계산 및 추천 요리 받기"):
    # OpenAI API를 통해 정보 받기
    food_info_and_recipe = get_food_info_and_recipe(food_name)

    # 결과 출력
    st.markdown(f"### {food_name}에 대한 정보")
    st.markdown(f"```\n{food_info_and_recipe}\n```")
