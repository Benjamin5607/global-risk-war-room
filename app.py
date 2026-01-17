import streamlit as st
from groq import Groq
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="Global Risk War-Room | Dynamic Engine",
    page_icon="🛡️",
    layout="wide"
)

# 2. Groq 클라이언트 초기화 (Secrets 보안 적용)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 Streamlit Secrets에 'GROQ_API_KEY'가 등록되지 않았습니다.")
    st.stop()

# 💡 3. 서버에 문 두드리기: 실시간 가용 모델 리스트 가져오기
@st.cache_data(ttl=3600) # 1시간 동안 캐시 유지 (서버 부하 방지)
def fetch_available_models():
    try:
        models_data = client.models.list()
        # 음성 모델(whisper) 및 미리보기용 일부 모델 제외하고 텍스트 모델만 필터링
        text_models = [
            m.id for m in models_data.data 
            if "whisper" not in m.id and "preview" not in m.id
        ]
        return text_models
    except Exception as e:
        st.sidebar.warning(f"모델 목록 로드 실패: {e}")
        # 실패 시 최소한의 기본 모델 리스트 반환 (Fallback)
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

# 실시간 모델 목록 로드
available_models = fetch_available_models()

# 4. 사이드바: 모델 엔진 제어
with st.sidebar:
    st.title("🤖 Engine Settings")
    selected_model = st.selectbox(
        "Preferred AI Model (Live from Server)", 
        available_models,
        index=0
    )
    st.divider()
    st.info(f"현재 서버에서 {len(available_models)}개의 텍스트 모델을 감지했습니다.")
    st.caption("장애 발생 시 리스트의 다음 모델로 자동 전환을 시도합니다.")

# 5. 핵심 리포트 생성 함수 (7단계 가이드 프레임워크)
def generate_risk_report(incident_text, primary_model):
    system_prompt = """
    너는 글로벌 플랫폼의 Senior Trust & Safety PM이야. 
    입력된 사건에 대해 'Operational Sensitivity'를 유지하며 아래 7단계 형식으로 리포트를 작성해.
    어투는 차갑고 전문적이며, 틱톡 가이드라인을 기준으로 판단해.
    
    1. Risk Level: Negligible, Low, Medium, High 중 택 1
    2. Summary: 사건의 핵심 (팩트 중심 200자)
    3. Platform Impact: 틱톡 플랫폼 영향 및 이유 (100자)
    4. Target Groups: 특별 보호가 필요한 계층 (해시태그 형태)
    5. Policy Mapping: 위반 소지가 큰 커뮤니티 가이드라인 조항
    6. Watchlist Keywords: 주의해야 할 키워드/슬러/인물
    7. Action Plan: 운영팀을 위한 구체적 대응 방안
    """

    # 가용한 전체 모델 중 선택한 모델을 0순위로 두고 순차적 시도 (유연한 구조)
    retry_queue = [primary_model] + [m for m in available_models if m != primary_model]
    
    for model in retry_queue:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": incident_text}
                ],
                temperature=0.1 # 사실 기반 리포트를 위한 낮은 창의성
            )
            return completion.choices[0].message.content, model
        except Exception as e:
            st.sidebar.error(f"⚠️ {model} 호출 실패, 다음 모델로 넘어갑니다...")
            continue
            
    return "🚨 모든 가용 모델 호출에 실패했습니다. API 키나 서버 상태를 확인하세요.", None

# 6. 메인 UI 레이아웃
st.title("🛡️ T&S Actionable Incident Guide")
st.markdown("---")

# 입력 섹션
incident_input = st.text_area(
    "사건 개요를 입력하세요:",
    placeholder="예: 미니애폴리스 ICE 요원 총격 사건 및 실시간 도싱(Doxing) 확산 중...",
    height=200
)

# 분석 실행
if st.button("Generate Action Plan 🚀"):
    if not incident_input:
        st.warning("분석할 내용을 입력해주세요.")
    else:
        with st.spinner("서버와 통신하며 리스크를 분석 중입니다..."):
            report, used_model = generate_risk_report(incident_input, selected_model)
            
            st.markdown(f"### 📊 Analysis Report (Source: {used_model})")
            st.divider()
            
            # 리포트 결과 출력
            st.markdown(report)
            
            # 유틸리티 기능: 텍스트 파일 다운로드
            st.download_button(
                label="Download Analysis Report",
                data=report,
                file_name="incident_response_guide.txt",
                mime="text/plain"
            )

# 하단 푸터
st.divider()
st.caption("🔒 본 도구는 내부 Operational Sensitivity 강화를 위한 목적으로만 사용됩니다.")
