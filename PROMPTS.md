# 📝 Prompt History & Engineering Log (PROMPTS.md)

> **Project:** Rural Women Government Schemes Explainer  
> **Hackathon:** PromptWars x HackArena (Google Developer Community + Hack2Skill)  
> **Tooling:** Google Antigravity Agentic Assistant

This log summarizes the primary prompt patterns and engineering iterations used to build, refine, and verify this application.

---

## 1. Persona & Architecture Definition Prompt
- **Context:** Target user is Lakshmi, a 42-year-old rural woman in Tamil Nadu with zero digital literacy, no English, and no one to ask.
- **Prompt Summary:** Specified a touch-first Streamlit layout featuring exactly 4 large buttons (1 demo + 3 real women welfare schemes) with pure spoken Tamil labels, minimum 23px font size, and modular architecture separating UI (`app.py`) from AI/TTS logic (`utils.py`).

---

## 2. Gemini 3.8 Flash System & Explanation Prompt
- **Context:** Official government scheme notifications are dense and bureaucratic.
- **Prompt Summary:** Instructed Gemini to act as a warm, empathetic village counselor explaining schemes to a rural woman without formal schooling. Enforced strict 3-part formatting:
  1. 📌 *திட்டம் என்ன?* (What the scheme is and financial benefit)
  2. 👩 *யார் தகுதியானவர்கள்?* (Eligibility criteria in plain bullet points)
  3. 📝 *விண்ணப்பிக்கும் 2-3 எளிய வழிகள்* (Practical physical steps and local village office guidance)
- **Constraint:** Zero English, zero legal jargon, and explicit guidance to visit the local village Ration Shop or *e-Sevai* center.

---

## 3. High-Contrast WCAG AAA Accessibility Styling Prompt
- **Context:** Low-vision rural users operating inexpensive mobile screens under outdoor sunlight.
- **Prompt Summary:** Designed high-contrast color tokens:
  - Deep Teal (`#134E4A`) and Amber (`#92400E`) cards with glowing borders (`#2DD4BF`, `#FCD34D`).
  - Warm cream background (`#FFFDF7`) eliminating eye strain.
  - Large button heights (92px+) for effortless tapping by trembling or elderly hands.

---

## 4. Voice Synthesis & Caching Optimization Prompt
- **Context:** Automated voice output must play immediately without lag or repeated network calls.
- **Prompt Summary:** Integrated Google Text-to-Speech (gTTS) with an in-memory and session-state audio buffer. Text is sanitized to remove emojis and markdown symbols before speech synthesis, and the `🔁 மறுபடியும் கேளுங்கள்` (Listen Again) button replays cached audio instantly without re-calling Gemini or gTTS.

---

## 5. Offline Fault Tolerance & Zero-Crash Prompt
- **Context:** Fragile rural connectivity and missing/depleted API keys must never cause a crash.
- **Prompt Summary:** Implemented an instant offline demo mode returning pre-written verified sample text with zero API calls. For live calls, all exceptions (timeouts, client errors, empty payloads) are caught and gracefully routed to a friendly Tamil fallback message directing the user to their local village center.

---

## 6. Automated Testing Specification Prompt
- **Context:** Complete test coverage across unit functions and headless Streamlit interactions.
- **Prompt Summary:** Formulated a 14-test `pytest` suite in `test_app.py` covering:
  - Demo mode sample response accuracy (zero API calls).
  - Missing, empty, and invalid API key handling.
  - Network timeouts and exception containment returning friendly fallback.
  - gTTS audio byte generation and failure handling.
  - Streamlit `AppTest` headless verification of initial 4-button render, demo click, scheme click, and reset view.
