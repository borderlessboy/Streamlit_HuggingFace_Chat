"""Main application entry point for HuggingFace Inference Chat."""

import os
import uuid
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from api.huggingface import HuggingFaceAPI
from config.settings import DEFAULT_MODEL
from utils.logger import setup_logger
from ui.streamlit_ui import setup_page_style, setup_sidebar, handle_user_input

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


def initialize_session_state():
    """Initialize Streamlit session state with default values."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main() -> None:
    """Main application function."""
    try:
        # Get API token
        api_token = os.getenv("HUGGING_FACE_API_TOKEN")
        if not api_token:
            st.error(
                "⚠️ HuggingFace API token not found. Please set HUGGING_FACE_API_TOKEN in .env file."
            )
            return

        # Initialize API client
        model_name = os.getenv("DEFAULT_MODEL", DEFAULT_MODEL)
        hf_api = HuggingFaceAPI(model_name, api_token)

        # Initialize session state
        initialize_session_state()

        # Setup page style
        setup_page_style()

        # Main chat interface
        st.title("🤗 HuggingFace Inference Chat")

        # Setup sidebar and get uploaded file
        uploaded_file = setup_sidebar(hf_api)

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if "file" in message:
                    st.markdown(f"📎 Attached file: {message['file']}")
                st.markdown(message["content"], unsafe_allow_html=True)

        # Handle user input
        if prompt := st.chat_input("Ask me anything..."):
            handle_user_input(prompt, uploaded_file, hf_api)

    except Exception as e:
        logger.error("Application error: %s", e)
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
