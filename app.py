import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="CAB Interview Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        padding-bottom: 10px;
        border-bottom: 2px solid #E5E7EB;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# System Prompt for "Mark" Scenario
SYSTEM_PROMPT = """
You are acting as 'Mark', a client visiting a Citizen's Advice Bureau (CAB) in New Zealand.
You are seeking advice regarding a dispute with your landlord, who is refusing to return your tenancy bond of $1,800.

Your Persona:
- Slightly stressed, polite, but frustrated about your money being held.
- You moved out 3 weeks ago after living in a flat in Lower Hutt for 2 years.
- The landlord claims there is damage to the lounge carpet and cleaning required, but you believe it is just fair wear and tear.
- You have photos from when you moved out.
- You do not know the exact process for applying to the Tenancy Tribunal or how the Bond Centre works.

Instructions for AI:
1. Stay in character at all times as Mark.
2. Respond naturally to the user's questions as a CAB volunteer interviewer.
3. Provide details when asked, but don't dump all information at once—let the volunteer ask good clarifying questions.
4. Keep responses concise (2-4 sentences per response).
"""

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Kia ora. My name is Mark. I was told I could get some help here regarding a issue with my landlord and my bond?"}
    ]

if "notes" not in st.session_state:
    st.session_state.notes = {
        "client_name": "Mark",
        "category": "Tenancy / Housing",
        "key_issues": "",
        "action_taken": ""
    }

# Sidebar - Settings & API Key
with st.sidebar:
    st.title("⚙️ Simulator Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    st.markdown("---")
    st.subheader("📋 Volunteer Guidance")
    st.info("""
    **Goal:** Conduct an intake interview with Mark.
    1. Identify key facts of the tenancy dispute.
    2. Document findings in the CAB Report Form on the right.
    3. Outline clear next steps for Mark.
    """)

# Main Layout Split
col1, col2 = st.columns([1, 1])

# Left Column: Interactive Chat Interface
with col1:
    st.markdown('<div class="main-header">💬 Client Interview (Mark)</div>', unsafe_allow_html=True)
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User Input Field
    user_input = st.chat_input("Type your response or question to Mark...")

    if user_input:
        if not api_key:
            st.error("Please enter your Gemini API Key in the left sidebar to chat with Mark.")
        else:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

         # Generate Gemini Response
            try:
                genai.configure(api_key=api_key)

                # Dynamically fetch available generation models for your API key
                available_models = [
                    m.name for m in genai.list_models()
                    if "generateContent" in m.supported_generation_methods
                ]
                
                # Pick the best available Flash model, or fall back to the first supported model
                chosen_model = next((m for m in available_models if "flash" in m.lower()), available_models[0])

                model = genai.GenerativeModel(chosen_model, system_instruction=SYSTEM_PROMPT)

                # Format history for Gemini
                formatted_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    formatted_history.append({"role": role, "parts": [msg["content"]]})

                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(user_input)

                # Append assistant response
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                with st.chat_message("assistant"):
                    st.write(response.text)

            except Exception as e:
                st.error(f"Error connecting to Gemini API: {str(e)}")
# Right Column: CAB Database Intake Form
with col2:
    st.markdown('<div class="main-header">📝 CAB Client Record Form</div>', unsafe_allow_html=True)
    
    st.text_input("Client Name", value=st.session_state.notes["client_name"], disabled=True)
    st.text_input("Enquiry Category", value=st.session_state.notes["category"], disabled=True)
    
    st.session_state.notes["key_issues"] = st.text_area(
        "Key Facts & Client Circumstances",
        value=st.session_state.notes["key_issues"],
        height=150,
        placeholder="Record key details here as you interview Mark..."
    )
    
    st.session_state.notes["action_taken"] = st.text_area(
        "Options & Advice Provided",
        value=st.session_state.notes["action_taken"],
        height=150,
        placeholder="Record advice, Tenancy Services info, or Tribunal steps shared with Mark..."
    )

    if st.button("Save Record"):
        st.success("Intake Record saved successfully!")
