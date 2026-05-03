#!/usr/bin/env python3
"""
AutiSense AI - Voice-based AI simulator for autistic children
Secure API key handling for GitHub + Hugging Face Spaces deployment
"""

import os
import time
import whisper
import gradio as gr
from gtts import gTTS
from groq import Groq
from collections import Counter
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()  # Load from .env file (local) or HF Secrets (production)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Add to .env or Hugging Face Secrets.")

client = Groq(api_key=GROQ_API_KEY)
stt_model = whisper.load_model("tiny")

# --- RAG KNOWLEDGE BASE ---
STRATEGY_KB = {
    "emotional": "Validate the feeling first, then gently suggest a calming activity or sensory break.",
    "social":    "Use simple 'I feel' statements and explain social cues in concrete, literal terms.",
    "functional":"Use 'First/Then' logic and offer two specific choices so the child can decide.",
    "crisis":    "Stay calm and use very few words — one short instruction at a time.",
}

DAILY_TASKS = ["Brush Teeth", "Breakfast", "Lunch", "Playing Game", "Dinner", "Sleep"]
TASK_STEPS  = {
    "Brush Teeth":  ["1. Put paste on brush.", "2. Brush all teeth.", "3. Rinse your mouth."],
    "Breakfast":    ["1. Sit at the table.",   "2. Eat your food.",   "3. Drink your water."],
    "Playing Game": ["1. Pick a toy.",          "2. Play nicely.",     "3. Clean up when done."],
    "Lunch":        ["1. Wash hands.",          "2. Eat your lunch.",  "3. Put your plate away."],
    "Dinner":       ["1. Sit with family.",     "2. Try your food.",   "3. Wipe your face."],
    "Sleep":        ["1. Put on pajamas.",      "2. Get in bed.",      "3. Close your eyes."]
}

