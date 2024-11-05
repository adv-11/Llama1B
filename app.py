from huggingface_hub import InferenceClient
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(api_key=os.getenv('HF_TOKEN'))

st.set_page_config(page_title="🦙💬 Llama 3.2 Chatbot")

with st.sidebar:
    st.title('🦙💬 Llama 3.2 Chatbot')
    st.write('This chatbot is created using the open-source Llama 3.2 LLM model from Meta.')
    if os.getenv('HF_TOKEN') != None:
        st.success('API key already provided!', icon='✅')
        HF_TOKEN = os.getenv('HF_TOKEN')
    else:
        HF_TOKEN = st.text_input('Enter HF API token:', type='password')
        if not (HF_TOKEN.startswith('hf_')):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['HF_TOKEN'] = HF_TOKEN

    st.subheader('Models and parameters')
    st.write('Model')
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=20, max_value=80, value=50, step=5)

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if the last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare the messages for the model
            stream = client.chat.completions.create(
                model="meta-llama/Llama-3.2-1B-Instruct",
                messages=st.session_state.messages,
                max_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )
            
            # Placeholder for the response
            placeholder = st.empty()
            full_response = ''

            # Stream the response
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response)

            # Add the final response to the session state
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)