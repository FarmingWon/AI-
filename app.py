import streamlit as st
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from recommend import jaccard


def main():
    st.title("이력서 PDF파일을 통한 직업 추천")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        recommend_jobs = jaccard.recommend_job(uploaded_file)
        if recommend_jobs :
            st.write(f"추천 직업 : {recommend_jobs[0]['occupation3Nm']}")


if __name__ == "__main__":
    main()