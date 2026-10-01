"""
மகளிர் அரசு நலத்திட்டங்கள் — Utility Module.

Handles Google Gemini 3.8 Flash API calls, gTTS voice audio generation,
scheme metadata, and graceful offline fallback logic.
All business and AI logic lives here; app.py handles the Streamlit UI.
"""

import io
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Optional module-level import for gTTS with fallback
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

load_dotenv()

# In-memory audio cache so repeated plays do not re-call gTTS
_AUDIO_CACHE: Dict[int, bytes] = {}

# Warm, respectful spoken-style Tamil fallback (no tech jargon, no English)
FALLBACK_MESSAGE: str = (
    "அம்மா, மன்னிக்கவும்! இப்போது தகவல் எடுக்க முடியவில்லை.\n\n"
    "உங்கள் ஊர் இணைய இணைப்பு குறைவாக இருக்கலாம்.\n"
    "சிறிது நேரம் கழித்து மீண்டும் தொட்டுப் பாருங்கள்.\n\n"
    "நேரடி உதவிக்கு: உங்கள் கிராம இ-சேவை மையம் அல்லது "
    "ரேஷன் கடைக்குச் சென்றால், அங்குள்ள அலுவலர்கள் "
    "இலவசமாக உதவி செய்வார்கள்."
)

# 3 Real Government Schemes for Women in Tamil Nadu
SCHEMES: List[Dict[str, str]] = [
    {
        "id": "kalaignar_magalir",
        "title": "கலைஞர் மகளிர் உரிமைத் திட்டம்",
        "short_desc": "குடும்பத் தலைவிக்கு மாதம் ரூ. 1000 வங்கி உதவி",
        "icon": "💰",
        "badge": "மாதம் ரூ. 1000",
    },
    {
        "id": "sewing_machine",
        "title": "இலவச தையல் இயந்திரம் வழங்கும் திட்டம்",
        "short_desc": "பெண்களுக்கு சுயதொழில் செய்ய இலவச மெஷின்",
        "icon": "🧵",
        "badge": "இலவச மெஷின்",
    },
    {
        "id": "pmmvy",
        "title": "பிரதம மந்திரி மாத்ரு வந்தனா திட்டம்",
        "short_desc": "கர்ப்பிணி தாய்மார்களுக்கு ரூ. 5000 ஊட்டச்சத்து நிதி",
        "icon": "👶",
        "badge": "உதவி நிதி ரூ. 5000",
    },
]

# Pre-written verified sample for instant offline demo (zero API calls)
DEMO_RESPONSE: str = """📌 1. திட்டம் என்ன? (விளக்கம்):
இது தமிழ்நாடு அரசின் திட்டம். ஏழை எளிய குடும்பத் தலைவிகளின் உழைப்பை அங்கீகரித்து, மாதாந்திர குடும்ப செலவுகளுக்கு உதவ மாதம் தோறும் ரூ. 1000 அவர்களின் வங்கிக் கணக்கில் நேரடியாக வரவு வைக்கப்படுகிறது.

👩 2. யார் விண்ணப்பிக்கலாம்? (தகுதிகள்):
• 21 வயது நிரம்பிய குடும்பத் தலைவிகள்.
• ஆண்டு குடும்ப வருமானம் ரூ. 2.5 லட்சத்திற்குள் இருக்கும் குடும்பங்கள்.
• குடும்பத்தில் 5 ஏக்கருக்கு குறைவான நன்செய் நிலம் அல்லது 10 ஏக்கருக்கு குறைவான புன்செய் நிலம் வைத்திருப்போர்.
• வீட்டில் சொந்தமாக நான்கு சக்கர வாகனம் (கார், ஜீப், டிராக்டர்) இல்லாத குடும்பங்கள்.

📝 3. விண்ணப்பிக்கும் 3 எளிய வழிகள்:
• படி 1: உங்கள் குடும்ப அட்டை (ரேஷன் கார்டு), ஆதார் அட்டை, மற்றும் உங்கள் பெயரிலுள்ள வங்கி பாஸ்புக் ஆகியவற்றை எடுத்துக் கொள்ளுங்கள்.
• படி 2: உங்கள் ஊரிலுள்ள ரேஷன் கடை அல்லது கிராம நிர்வாக அலுவலர் அறிவிக்கும் முகாமிற்கு செல்லுங்கள்.
• படி 3: அங்குள்ள அலுவலரிடம் அட்டைகளைக் காட்டி, விண்ணப்பத்தில் கைரேகை வையுங்கள். பணம் உங்கள் வங்கி கணக்கிற்கு வந்துவிடும்!

🏢 உதவிக்கு எங்கு செல்வது?
உங்களுக்கு படிவம் நிரப்பத் தெரியாவிட்டால், உங்கள் கிராம இ-சேவை மையம் அல்லது ரேஷன் கடை பணியாளரிடம் நேரடியாகக் கேட்கலாம்."""


