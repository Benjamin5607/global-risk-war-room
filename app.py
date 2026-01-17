import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Global Risk War-Room", layout="wide")

# 사이드바: 현재 플랫폼 상태 제어
st.sidebar.title("🚨 Operational Status")
status = st.sidebar.selectbox("Current Level", ["NORMAL", "LEVEL 3", "LEVEL 5 - CRITICAL"])
if status == "LEVEL 5 - CRITICAL":
    st.sidebar.error(f"Status: {status}")
else:
    st.sidebar.info(f"Status: {status}")

st.title("🛡️ T&S Incident Response Guide")
st.caption("Operational Sensitivity Calibration Tool v2.0")

# 7단계 프레임워크 렌더링 함수
def render_incident_guide(data):
    # 1. Risk Level
    level_colors = {"High": "red", "Medium": "orange", "Low": "blue", "Negligible": "gray"}
    color = level_colors.get(data['level'], "gray")
    st.markdown(f"### 1. Risk Level: :{color}[{data['level']} Risk]")
    
    # 2. Summary & 3. Impact
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("2. Incident Summary")
        st.info(data['summary'])
    with col2:
        st.subheader("3. Platform Impact (TikTok)")
        st.warning(data['impact'])

    # 4. Target Groups & 5. Policy Mapping
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("4. Vulnerable Groups")
        st.write(f"🎯 **Target:** {data['targets']}")
    with col4:
        st.subheader("5. Policy Mapping")
        st.markdown(f"📌 **Violations:** `{data['policies']}`")

    # 6. Watchlist Keywords
    st.subheader("6. Watchlist Keywords")
    st.code(data['keywords'], language="text")

    # 7. Action Plan
    st.subheader("7. Action Plan")
    st.success(data['action_plan'])

# 시뮬레이션 데이터 (미니애폴리스 인시던트)
mock_data = {
    "level": "High",
    "summary": "ICE 요원의 총격으로 인한 Renee Good 사망 사건 이후, 연방 요원에 대한 디지털 도싱(Doxing) 및 보복 시위가 전국적으로 확산 중.",
    "impact": "요원들의 얼굴을 노출하는 'Face-reveal' 챌린지 급증 우려. 듀엣/스티치 기능을 통한 신상 정보 복제 위험.",
    "targets": "연방 요원 및 그 가족, 시위 인근 이민자 커뮤니티",
    "policies": "Harassment & Bullying, Violence & Incitement",
    "keywords": "#IceHunter, Agent Jonathan Ross, Mask-off, #JusticeForRenee",
    "action_plan": "1. 특정 요원 이름 검색어 차단. 2. 유출 사진 안면 인식 필터 적용. 3. PSA 안내 배너 노출."
}

render_incident_guide(mock_data)
