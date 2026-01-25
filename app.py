import streamlit as st
import json
import sys
from io import StringIO
import os

# 페이지 설정
st.set_page_config(layout="wide", page_title="정보 수업 파이썬 실습")

# --- CSS 스타일링 (행 번호 느낌 및 음영 효과) ---
# 실제 에디터처럼 줄번호를 완벽히 구현하는 것은 Streamlit 기본 기능으로는 제한이 있으나,
# 최대한 코드 입력창스럽게 보이도록 스타일을 주입합니다.
st.markdown("""
<style>
    .stTextArea textarea {
        background-color: #f0f2f6; /* 회색 배경 */
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.5;
    }
    /* 실행 결과창 스타일 */
    .output-box {
        background-color: #262730;
        color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 데이터 로드 함수 ---
def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다: {filepath}")
        return []

# --- 사이드바 (메뉴 구성) ---
st.sidebar.title("🐍 정보 수업 실습실")
st.sidebar.header("학습 주제 선택")

# 1. 대단원 메뉴 로드
menu_data = load_json("data/menu.json")
menu_options = {item['title']: item for item in menu_data}
selected_main_title = st.sidebar.selectbox("대단원을 선택하세요", list(menu_options.keys()))

# 2. 선택된 대단원의 상세 내용 로드
if selected_main_title:
    selected_file = menu_options[selected_main_title]['file']
    chapter_data = load_json(os.path.join("data", selected_file))
    
    # 3. 소단원(챕터) 선택
    chapter_titles = [item['sub_title'] for item in chapter_data]
    selected_chapter_title = st.sidebar.selectbox("학습할 내용을 선택하세요", chapter_titles)
    
    # 선택된 챕터 데이터 찾기
    current_chapter = next((item for item in chapter_data if item['sub_title'] == selected_chapter_title), None)

# --- 메인 화면 구성 ---
if current_chapter:
    st.header(f"📝 {current_chapter['sub_title']}")
    
    # 설명 영역
    st.info(current_chapter['content'])
    
    st.divider() # 구분선
    
    # 화면 분할 (왼쪽: 코드 작성 / 오른쪽: 실행 결과)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💻 코드 작성")
        st.caption("아래 공간에 파이썬 코드를 작성하세요.")
        
        # 코드 에디터 (기본값은 JSON에 있는 예제 코드)
        # key를 unique하게 주어야 챕터 변경 시 내용이 리셋됨
        user_code = st.text_area(
            "Code Editor", 
            value=current_chapter.get('default_code', ''),
            height=300,
            key=f"editor_{selected_chapter_title}",
            label_visibility="collapsed"
        )
        
        # 실행 버튼
        run_button = st.button("▶️ 실행하기 (Run)", type="primary")

    with col2:
        st.subheader("결과 확인")
        
        if run_button:
            # 출력 캡처를 위한 설정
            old_stdout = sys.stdout
            redirected_output = StringIO()
            sys.stdout = redirected_output
            
            try:
                # 학생이 작성한 코드 실행
                exec(user_code)
                output = redirected_output.getvalue()
                
                if output:
                    st.markdown(f"<div class='output-box'>{output.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                else:
                    st.warning("출력된 결과가 없습니다. (print 함수를 사용했나요?)")
                    
            except Exception as e:
                # 에러 발생 시 붉은색으로 표시
                st.error(f"에러가 발생했습니다:\n{e}")
            finally:
                sys.stdout = old_stdout
        else:
            st.write("👈 왼쪽에서 '실행하기' 버튼을 눌러보세요.")

else:
    st.write("왼쪽 메뉴에서 학습할 내용을 선택해주세요.")
