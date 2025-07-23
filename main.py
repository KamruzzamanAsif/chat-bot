import streamlit as st
import openai
import base64
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Tutor - Bangladesh",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean design
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 50%, #0d9488 100%);
        min-height: 100vh;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }

    .app-title {
        text-align: center;
        color: #0f766e;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .app-subtitle {
        text-align: center;
        color: #14b8a6;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #14b8a6, #0d9488);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(20, 184, 166, 0.35);
    }

    @media (max-width: 768px) {
        .main-container {
            margin: 1rem;
            padding: 1rem;
        }

        .app-title {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# OpenAI API Key
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "selected_class" not in st.session_state:
    st.session_state.selected_class = "প্রথম শ্রেণী"
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "বাংলা"

# Sidebar selection
with st.sidebar:
    st.markdown("### 🏫 শ্রেণী ও বিষয় নির্বাচন")
    st.session_state.selected_class = st.selectbox(
        "শ্রেণী নির্বাচন করুন",
        ["প্রথম শ্রেণী", "দ্বিতীয় শ্রেণী", "তৃতীয় শ্রেণী", "চতুর্থ শ্রেণী", 
         "পঞ্চম শ্রেণী", "ষষ্ঠ শ্রেণী", "সপ্তম শ্রেণী", "অষ্টম শ্রেণী", 
         "নবম শ্রেণী", "দশম শ্রেণী"],
        index=0
    )

    st.session_state.selected_subject = st.selectbox(
        "বিষয় নির্বাচন করুন",
        ["বাংলা", "ইংরেজি", "গণিত", "বিজ্ঞান", "সামাজিক বিজ্ঞান", 
         "ধর্ম ও নৈতিক শিক্ষা", "শিল্প ও সংস্কৃতি"],
        index=0
    )

# Encode image for API
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Process file
def process_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension in ['.png', '.jpg', '.jpeg']:
        return {"type": "image", "content": encode_image(file)}
    else:
        return {"type": "text", "content": file.read().decode('utf-8', errors='ignore')}

# Main UI
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="app-title">🔰 AI শিক্ষক</div>
    <div class="app-subtitle">বাংলাদেশের স্মার্ট শিক্ষা সহায়ক</div>
    """, unsafe_allow_html=True)

    st.markdown("### 💬 কথোপকথন")

    # Display chat history
    with st.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("আপনার প্রশ্ন এখানে লিখুন... 💭")

    # File uploader below input
    st.markdown("#### 📎 ফাইল আপলোড করুন (ছবি বা টেক্সট)")
    uploaded_file = st.file_uploader(
        "আপনার ফাইল দিন (png, jpg, jpeg, txt, pdf)", 
        type=['png', 'jpg', 'jpeg', 'txt', 'pdf'], 
        accept_multiple_files=False,
        key="file_upload"
    )

    # Handle uploaded file
    if uploaded_file:
        file_data = process_file(uploaded_file)
        st.session_state.uploaded_files.append({
            "name": uploaded_file.name,
            "type": file_data["type"],
            "content": file_data["content"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if file_data["type"] == "image":
            st.image(uploaded_file, caption=f"📸 {uploaded_file.name}", use_container_width=True)
        else:
            with st.expander(f"📄 {uploaded_file.name} এর বিষয়বস্তু"):
                st.text_area("", file_data["content"], height=200, disabled=True)

        st.success(f"✅ {uploaded_file.name} সফলভাবে আপলোড হয়েছে!")

    # Chat logic
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        system_message = f"""আপনি একজন বাংলাদেশী AI শিক্ষক। আপনি {st.session_state.selected_class} এর {st.session_state.selected_subject} বিষয়ে সাহায্য করছেন। 
        বাংলায় উত্তর দিন এবং শিক্ষার্থীদের বোঝার উপযোগী করে ব্যাখ্যা করুন। 
        সৃজনশীল এবং আকর্ষণীয় পদ্ধতিতে শেখান।"""

        messages = [{"role": "system", "content": system_message}]

        for file in st.session_state.uploaded_files:
            if file["type"] == "image":
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"আপলোড করা ছবি: {file['name']}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{file['content']}"}}
                    ]
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"আপলোড করা ফাইল {file['name']} এর বিষয়বস্তু: {file['content']}"
                })

        messages.extend(st.session_state.messages)

        try:
            with st.spinner("AI শিক্ষক চিন্তা করছেন... 🤔"):
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                assistant_response = response.choices[0].message.content
        except Exception as e:
            assistant_response = f"দুঃখিত, একটি সমস্যা হয়েছে: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.rerun()

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🗑️ কথোপকথন মুছুন"):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.success("কথোপকথন মুছে ফেলা হয়েছে!")
            st.rerun()

    with col2:
        if st.button("📚 নতুন প্রসঙ্গ"):
            st.session_state.uploaded_files = []
            st.success("নতুন প্রসঙ্গ শুরু হয়েছে!")

    with col3:
        if st.button("ℹ️ সাহায্য"):
            st.info("""
            **কিভাবে ব্যবহার করবেন:**
            1. বাম পাশ থেকে শ্রেণী ও বিষয় নির্বাচন করুন
            2. প্রয়োজনে ছবি বা ফাইল আপলোড করুন  
            3. প্রশ্ন লিখুন এবং এন্টার চাপুন
            4. AI শিক্ষক আপনাকে সাহায্য করবেন!
            """)

    st.markdown('</div>', unsafe_allow_html=True)
