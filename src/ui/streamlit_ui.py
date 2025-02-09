"""Streamlit UI components and handlers."""

from typing import Any, Optional

import streamlit as st

from api.huggingface import HuggingFaceAPI
from config.settings import SUPPORTED_FILE_TYPES
from utils.file_handler import process_uploaded_file
from utils.logger import setup_logger
from utils.message_formatter import format_code_in_message

logger = setup_logger(__name__)


def setup_page_style() -> None:
    """Configure page styling."""
    # Set page title and icon
    st.set_page_config(
        page_title="🤗 HuggingFace Inference Chat",
        page_icon="🤗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <!-- Add Prism.js CSS and JS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-cpp.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>

        <style>
        /* Main chat container */
        .stChatFloatingInputContainer {
            bottom: 20px;
            background: transparent;
        }
        
        /* Message styles */
        .chat-message {
            padding: 1rem 1.5rem;
            margin-bottom: 0.5rem;
            line-height: 1.5;
            font-size: 1rem;
        }
        
        .user-message {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
        }
        
        .assistant-message {
            background-color: white;
            border-left: 4px solid #10a37f;
            border-radius: 0;
        }
        
        /* Code block styling */
        .code-block {
            padding: 1rem;
            border-radius: 0.375rem;
            margin: 0.75rem 0;
            font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, monospace;
            font-size: 0.875rem;
            line-height: 1.5;
            overflow-x: auto;
            position: relative;
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
        }

        /* Code block header */
        .code-block::before {
            content: attr(data-language);
            display: block;
            background: #333;
            color: #fff;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            border-radius: 0.25rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
        }

        /* Prism.js theme overrides */
        .code-block pre[class*="language-"] {
            margin: 0;
            padding: 0;
            background: transparent;
        }

        .code-block code[class*="language-"] {
            font-family: inherit;
            font-size: inherit;
            text-shadow: none;
        }
        </style>

        <!-- Initialize Prism.js -->
        <script>
            // Function to initialize Prism highlighting
            function highlightCode() {
                if (typeof Prism !== 'undefined') {
                    Prism.highlightAll();
                }
            }

            // Create observer to watch for new code blocks
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.addedNodes.length) {
                        highlightCode();
                    }
                });
            });

            // Start observing content changes
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        </script>
        """,
        unsafe_allow_html=True,
    )


def setup_sidebar(hf_api: HuggingFaceAPI) -> Optional[Any]:
    """Setup sidebar components."""
    st.sidebar.title("Settings")

    # Token counters
    st.sidebar.markdown("### Token Usage")
    token_cols = st.sidebar.columns(2)

    # Get token counts from session state, default to 0
    sent_tokens = st.session_state.get("total_tokens_sent", 0)
    received_tokens = st.session_state.get("total_tokens_received", 0)

    with token_cols[0]:
        st.metric(
            "Tokens Sent",
            f"{sent_tokens:,}",
            help="Total number of tokens sent to the API",
        )
    with token_cols[1]:
        st.metric(
            "Tokens Received",
            f"{received_tokens:,}",
            help="Total number of tokens received from the API",
        )

    st.sidebar.markdown("---")

    # Model parameters
    st.sidebar.subheader("Model Parameters")

    # Temperature
    st.session_state.temperature = st.sidebar.slider(
        "Temperature",
        0.0,
        1.0,
        st.session_state.get("temperature", 0.7),
        0.1,
        help="""
        Controls randomness in the output.
        - Higher (1.0): More creative but less focused
        - Lower (0.0): More deterministic and focused
        """,
    )

    # Top P
    st.session_state.top_p = st.sidebar.slider(
        "Top P",
        0.0,
        1.0,
        st.session_state.get("top_p", 0.9),
        0.1,
        help="""
        Controls diversity via nucleus sampling.
        - Higher: More diverse outputs
        - Lower: More focused on likely tokens
        """,
    )

    # Max Tokens
    st.session_state.max_tokens = st.sidebar.slider(
        "Max Tokens",
        64,
        2048,
        st.session_state.get("max_tokens", 1024),
        64,
        help="""
        Maximum length of the generated response.
        - Higher: Longer responses but slower
        - Lower: Shorter, quicker responses
        """,
    )

    # Repetition Penalty
    st.session_state.rep_penalty = st.sidebar.slider(
        "Repetition Penalty",
        1.0,
        2.0,
        st.session_state.get("rep_penalty", 1.1),
        0.1,
        help="""
        Penalizes repetition in the output.
        - Higher: Less repetition but potentially less coherent
        - Lower: More natural but might repeat more
        """,
    )

    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload a file",
        type=["py", "js", "java", "cpp", "txt", "md"],
        help="""
        Upload code files for analysis.
        Supported types: Python, JavaScript, Java, C++, Text, Markdown
        Max size: 5MB
        """,
    )

    # Clear chat button
    if st.sidebar.button(
        "Clear Chat",
        help="Clear all chat history and start fresh",
    ):
        st.session_state.messages = []
        st.rerun()

    return uploaded_file


def handle_user_input(
    prompt: str, uploaded_file: Optional[Any], hf_api: HuggingFaceAPI
) -> None:
    """Handle user input and generate response."""
    # Display user message
    with st.chat_message("user"):
        if uploaded_file:
            st.markdown(f"📎 Uploaded file: `{uploaded_file.name}`")
        st.markdown(prompt)

    # Add to message history
    message_content = prompt
    if uploaded_file:
        file_content = uploaded_file.getvalue().decode()
        message_content = f"{prompt}\n\nFile contents:\n```\n{file_content}\n```"

    st.session_state.messages.append({"role": "user", "content": message_content})

    # Generate and display response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        cursor = "▌"

        # Create placeholders for token counters
        tokens_sent_placeholder = st.sidebar.empty()
        tokens_received_placeholder = st.sidebar.empty()

        # Store initial token counts
        initial_sent = st.session_state.get("total_tokens_sent", 0)
        initial_received = st.session_state.get("total_tokens_received", 0)

        # Stream the response
        for response_chunk in hf_api.generate_stream(message_content):
            if response_chunk:
                full_response += response_chunk
                formatted_response = format_code_in_message(full_response)
                message_placeholder.markdown(
                    formatted_response + cursor, unsafe_allow_html=True
                )

        if full_response.strip():
            # Remove cursor for final response
            formatted_response = format_code_in_message(full_response)
            message_placeholder.markdown(formatted_response, unsafe_allow_html=True)
            st.session_state.messages.append(
                {"role": "assistant", "content": formatted_response}
            )

            # Force UI update for token counters
            st.rerun()
        else:
            message_placeholder.markdown(
                "I apologize, but I couldn't generate a response. Please try again."
            )
