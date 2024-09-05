from llm import get_ai_message
import streamlit as st
from dotenv import load_dotenv



st.set_page_config(page_title='뉴스레터 챗봇')

st.title("뉴스레터 챗봇")
st.caption("뉴스레터를 생성해 드립니다!")
load_dotenv()

if 'message_list' not in st.session_state:
    st.session_state.message_list = []


for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message['content'])





if user_question := st.chat_input(placeholder="입력한 내용을 바탕으로 뉴스레터를 생성해드릴게요"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("뉴스레터를 생성하는 중입니다"):
        ai_message = get_ai_message(user_question)
        with st.chat_message("ai"):
            st.write(ai_message)
        st.session_state.message_list.append({"role": "user", "content": ai_message})

