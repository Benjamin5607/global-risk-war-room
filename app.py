import streamlit as st
from groq import Groq

# 1. 페이지 설정 (워룸 분위기)
st.set_page_config(
    page_title="Global Risk War-Room | High-Fidelity",
    page_icon="📡",
    layout="wide"
)

# 2. Groq 클라이언트 초기화
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 Streamlit Secrets에 'GROQ_API_KEY'가 등록되지 않았습니다.")
    st.stop()

# 3. 서버에 문 두드리기: 실시간 가용 모델 리스트
@st.cache_data(ttl=3600)
def fetch_available_models():
    try:
        models_data = client.models.list()
        text_models = [
            m.id for m in models_data.data 
            if "whisper" not in m.id and "preview" not in m.id
        ]
        return text_models
    except Exception:
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

available_models = fetch_available_models()

# 사이드바 설정
with st.sidebar:
    st.header("📡 Radar Settings")
    selected_model = st.selectbox("Intelligence Engine", available_models, index=0)
    st.markdown("---")
    st.info(f"**Operational Status:** LEVEL 5 (CRITICAL)")
    st.caption("Monitoring global signals...")

# 💡 4. 핵심 엔진: STAR 프레임워크 & Radar 깊이 적용
def generate_risk_report(incident_text, primary_model):
    # 여기가 핵심입니다. 단순 요약이 아닌 '분석'을 지시합니다.
    system_prompt = """
    You are a Senior Trust & Safety Risk Analyst for a global video platform (TikTok).
    Your goal is to convert raw news signals into actionable intelligence using the STAR narrative framework.
    
    Analyze the input text and generate a report following strictly these 7 steps.
    Maintain a cold, professional, and forensic tone.

    ### 1. Risk Level
    - Label as: Negligible, Low, Medium, or High.
    - Base this on 'Risk Velocity' (how fast it's spreading) and 'Harm Potential'.

    ### 2. Incident Summary (STAR Narrative Format)
    - Do not just summarize. Tell the risk story in 200 words:
    - **S (Situation):** The factual ground truth of the event.
    - **T (Threat/Tension):** Why this is a conflict point (e.g., cross-border tension, civil unrest).
    - **A (Amplification):** How it is spreading on platforms (e.g., bot networks, influencers, graphic content).
    - **R (Reality/Result):** The immediate operational consequence for Trust & Safety.

    ### 3. Platform Impact (TikTok Specifics)
    - Focus on 'Spillover' effects. How will this manifest on the For You Feed?
    - Mention specific formats (e.g., Duets, Sound bites, Challenges).

    ### 4. Vulnerable Target Groups
    - Who is being attacked? (List as hashtags or demographics).

    ### 5. Policy Mapping
    - Map to specific Community Guidelines (e.g., Hate Speech, Dangerous Orgs, DOI, Violent Content).

    ### 6. Watchlist Keywords
    - List specific slurs, coded language, dog-whistles, or key figures to monitor.

    ### 7. Action Plan
    - Provide 3 concrete forensic or moderation steps (e.g., "Enable Visual Hashing," "Geofence specific hashtags").
    """

    retry_queue = [primary_model] + [m for m in available_models if m != primary_model]
    
    for model in retry_queue:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": incident_text}
                ],
                temperature=0.2 # 분석적이고 일관된 톤 유지
            )
            return completion.choices[0].message.content, model
        except Exception:
            continue
            
    return "🚨 Intelligence Engine Failed. Check API Key or Server Status.", None

# 5. 메인 UI
st.title("🛡️ Global Risk Radar: Incident Analysis")
st.markdown("Run a deep-dive forensic analysis on emerging global threats.")

col1, col2 = st.columns([2, 1])

with col1:
    incident_input = st.text_area(
        "Input Raw Signals (News, URL, or Brief):",
        placeholder="Paste raw intelligence here (e.g., 'Reports of internet blackout in Uganda amid election protests...')",
        height=250
    )

    if st.button("Activate Radar Analysis 🚀", type="primary"):
        if not incident_input:
            st.warning("Please input signal data.")
        else:
            with st.spinner("Triaging signals & generating forensic report..."):
                report, used_model = generate_risk_report(incident_input, selected_model)
                
                st.markdown("---")
                st.subheader(f"📂 Operational Briefing (Engine: {used_model})")
                st.markdown(report)
                
                # 다운로드 버튼
                st.download_button(
                    label="📄 Export Briefing to War Room",
                    data=report,
                    file_name="Risk_Radar_Briefing.txt",
                    mime="text/plain"
                )

with col2:
    st.markdown("### 🔍 Radar Scope")
    st.info("""
    **Focus Areas:**
    - 📈 **Velocity:** Viral spread speed
    - 🗣️ **Narrative:** Sentiment shifts
    - 🗺️ **Spillover:** Cross-platform contagion
    """)
    
    st.markdown("### ⚡ Quick Prompts")
    if st.button("Case: Iran Blackout"):
        st.code("Reports indicate total internet blackout in Tehran following 3 weeks of protests. Death toll est. 2,600.")
    if st.button("Case: Minneapolis Doxing"):
        st.code("ICE agent shooting of Renee Good leads to 'face-reveal' doxing campaigns against federal agents.")
