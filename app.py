import streamlit as st
from groq import Groq
import pandas as pd
import json

# 1. 페이지 설정 및 테마
st.set_page_config(
    page_title="Global Risk War-Room v2.0",
    page_icon="🚨",
    layout="wide"
)

# 2. 보안 설정: Groq API Key (Streamlit Secrets 사용)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("🔑 API Key가 설정되지 않았습니다. Streamlit Secrets에 GROQ_API_KEY를 등록해주세요.")
    st.stop()

# 3. 유연한 모델 엔진 (Dynamic Model Selector)
# Groq에서 지원하는 최신 모델 리스트 (가용성에 따라 우선순위 조정 가능)
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile", # 메인 모델
    "llama-3.1-8b-instant",    # 속도 최적화
    "mixtral-8x7b-32768",      # 추론 특화
    "gemma2-9b-it"             # 가벼운 작업
]

def get_ai_guide(incident_input, model_preference):
    """선택된 모델로 7단계 리포트를 생성하며, 실패 시 Fallback 시도"""
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
    
    # 모델 리스트에서 사용자가 선택한 모델을 가장 앞에 배치
    retry_models = [model_preference] + [m for m in AVAILABLE_MODELS if m != model_preference]
    
    for model in retry_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": incident_input}
                ],
                temperature=0.1 # 일관성을 위해 낮은 창의성 설정
            )
            return response.choices[0].message.content, model
        except Exception as e:
            continue # 실패 시 다음 모델로 이동
    return "🚨 모든 모델 호출에 실패했습니다.", None

# 4. UI 구성 (Sidebar & Main)
with st.sidebar:
    st.title("⚙️ Engine Settings")
    selected_model = st.selectbox("Preferred AI Model", AVAILABLE_MODELS)
    st.divider()
    st.info("💡 모델 장애 발생 시 하위 모델로 자동 전환됩니다.")

st.title("🛡️ T&S Incident Response Guide")
st.caption("AI-Powered Global Risk Dashboard (Groq Engine)")

# 입력창
incident_input = st.text_area(
    "사건의 개요나 뉴스를 입력하세요:",
    placeholder="예: 미니애폴리스 ICE 요원 총격 사건 및 도싱 확산 중...",
    height=150
)

if st.button("Generate Guide 🚀"):
    if not incident_input:
        st.warning("분석할 사건 내용을 입력해주세요.")
    else:
        with st.spinner("Groq 엔진이 리스크를 분석 중입니다..."):
            report, used_model = get_ai_guide(incident_input, selected_model)
            
            st.divider()
            st.subheader(f"📊 Analysis Report (via {used_model})")
            
            # 리포트 출력 (7단계 가이드)
            st.markdown(report)
            
            # 후속 조치 버튼 (예시)
            st.download_button(
                label="Download Report (TXT)",
                data=report,
                file_name="risk_report.txt",
                mime="text/plain"
            )

# 5. 하단 가이드라인 참고 (Footer)
st.divider()
st.markdown("🔒 *본 시스템은 내부 T&S 감각 유지를 위한 도구이며, 최종 정책 결정은 관련 부서와의 협의가 필요합니다.*")