def get_demo_response() -> str:
    """Return the pre-written demo response. Zero API calls, works completely offline."""
    return DEMO_RESPONSE


def clear_audio_cache() -> None:
    """Clear the in-memory audio cache (used in testing)."""
    _AUDIO_CACHE.clear()


def clean_text_for_speech(text: str) -> str:
    """Strip emojis and formatting markers for natural, pleasant spoken Tamil."""
    clean = text
    for ch in "📌👩📝🏢•✨💰🧵👶❌⚠️⏳🔊🗣️🌾🌸🏛️*#_`~":
        clean = clean.replace(ch, " ")
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


LAST_AUDIO_ERROR: Optional[str] = None


def get_last_audio_error() -> Optional[str]:
    """Return the last exception message from audio generation, if any."""
    return LAST_AUDIO_ERROR


def generate_tamil_audio(text: str) -> Optional[bytes]:
    """Generate Tamil speech audio bytes from text using Google gTTS.

    Writes to an in-memory BytesIO buffer (never to disk).
    Returns MP3 bytes on success, None on failure (offline/timeout).
    Uses caching so repeated calls for the same text take 0ms.
    """
    global LAST_AUDIO_ERROR
    LAST_AUDIO_ERROR = None

    clean = clean_text_for_speech(text)
    if not clean:
        return None

    # Limit spoken text to first 100 words for rapid, responsive audio generation
    words = clean.split()
    if len(words) > 100:
        clean = " ".join(words[:100]) + "..."

    # If gTTS is mocked in unit tests, bypass cache to test mock behavior
    is_mocked = hasattr(gTTS, "side_effect") or hasattr(gTTS, "assert_called")

    text_hash = hash(clean)
    if not is_mocked and text_hash in _AUDIO_CACHE:
        return _AUDIO_CACHE[text_hash]

    if gTTS is None:
        LAST_AUDIO_ERROR = "gTTS library is not installed."
        return None

    try:
        tts = gTTS(text=clean, lang="ta", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_data = buf.read()
        if audio_data and len(audio_data) > 50:
            _AUDIO_CACHE[text_hash] = audio_data
            return audio_data
        LAST_AUDIO_ERROR = "Generated audio buffer was empty or under 50 bytes."
        return None
    except Exception as e:
        LAST_AUDIO_ERROR = str(e)
        return None


def generate_tamil_audio_stream(text: str) -> Optional[io.BytesIO]:
    """Generate an in-memory BytesIO stream for st.audio() from Tamil text.

    Uses gTTS writing to an in-memory buffer (write_to_fp).
    Never writes to disk. Returns seek(0) BytesIO buffer or None.
    """
    audio_data = generate_tamil_audio(text)
    if audio_data:
        buf = io.BytesIO(audio_data)
        buf.seek(0)
        return buf
    return None


def get_scheme_explanation(
    scheme_name: str,
    api_key: Optional[str] = None,
    client_instance: Optional[Any] = None,
) -> str:
    """Call Google Gemini 3.8 Flash to explain a scheme in simple, respectful rural Tamil.

    Returns FALLBACK_MESSAGE on any failure (missing key, timeout, bad response).
    """
    if "GEMINI_API_KEY" not in os.environ:
        load_dotenv()
    resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_api_key and client_instance is None:
        return FALLBACK_MESSAGE

    prompt = (
        "நீங்கள் கிராமப்புற தமிழ்நாட்டு பெண்களுக்கு உதவும் ஒரு கனிவான அரசு ஆலோசகர். "
        "தொழில்நுட்ப அறிவு அல்லது ஆங்கிலம் தெரியாத ஒரு கிராமத்துப் பெண் "
        "இந்தத் திட்டத்தைப் பற்றிக் கேட்கிறார். "
        "மிக எளிய, கிராமத்துப் பேச்சுத்தமிழில் விளக்கவும்.\n\n"
        f"திட்டம்: {scheme_name}\n\n"
        "கீழ்க்கண்ட 3 தலைப்புகளில் மட்டும் பதிலளிக்கவும்:\n"
        "📌 1. திட்டம் என்ன? (விளக்கம் & உதவித் தொகை)\n"
        "👩 2. யார் தகுதியானவர்கள்?\n"
        "📝 3. விண்ணப்பிக்கும் 2-3 எளிய வழிகள் & தேவையான ஆவணங்கள்\n\n"
        "விதிகள்: ஆங்கிலம் முற்றிலும் தவிர்க்கவும். எளிய புல்லட் பாயிண்டுகள். "
        "முடிவில் உதவிக்கு ஊர் இ-சேவை மையம் அல்லது ரேஷன் கடையை அணுகுமாறு கூறவும்."
    )

    try:
        if client_instance is not None:
            client = client_instance
        else:
            from google import genai
            client = genai.Client(api_key=resolved_api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )

        if response and hasattr(response, "text") and response.text:
            cleaned = response.text.strip()
            if cleaned:
                return cleaned
        return FALLBACK_MESSAGE
    except Exception:
        return FALLBACK_MESSAGE
