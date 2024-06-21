# Streamlit app for interacting with a fine-tuned OpenAI model, including chat history management.
import os

import streamlit as st
from openai import OpenAI

# Assuming the OpenAI API key is correctly configured.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def send_prompt_to_model(messages):
    """Send the conversation history as a prompt to the model and get the response."""
    completion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::97QirxUL",  # Your fine-tuned model's name
        messages=messages
    )
    # Correctly accessing the message content from the completion object.
    return completion.choices[0].message.content


# Initialize chat history if it's not already in the session state.
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = [
        {"role": "system",
         "content": "You are a tutor for students that are learning a business administration course."}
    ]


def app():
    # UI for chat display
    st.title("Tutor Chatbot")
    for message in st.session_state['chat_history']:
        if message['role'] == 'user':
            st.text_area("You", value=message['content'], height=75, key=message['content'] + "_user")
        else:  # model response
            st.text_area("Bot", value=message['content'], height=75, key=message['content'] + "_bot")

    # Create a placeholder for the input field
    input_placeholder = st.empty()

    # Input for new message
    user_message = input_placeholder.text_input("Your message", key="user_message")

    # Send message button
    if st.button('Send'):
        if user_message:  # Ensure the message is not empty
            # Add user message to chat history
            st.session_state['chat_history'].append({"role": "user", "content": user_message})

            # Get model response
            model_response = send_prompt_to_model(st.session_state['chat_history'])

            # Add model response to chat history
            st.session_state['chat_history'].append({"role": "system", "content": model_response})

            # Clear the input field by re-creating the text input widget in the placeholder
            input_placeholder.text_input("Your message", value="", key="user_message_next")

            # Scroll to the last message
            st.experimental_rerun()
        else:
            st.warning("Please enter a message.")


if __name__ == '__main__':
    app()

