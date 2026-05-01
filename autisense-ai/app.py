import os
from groq import Groq
import gradio as gr
from dotenv import load_dotenv

# 1. Setup & Environment
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

client = Groq(api_key=api_key)

# 2. System Instructions
SHOPKEEPER_PROMPT = """
You are a friendly shopkeeper. A child is practicing buying something.
Rules:
- Use simple English.
- Be friendly.
- Ask questions to continue the conversation.
- Keep responses very short (1–2 sentences).
"""

# 3. Phase 2: Feedback Logic
def generate_feedback(user_input):
    """Analyzes user behavior and returns one simple coaching tip."""
    text = user_input.lower().strip()
    
    # Check for Politeness
    if "please" not in text and "thank" not in text:
        return "Try saying 'please' to be more polite 🙏"
    
    # Check for Clarity (Length)
    words = text.split()
    if len(words) < 3:
        return "Try using a full sentence like 'I want an apple' 😊"
    
    # Check for Question Asking (Engagement)
    if "?" not in text:
        return "Good job! Next time, try asking the shopkeeper a question. ❓"
    
    # Default Positive Reinforcement
    return "Great job being polite and clear! 👍"

# 4. Core Logic Function
def handle_interaction(user_input, history):
    if not user_input.strip():
        return "", history, ""

    # Generate coaching feedback first
    feedback = generate_feedback(user_input)

    # Prepare AI Response
    messages = [{"role": "system", "content": SHOPKEEPER_PROMPT}]
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )
        ai_response = completion.choices[0].message.content
        
        # Update History
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": ai_response})
        
        # Return: Clear input, Update Chatbot, Update Feedback Label
        return "", history, feedback 

    except Exception as e:
        print(f"Error: {e}")
        history.append({"role": "assistant", "content": "I'm sorry, I'm having a little trouble. Can you try again?"})
        return "", history, "Error getting feedback."

# 5. UI Layout (Gradio 6.0+)
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 AutiSense AI (Phase 2)")
    gr.Markdown("Practice your shopping skills and get helpful tips from your AI coach!")

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="Shop Counter", height=400)
            user_input = gr.Textbox(
                label="Type your message here...", 
                placeholder="e.g., 'Hello!', 'I want an apple.'"
            )
        
        with gr.Column(scale=1):
            feedback_box = gr.Label(label="Coaching Feedback", value="Start talking to see tips!")

    # Connect the interaction
    user_input.submit(
        handle_interaction, 
        inputs=[user_input, chatbot], 
        outputs=[user_input, chatbot, feedback_box]
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())