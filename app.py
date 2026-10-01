"""
மகளிர் அரசு நலத்திட்டங்கள் — Rural Women Government Schemes Explainer.

Target user: First-time woman user in rural India, no English, no tech background, no one to ask.
Design: 4 large touch buttons (1 demo + 3 schemes), 100% Tamil, auto-voice playback via gTTS,
        cached replay without API calls, and zero digital knowledge required.
"""

import base64
import io
import streamlit as st
from utils import (
    SCHEMES,
    FALLBACK_MESSAGE,
    get_demo_response,
    get_scheme_explanation,
    generate_tamil_audio,
    get_last_audio_error,
)

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="அரசு மகளிர் திட்டங்கள்",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── High-Contrast CSS: Rural-First, WCAG AAA ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta+Malar:wght@400;600;700;800&family=Noto+Sans+Tamil:wght@400;600;700;800&display=swap');

/* Hide ALL Streamlit chrome for clean kiosk/mobile feel */
#MainMenu, header, footer,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
.stDeployButton { display: none !important; }

html, body, [class*="css"] {
    font-family: 'Mukta Malar', 'Noto Sans Tamil', sans-serif !important;
    background: #FFFDF7 !important;
    color: #1a1a1a;
}

.main .block-container {
    padding: 1rem 1rem 3rem !important;
    max-width: 720px;
}

/* ── App Header ── */
.app-title {
    text-align: center;
    font-size: 32px;
    font-weight: 800;
    color: #7C2D12;
    margin: 0 0 6px;
    line-height: 1.3;
}
.app-subtitle {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    color: #065F46;
    margin: 0 0 16px;
}

/* ── Demo Box (Top Distinct Row) ── */
.demo-box {
    background: #FEF3C7;
    border: 3px solid #D97706;
    border-radius: 18px;
    padding: 14px 16px 6px;
    margin-bottom: 14px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(217,119,6,0.15);
}
.demo-hint {
    font-size: 20px;
    font-weight: 800;
    color: #92400E;
    margin: 0 0 8px;
}

div.stButton > button[key="demo_btn"] {
    background: #92400E !important;
    color: #FFFFFF !important;
    border: 3px solid #FCD34D !important;
    min-height: 74px !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    border-radius: 16px !important;
    width: 100% !important;
    box-shadow: 0 5px 14px rgba(146,64,14,0.25) !important;
    cursor: pointer !important;
}
div.stButton > button[key="demo_btn"]:hover {
    background: #B45309 !important;
    transform: translateY(-2px);
}

/* ── Spoken Guide Line ── */
.guide-line {
    background: #ECFDF5;
    border: 2px dashed #059669;
    color: #064E3B;
    padding: 14px 16px;
    border-radius: 16px;
    font-size: 22px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 16px;
    line-height: 1.4;
}

/* ── 3 Scheme Buttons (High Contrast 92px min-height) ── */
div.stButton > button[key^="scheme_btn_"] {
    background: #134E4A !important;
    color: #FFFFFF !important;
    border: 3px solid #2DD4BF !important;
    min-height: 92px !important;
    border-radius: 18px !important;
    font-size: 23px !important;
    font-weight: 800 !important;
    font-family: 'Mukta Malar', 'Noto Sans Tamil', sans-serif !important;
    margin-bottom: 14px !important;
    padding: 14px 18px !important;
    box-shadow: 0 6px 16px rgba(19,78,74,0.2) !important;
    white-space: pre-line !important;
    line-height: 1.4 !important;
    width: 100% !important;
    text-align: center !important;
    cursor: pointer !important;
}
div.stButton > button[key^="scheme_btn_"]:hover {
    background: #0F766E !important;
    border-color: #5EEAD4 !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(19,78,74,0.35) !important;
}

/* ── Pulsing Wait Card ── */
@keyframes pulse { 0%,100%{opacity:.9} 50%{opacity:1} }
.wait-card {
    animation: pulse 1.3s infinite;
    background: #FEF3C7;
    border: 3px solid #F59E0B;
    border-radius: 18px;
    padding: 22px 18px;
    font-size: 24px;
    font-weight: 800;
    color: #92400E;
    text-align: center;
    margin: 16px 0;
    box-shadow: 0 5px 18px rgba(245,158,11,0.2);
}

