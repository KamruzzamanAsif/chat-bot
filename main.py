import streamlit as st
import openai
import base64
import os
from datetime import datetime

# Initialize OpenAI client (replace with your API key)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Function to encode image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Function to process uploaded files
def process_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension in ['.png', '.jpg', '.jpeg']:
        return {"type": "image", "content": encode_image(file)}
    else:
        return {"type": "text", "content": file.read().decode('utf-8', errors='ignore')}

# Streamlit app layout
st.title("Grok-like Chatbot with File Upload")
st.write("Upload images or text files and chat with the bot. Conversation context is maintained.")

# File uploader
uploaded_file = st.file_uploader("Upload an image or text file", type=['png', 'jpg', 'jpeg', 'txt', 'pdf'], accept_multiple_files=False)

# Process uploaded file
if uploaded_file:
    file_data = process_file(uploaded_file)
    st.session_state.uploaded_files.append({
        "name": uploaded_file.name,
        "type": file_data["type"],
        "content": file_data["content"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    if file_data["type"] == "image":
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
    else:
        st.text_area("File Content", file_data["content"], height=200)

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Prepare messages for OpenAI API
    messages = [{"role": "system", "content": "You are a helpful assistant. Respond to user queries and analyze uploaded files if provided."}]
    
    # Include uploaded files in context
    for file in st.session_state.uploaded_files:
        if file["type"] == "image":
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Uploaded image: {file['name']}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{file['content']}"}}
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Uploaded file {file['name']} content: {file['content']}"
            })
    
    # Add conversation history
    messages.extend(st.session_state.messages)
    
    # Call OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )
        assistant_response = response.choices[0].message.content
    except Exception as e:
        assistant_response = f"Error: {str(e)}"
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # Display user and assistant messages
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.session_state.uploaded_files = []
    st.experimental_rerun()