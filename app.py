import streamlit as st
import json
import sys
from io import StringIO

# 페이지 기본 설정
st.set_page_config(page_title="경문고 정보수업 Python 박살내기", layout="wide")

# 1. CSS 스타일링 (행 번호 및 얼룩말 무늬 효과 구현)
# Streamlit 기본 Text Area로는 완벽한 에디터 구현이 어렵지만, 최대한 요청하신 디자인에 맞게 스타일을 주입합니다.
st.markdown("""
<style>
    /* 전체 폰트 설정 */
    body { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 코드 에디터 스타일 모방 */
    .stTextArea textarea {
        background-color: #f0f2f6; /* 기본 배경 */
        font-family: 'Courier New', monospace;
        line-height: 1.5;
        font-size: 14px;
        /* 얼룩말 무늬 (linear-gradient 이용) */
        background-image: linear-gradient(#f0f2f6 50%, #e6e9ef 50%);
        background-size: 100% 3rem; /* 2줄(1.5rem * 2) 간격으로 패턴 반복 */
        background-attachment: local;
        padding-left: 35px; /* 행 번호 공간 확보 */
    }

    /* 행 번호 가상 요소 (시각적 효과) */
    .code-container {
        position: relative;
    }
    .line-numbers {
        position: absolute;
        top: 2px;
        left: 5px;
        width: 25px;
        height: 100%;
        color: #888;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.5;
        text-align: right;
        overflow: hidden;
        pointer-events: none;
        z-index: 10;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    with open('lecture_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_data()

# 3. 사이드바 (주제 선택)
st.sidebar.title("🐍 Python 박살내기!!")
chapter_list = [f"{ch['title']}" for ch in data['chapters']]
selected_chapter_name = st.sidebar.selectbox("학습할 단원을 선택하세요:", chapter_list)

# 선택된 챕터 데이터 가져오기
selected_chapter = next(item for item in data['chapters'] if item['title'] == selected_chapter_name)

# 4. 메인 화면 구성
st.title(selected_chapter['title'])
st.info(selected_chapter['description'])
st.markdown(selected_chapter['content'])

st.write("---")
st.subheader("💻 실습 코딩")

# 코드 실행 영역 (왼쪽: 에디터, 오른쪽: 결과)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**코드 작성**")
    
    # 행 번호 시각화를 위한 HTML 생성 (단순 1~20줄 예시)
    line_numbers = "<br>".join([str(i) for i in range(1, 21)])
    
    # 에디터 컨테이너
    st.markdown(f"""
    <div class="code-container">
        <div class="line-numbers">{line_numbers}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 코드 입력창
    code_input = st.text_area(
        label="Code Editor",
        value=selected_chapter['default_code'],
        height=300,
        label_visibility="collapsed",
        key=f"editor_{selected_chapter['id']}"
    )

    if st.button("▶ 실행하기", type="primary"):
        run_code = True
    else:
        run_code = False

with col2:
    st.markdown("**실행 결과**")
    result_container = st.container(border=True)
    
    if run_code:
        # 표준 출력을 가로채기 위한 설정
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        try:
            # 코드 실행 (Pyodide 환경에서는 브라우저 내에서 안전하게 실행됨)
            exec(code_input)
            output = redirected_output.getvalue()
            result_container.code(output if output else "출력 결과가 없습니다.")
        except Exception as e:
            result_container.error(f"에러 발생:\n{e}")
        finally:
            sys.stdout = old_stdout
    else:
        result_container.write("왼쪽의 [실행하기] 버튼을 눌러보세요.")

# 하단 푸터
st.write("---")
st.caption("교재 출처: Python 박살내기!! (경문고 정보수업)")