/* ── Clearly Bordered Answer Card ── */
.answer-card {
    background: #FFFFFF;
    border: 3px solid #1E3A8A;
    border-radius: 20px;
    padding: 24px 20px;
    margin: 16px 0;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.answer-header {
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 12px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
}
.answer-title {
    font-size: 26px;
    font-weight: 800;
    color: #1E3A8A;
    margin: 0;
}
.answer-badge {
    background: #DBEAFE;
    color: #1E40AF;
    padding: 6px 14px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 800;
}
.answer-body {
    font-size: 23px !important;
    line-height: 1.8 !important;
    font-weight: 500;
    color: #0F172A;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Replay Audio Button ── */
div.stButton > button[key="replay_voice_btn"] {
    background: #065F46 !important;
    color: #FFFFFF !important;
    border: 3px solid #34D399 !important;
    min-height: 68px !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    border-radius: 16px !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(6,95,70,0.25) !important;
    margin: 12px 0 6px !important;
    cursor: pointer !important;
}
div.stButton > button[key="replay_voice_btn"]:hover {
    background: #047857 !important;
    transform: translateY(-2px);
}

/* ── Fallback Card ── */
.fallback-card {
    background: #FFFBEB;
    border: 3px solid #D97706;
    border-radius: 20px;
    padding: 24px 20px;
    margin: 16px 0;
    box-shadow: 0 8px 24px rgba(217,119,6,0.12);
}
.fallback-title {
    font-size: 24px;
    font-weight: 800;
    color: #B45309;
    margin: 0 0 10px;
}
.fallback-body {
    font-size: 22px;
    line-height: 1.8;
    font-weight: 600;
    color: #78350F;
    white-space: pre-wrap;
}

/* ── Reset Button ── */
div.stButton > button[key="reset_btn"] {
    background: #374151 !important;
    color: #F9FAFB !important;
    border: 2px solid #9CA3AF !important;
    min-height: 60px !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    border-radius: 16px !important;
    width: 100% !important;
    margin-top: 10px !important;
}

/* ── Village Help Footer ── */
.village-help {
    text-align: center;
    background: #F8FAFC;
    border: 2px solid #CBD5E1;
    border-radius: 16px;
    padding: 16px;
    margin-top: 26px;
    font-size: 20px;
    font-weight: 600;
    color: #1E293B;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ──────────────────────────────────────────────────────────────
if "selected_scheme" not in st.session_state:
    st.session_state.selected_scheme = None
if "response_text" not in st.session_state:
    st.session_state.response_text = None
if "is_demo" not in st.session_state:
    st.session_state.is_demo = False
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None


def reset_view():
    """Return to the 4-button home screen."""
    st.session_state.selected_scheme = None
    st.session_state.response_text = None
    st.session_state.is_demo = False
    st.session_state.audio_bytes = None


# ─── Title & Subtitle ───────────────────────────────────────────────────────────
st.markdown('<h1 class="app-title">🌸 மகளிர் அரசு நலத்திட்டங்கள்</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">கிராமப்புற பெண்களுக்கான எளிய நேரடி குரல் வழிகாட்டி</p>', unsafe_allow_html=True)

# ─── 1. Instant Offline Demo Button (Top Distinct Row) ─────────────────────────
st.markdown("""
<div class="demo-box">
    <div class="demo-hint">✨ முதலில் இது எப்படி வேலை செய்கிறது என்று பாருங்கள்:</div>
</div>
""", unsafe_allow_html=True)

if st.button("✨ மாதிரி விளக்கம் (இணையம் தேவையில்லை)", key="demo_btn"):
    text = get_demo_response()
    st.session_state.selected_scheme = {
        "title": "கலைஞர் மகளிர் உரிமைத் திட்டம்",
        "icon": "✨",
        "badge": "மாதிரி விளக்கம்",
    }
    st.session_state.response_text = text
    st.session_state.is_demo = True
    # Fast spoken summary for instant audio playback
    demo_speech = "கலைஞர் மகளிர் உரிமைத் திட்டம். ஏழை குடும்பத் தலைவிகளுக்கு மாதம் ஆயிரம் ரூபாய் வங்கி உதவி."
    try:
        st.session_state.audio_bytes = generate_tamil_audio(demo_speech)
    except Exception:
        st.session_state.audio_bytes = None

# ─── Spoken Guide Line ──────────────────────────────────────────────────────────
st.markdown("""
<div class="guide-line">
    🗣️ கீழே உள்ள திட்டங்களில் ஏதாவது ஒன்றைத் தொடவும் — நான் உங்களுக்கு விளக்குகிறேன்:
</div>
""", unsafe_allow_html=True)

# ─── 2. Exactly 3 Scheme Buttons (Large Touch Targets) ──────────────────────────
for idx, scheme in enumerate(SCHEMES):
    label = f"{scheme['icon']} {scheme['title']}\n({scheme['short_desc']})"
    if st.button(label, key=f"scheme_btn_{idx}"):
        wait = st.empty()
        wait.markdown("""
        <div class="wait-card">
            ⏳ அம்மா, ஒரு நொடி பொறுங்கள்...<br>
            உங்களுக்கான தகவலை எடுத்து வருகிறேன்...
        </div>
        """, unsafe_allow_html=True)

        explanation = get_scheme_explanation(scheme["title"])
        if explanation.strip() == FALLBACK_MESSAGE.strip():
            spoken_summary = f"{scheme['title']}. அம்மா, இப்போது இணைய இணைப்பு குறைவாக உள்ளது. ரேஷன் கடையில் இலவசமாக உதவி செய்வார்கள்."
        else:
            spoken_summary = explanation.split("📝")[0] if "📝" in explanation else explanation[:140]

        try:
            audio = generate_tamil_audio(spoken_summary)
        except Exception:
            audio = None

        wait.empty()

        st.session_state.selected_scheme = scheme
        st.session_state.response_text = explanation
        st.session_state.is_demo = False
        st.session_state.audio_bytes = audio

# ─── 3. Response Display & Voice Playback Card ─────────────────────────────────
if st.session_state.response_text:
    info = st.session_state.selected_scheme or {}
    title = info.get("title", "திட்ட விவரம்")
    icon = info.get("icon", "📄")
    badge = info.get("badge", "அரசு உதவி")
    content = st.session_state.response_text
    is_fallback = content.strip() == FALLBACK_MESSAGE.strip()

    if is_fallback:
        st.markdown(f"""
        <div class="fallback-card">
            <div class="fallback-title">⚠️ தகவல் உதவி</div>
            <div class="fallback-body">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Clearly Bordered Answer Card
        st.markdown(f"""
        <div class="answer-card">
            <div class="answer-header">
                <h2 class="answer-title">{icon} {title}</h2>
                <span class="answer-badge">{badge}</span>
            </div>
            <div class="answer-body">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Voice Output & Listen Again Replay ───────────────────────────────
    audio_bytes = st.session_state.audio_bytes

    if audio_bytes:
        # Replay button allows listening again anytime
        if st.button("🔁 மறுபடியும் கேளுங்கள் (குரல் ஒலி)", key="replay_voice_btn"):
            st.session_state.replay_count = st.session_state.get("replay_count", 0) + 1

        try:
            audio_buffer = io.BytesIO(audio_bytes)
            audio_buffer.seek(0)
            st.audio(audio_buffer, format="audio/mp3", autoplay=True)
        except Exception:
            st.info("🔊 குரல் ஒலி தற்காலிகமாக கிடைக்கவில்லை. (இணைய இணைப்பு குறைவாக இருக்கலாம்)")
    else:
        st.info("🔊 குரல் ஒலி தற்காலிகமாக கிடைக்கவில்லை. (குரல் சேவை இணையம் வழியாக இயங்குகிறது)")

    # Dismiss Button to return to home
    if st.button("❌ விளக்கம் போதும் — வேறு திட்டம் பார்க்க", key="reset_btn"):
        reset_view()
        st.rerun()

# ─── Village Help Footer ────────────────────────────────────────────────────────
st.markdown("""
<div class="village-help">
    🌾 நேரடி உதவிக்கு: உங்கள் ஊர் ரேஷன் கடை அல்லது கிராம இ-சேவை மையத்திற்குச் செல்லுங்கள்.
    அங்குள்ள அலுவலர்கள் இலவசமாக விண்ணப்பம் போட்டுத் தருவார்கள்.
</div>
""", unsafe_allow_html=True)