# ---------------------------------------------------------------------------
# EMOTION CARDS
# ---------------------------------------------------------------------------
def _svg(bg, stroke, eyes, mouth, extra, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" width="84" height="100">
  <circle cx="50" cy="50" r="36" fill="{bg}" stroke="{stroke}" stroke-width="2.5"/>
  <ellipse cx="14" cy="50" rx="5" ry="8" fill="{bg}" stroke="{stroke}" stroke-width="2"/>
  <ellipse cx="86" cy="50" rx="5" ry="8" fill="{bg}" stroke="{stroke}" stroke-width="2"/>
  {eyes}{mouth}{extra}
  <text x="50" y="108" text-anchor="middle"
        font-family="Arial Rounded MT Bold,Arial,sans-serif"
        font-size="12" font-weight="bold" fill="#222">{label}</text>
</svg>"""

_EO = """<circle cx="34" cy="44" r="6" fill="white" stroke="#333" stroke-width="1.8"/>
  <circle cx="66" cy="44" r="6" fill="white" stroke="#333" stroke-width="1.8"/>
  <circle cx="35" cy="45" r="3" fill="#333"/><circle cx="67" cy="45" r="3" fill="#333"/>
  <circle cx="36" cy="43" r="1" fill="white"/><circle cx="68" cy="43" r="1" fill="white"/>"""

_EW = """<circle cx="34" cy="44" r="8" fill="white" stroke="#333" stroke-width="1.8"/>
  <circle cx="66" cy="44" r="8" fill="white" stroke="#333" stroke-width="1.8"/>
  <circle cx="34" cy="45" r="5" fill="#333"/><circle cx="66" cy="45" r="5" fill="#333"/>
  <circle cx="35" cy="43" r="1.5" fill="white"/><circle cx="67" cy="43" r="1.5" fill="white"/>"""

_ES = """<ellipse cx="34" cy="46" rx="6" ry="3.5" fill="white" stroke="#333" stroke-width="1.8"/>
  <ellipse cx="66" cy="46" rx="6" ry="3.5" fill="white" stroke="#333" stroke-width="1.8"/>
  <path d="M28 42 Q34 38 40 42" stroke="#333" stroke-width="2" fill="none"/>
  <path d="M60 42 Q66 38 72 42" stroke="#333" stroke-width="2" fill="none"/>
  <ellipse cx="34" cy="47" rx="3.5" ry="2" fill="#333"/>
  <ellipse cx="66" cy="47" rx="3.5" ry="2" fill="#333"/>"""

_EA = """<circle cx="34" cy="46" r="6" fill="white" stroke="#333" stroke-width="1.8"/>
  <circle cx="66" cy="46" r="6" fill="white" stroke="#333" stroke-width="1.8"/>
  <circle cx="34" cy="47" r="3" fill="#333"/><circle cx="66" cy="47" r="3" fill="#333"/>
  <line x1="27" y1="37" x2="41" y2="42" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="73" y1="37" x2="59" y2="42" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>"""

_EX = """<line x1="27" y1="38" x2="41" y2="52" stroke="#333" stroke-width="3" stroke-linecap="round"/>
  <line x1="41" y1="38" x2="27" y2="52" stroke="#333" stroke-width="3" stroke-linecap="round"/>
  <line x1="59" y1="38" x2="73" y2="52" stroke="#333" stroke-width="3" stroke-linecap="round"/>
  <line x1="73" y1="38" x2="59" y2="52" stroke="#333" stroke-width="3" stroke-linecap="round"/>"""

EMOTION_CARDS = [
    ("btn_happy",   "I feel happy",
     _svg("#FFE066","#333",_EO,
          '<path d="M32 60 Q50 74 68 60" stroke="#333" stroke-width="2.5" fill="#FF8A80" stroke-linecap="round"/>',
          '<circle cx="31" cy="58" r="5" fill="#FFAB91" opacity=".7"/><circle cx="69" cy="58" r="5" fill="#FFAB91" opacity=".7"/>',
          "Happy")),
    ("btn_sad",     "I feel sad",
     _svg("#90CAF9","#333",_EO,
          '<path d="M32 66 Q50 54 68 66" stroke="#333" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
          '<line x1="37" y1="53" x2="35" y2="63" stroke="#5599cc" stroke-width="2" opacity=".8"/>'
          '<line x1="63" y1="53" x2="65" y2="63" stroke="#5599cc" stroke-width="2" opacity=".8"/>',
          "Sad")),
    ("btn_angry",   "I feel angry",
     _svg("#EF9A9A","#333",_EA,
          '<path d="M32 66 Q50 56 68 66" stroke="#333" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
          '<path d="M40 28 Q45 22 50 28 Q55 22 60 28" stroke="#c0392b" stroke-width="2" fill="none"/>',
          "Angry")),
    ("btn_scared",  "I feel scared",
     _svg("#CE93D8","#333",_EW,
          '<path d="M34 64 L39 58 L44 64 L49 58 L54 64 L59 58 L64 64" stroke="#333" stroke-width="2" fill="none" stroke-linecap="round"/>',
          "", "Scared")),
    ("btn_tired",   "I am tired",
     _svg("#A5D6A7","#333",_ES,
          '<path d="M35 64 Q50 70 65 64" stroke="#333" stroke-width="2" fill="none" stroke-linecap="round"/>',
          '<path d="M63 28 Q71 18 76 26" stroke="#aaa" stroke-width="1.5" fill="none"/>',
          "Tired")),
    ("btn_excited", "I feel excited",
     _svg("#FFF176","#333",_EO,
          '<ellipse cx="50" cy="63" rx="11" ry="7" fill="#FF8A80" stroke="#333" stroke-width="2"/>',
          '<circle cx="30" cy="57" r="5" fill="#FFAB91" opacity=".7"/><circle cx="70" cy="57" r="5" fill="#FFAB91" opacity=".7"/>',
          "Excited")),
    ("btn_hungry",  "I am hungry",
     _svg("#FFCC80","#333",_EO,
          '<path d="M34 63 Q50 73 66 63" stroke="#333" stroke-width="2.5" fill="#FF8A80" stroke-linecap="round"/>',
          '<text x="50" y="30" text-anchor="middle" font-size="13">🍕</text>',
          "Hungry")),
    ("btn_bathroom","Bathroom",
     _svg("#80DEEA","#333",_EO,
          '<path d="M37 63 Q50 70 63 63" stroke="#333" stroke-width="2" fill="none" stroke-linecap="round"/>',
          '<text x="50" y="30" text-anchor="middle" font-size="13">🚻</text>',
          "Bathroom")),
    ("btn_hurt",    "I am hurt",
     _svg("#FFCDD2","#333",_EX,
          '<path d="M34 66 Q50 58 66 66" stroke="#333" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
          '<path d="M61 26 L66 18 L71 26 L66 22 Z" fill="#E53935"/>',
          "Hurt")),
    ("btn_yes",     "Yes",
     """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" width="84" height="100">
  <circle cx="50" cy="50" r="36" fill="#A5D6A7" stroke="#2E7D32" stroke-width="3"/>
  <polyline points="27,50 41,64 73,32" stroke="#2E7D32" stroke-width="7"
            fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="50" y="108" text-anchor="middle"
        font-family="Arial Rounded MT Bold,Arial,sans-serif"
        font-size="12" font-weight="bold" fill="#222">Yes</text>
</svg>"""),
    ("btn_no",      "No",
     """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" width="84" height="100">
  <circle cx="50" cy="50" r="36" fill="#FFCDD2" stroke="#C62828" stroke-width="3"/>
  <line x1="30" y1="30" x2="70" y2="70" stroke="#C62828" stroke-width="7" stroke-linecap="round"/>
  <line x1="70" y1="30" x2="30" y2="70" stroke="#C62828" stroke-width="7" stroke-linecap="round"/>
  <text x="50" y="108" text-anchor="middle"
        font-family="Arial Rounded MT Bold,Arial,sans-serif"
        font-size="12" font-weight="bold" fill="#222">No</text>
</svg>"""),
]

# ---------------------------------------------------------------------------
# HTML PICTURE BOARD
# ---------------------------------------------------------------------------
CARD_CSS = """<style>
.aac-board{display:flex;flex-wrap:wrap;gap:10px;padding:6px 0;}
.aac-card{display:flex;flex-direction:column;align-items:center;
  background:#fff;border:3px solid #ddd;border-radius:14px;
  padding:6px 8px;cursor:pointer;user-select:none;
  transition:border-color .15s,box-shadow .15s,transform .1s;min-width:76px;}
.aac-card:hover{border-color:#42A5F5;box-shadow:0 4px 14px rgba(66,165,245,.35);transform:translateY(-2px);}
.aac-card:active,.aac-card.pressed{transform:scale(.95);border-color:#1565C0;background:#E3F2FD;}
</style>"""

def build_html_board(cards):
    items = ""
    for (eid, _, svg) in cards:
        items += f'<div class="aac-card" onclick="grClick(\'{eid}\', this)">{svg}</div>\n'
    return CARD_CSS + f'<div class="aac-board">{items}</div>'

HEAD_JS = """
<script>
function grClick(eid, cardEl) {
    var wrapper = document.getElementById(eid);
    if (!wrapper) { console.error('grClick: wrapper not found for id:', eid); return; }
    var btn = wrapper.querySelector('button');
    if (!btn) {
        if (wrapper.tagName === 'BUTTON') { btn = wrapper; }
        else { console.error('grClick: no <button> inside:', eid); return; }
    }
    btn.click();
    if (cardEl) {
        cardEl.classList.add('pressed');
        setTimeout(function(){ cardEl.classList.remove('pressed'); }, 300);
    }
}
</script>
"""

HIDDEN_BTN_CSS = "\n".join(
    f"#{eid} {{ "
    f"position:absolute !important; width:1px !important; height:1px !important; "
    f"padding:0 !important; margin:-1px !important; overflow:hidden !important; "
    f"clip:rect(0,0,0,0) !important; white-space:nowrap !important; "
    f"border:0 !important; }}"
    for (eid, _, __) in EMOTION_CARDS
)

# ---------------------------------------------------------------------------
# IMPROVED SESSION  — multi-state log + pattern detection + repeat guard
# ---------------------------------------------------------------------------
class Session:
    MAX_LOG     = 10   # rolling window of past states
    MAX_HISTORY = 20   # max chat turns kept in LLM context

    def __init__(self):
        self.scenario       = "parent"
        self.preferences    = {}        # {"food": "pizza", "toy": "lego", …}
        self.state_log      = []        # last N detected states
        self.last_responses = []        # last 3 AI replies (anti-repeat)
        self.history        = []
        self.turn_count     = 0

    def reset(self):
        self.history        = []
        self.state_log      = []
        self.last_responses = []
        self.turn_count     = 0
        return [], f"Ready! Mode: {self.scenario.upper()}", None

    def update_memory(self, text: str) -> str:
        t = text.lower()

        # Accumulate preferences
        if "i like" in t:
            tail = t.split("i like", 1)[-1].strip().rstrip(".")
            if any(w in tail for w in ["pizza","apple","banana","food","eat","snack","cookie","juice"]):
                self.preferences["food"] = tail
            elif any(w in tail for w in ["toy","game","block","car","doll","lego"]):
                self.preferences["toy"] = tail
            else:
                self.preferences["general"] = tail

        # State detection — priority order: crisis > emotional > functional > social
        crisis_words    = ["help","scared","panic","danger","hurt","pain","emergency"]
        emotional_words = ["sad","happy","angry","excited","worried","lonely","mad","frustrated"]
        functional_words= ["hungry","bathroom","tired","thirsty","eat","drink","brush","sleep","play"]

        if any(w in t for w in crisis_words):
            state = "crisis"
        elif any(w in t for w in emotional_words):
            state = "emotional"
        elif any(w in t for w in functional_words):
            state = "functional"
        else:
            state = "social"

        self.state_log.append(state)
        if len(self.state_log) > self.MAX_LOG:
            self.state_log.pop(0)

        self.turn_count += 1
        return state

    def detect_pattern(self) -> str:
        """Return a pattern hint for the prompt if a state repeats frequently."""
        if len(self.state_log) < 3:
            return ""
        counts  = Counter(self.state_log)
        top, n  = counts.most_common(1)[0]
        if n / len(self.state_log) >= 0.6 and n >= 3:
            messages = {
                "emotional":  "Pattern noticed: child has expressed emotions frequently. Prioritise validation and a calm-down activity.",
                "functional": "Pattern noticed: child has many practical needs. Keep language concrete and action-oriented.",
                "crisis":     "Pattern noticed: child seems repeatedly distressed. Use very short, soothing language.",
            }
            return messages.get(top, "")
        return ""

    def register_response(self, text: str):
        self.last_responses.append(text[:80])
        if len(self.last_responses) > 3:
            self.last_responses.pop(0)

    def no_repeat_hint(self) -> str:
        if not self.last_responses:
            return ""
        return "Do NOT repeat or closely paraphrase these recent replies: [" + " | ".join(self.last_responses) + "]"


session = Session()

# ---------------------------------------------------------------------------
# COACHING SYSTEM  — politeness reward + clarity nudge
# ---------------------------------------------------------------------------
# Cards that send intentionally short text — do not coach these
_CARD_TEXTS = {t.lower() for (_, t, _) in EMOTION_CARDS}

def get_coaching_feedback(text: str) -> str | None:
    t     = text.strip().lower()
    words = t.split()

    if any(p in t for p in ["please", "thank you", "thanks"]):
        return "⭐ Great manners! Saying please and thank you is wonderful!"

    if len(words) <= 2 and t not in _CARD_TEXTS:
        return "💬 Can you tell me a little more? Try using a full sentence!"

    return None

# ---------------------------------------------------------------------------
# SYSTEM PROMPT BUILDER
# ---------------------------------------------------------------------------
_ROLE_DESC = {
    "teacher":   "You are Ms. Anna, a warm and structured teacher.",
    "caretaker": "You are a calm, patient caretaker.",
    "parent":    "You are a loving, supportive parent.",
}

def build_system_prompt(state: str) -> str:
    role     = _ROLE_DESC.get(session.scenario, _ROLE_DESC["parent"])
    strategy = STRATEGY_KB.get(state, STRATEGY_KB["social"])
    pattern  = session.detect_pattern()

    pref_hints = [f"The child has mentioned they like: {v}." for v in session.preferences.values()]
    pref_str   = " ".join(pref_hints)

    no_repeat  = session.no_repeat_hint()

    return f"""{role}

RESPONSE RULES — follow all of these:
- Reply in 1–2 short, simple sentences only.
- Use warm, encouraging, concrete language appropriate for a child with autism.
- Never use jargon, sarcasm, idioms, or complex vocabulary.
- Do NOT ask more than one question per reply.
- Vary your sentence openings — do NOT start every reply with "I understand" or "Of course".
- When the child expresses a practical need (hunger, bathroom, tired, etc.), respond naturally and helpfully based on context. Do not recite a fixed script or menu — use reasoning.
- When the child shares a feeling, validate it sincerely before suggesting anything.
- Keep your tone gentle and never impatient.

CURRENT STRATEGY: {strategy}

{pref_str}
{pattern}
{no_repeat}
""".strip()

# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------
def generate_speech(text):
    try:
        fname = f"voice_{int(time.time()*1000)}.mp3"
        gTTS(text=text, lang='en').save(fname)
        return fname
    except:
        return None

# ---------------------------------------------------------------------------
# IMPROVED handle_interaction
# ---------------------------------------------------------------------------
def handle_interaction(text, history):
    if not text or not text.strip():
        return history, "Ready", None

    # 1. Update memory, get state
    state = session.update_memory(text)

    # 2. Coaching check
    coaching = get_coaching_feedback(text)

    # 3. Build prompt
    system_prompt = build_system_prompt(state)

    # 4. Assemble messages (cap history to avoid token overflow)
    recent = history[-(session.MAX_HISTORY):]
    messages = [{"role": "system", "content": system_prompt}]
    for m in recent:
        messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
    messages.append({"role": "user", "content": text})

    # 5. Call LLM
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.75,   # more variety
            max_tokens=120,     # enforces brevity at API level
        )
        ai = res.choices[0].message.content.strip()
    except Exception as e:
        ai = "I'm right here with you."

    # 6. Register reply for anti-repeat tracking
    session.register_response(ai)

    # 7. TTS
    audio = generate_speech(ai)

    # 8. Build new history
    new_history = history + [
        {"role": "user",      "content": text},
        {"role": "assistant", "content": ai},
    ]

    # 9. Feedback label — coaching takes priority
    label = coaching if coaching else f"State: {state.upper()} | Turn {session.turn_count}"

    return new_history, label, audio

# ---------------------------------------------------------------------------
# IMPROVED process_audio  (signature unchanged)
# ---------------------------------------------------------------------------
def process_audio(audio, history):
    if not audio:
        return history, "No audio", None, None
    text = stt_model.transcribe(audio)["text"].strip()
    h, f, a = handle_interaction(text, history)
    return h, f, a, None

# ---------------------------------------------------------------------------
# UI SETUP
# ---------------------------------------------------------------------------
with gr.Blocks(
    theme=gr.themes.Soft(),
    head=HEAD_JS,
    css=HIDDEN_BTN_CSS + """
.aac-section-label{font-size:15px;font-weight:700;color:#555;margin:6px 0 2px 2px;}
"""
) as demo:

    gr.Markdown("# 🧠 AutiSense AI: RAG Adaptive Support")

    with gr.Row():
        mode_p = gr.Button("🏠 Parent Mode")
        mode_t = gr.Button("🏫 Teacher Mode")
        mode_c = gr.Button("🤝 Caretaker Mode")

    with gr.Row():
        with gr.Column(scale=3):
            chat = gr.Chatbot(type="messages", height=320)

            gr.HTML("<div class='aac-section-label'>🎭 How do you feel? / What do you need?</div>")
            gr.HTML(build_html_board(EMOTION_CARDS))

            hidden_buttons = []
            for (eid, ai_text, _) in EMOTION_CARDS:
                hb = gr.Button(ai_text, elem_id=eid, visible=True)
                hidden_buttons.append((hb, ai_text))

            mic = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Record Voice")
            with gr.Row():
                submit_audio_btn = gr.Button("📤 Send & Clear", variant="primary")
                audio_playback   = gr.Audio(autoplay=True, label="AI Voice Output", visible=True)

        with gr.Column(scale=2):
            feedback_label = gr.Label(value="Mode: PARENT")

            gr.Markdown("### 📅 Daily Schedule")
            for t_name in DAILY_TASKS:
                gr.Checkbox(label=t_name, value=False)

            gr.Markdown("---")
            reset_btn = gr.Button("Reset Everything")

    # --- BINDINGS ---
    for (hb, ai_text) in hidden_buttons:
        hb.click(
            fn=lambda h, t=ai_text: handle_interaction(t, h),
            inputs=[chat],
            outputs=[chat, feedback_label, audio_playback]
        )

    mode_p.click(lambda: (setattr(session,'scenario','parent'),    "Mode: PARENT")[1],    None, feedback_label)
    mode_t.click(lambda: (setattr(session,'scenario','teacher'),   "Mode: TEACHER")[1],   None, feedback_label)
    mode_c.click(lambda: (setattr(session,'scenario','caretaker'), "Mode: CARETAKER")[1], None, feedback_label)

    submit_audio_btn.click(
        fn=process_audio,
        inputs=[mic, chat],
        outputs=[chat, feedback_label, audio_playback, mic]
    )
    reset_btn.click(session.reset, None, [chat, feedback_label, audio_playback])

if __name__ == "__main__":
    demo.launch()