
import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os
import io

load_dotenv()

st.set_page_config(
    page_title="Smart PDF AI Assistant",
    page_icon="📚",
    layout="wide"
)

# AI Connection
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key missing. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# Session Storage
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_names" not in st.session_state:
    st.session_state.pdf_names = []

# Custom Design
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #183153;
}
.stButton button {
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("📚 Smart PDF AI Assistant")
st.caption("Upload documents • Ask questions • Generate summaries • Learn with AI")

st.divider()

# Sidebar
with st.sidebar:
    st.title("⚙️ Dashboard")

    st.write("**Your Features**")
    st.write("📄 Multiple PDF Upload")
    st.write("💬 AI Chat Assistant")
    st.write("📝 Smart Summary")
    st.write("🧠 MCQ Generator")
    st.write("📖 Page References")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔄 Reset Documents", use_container_width=True):
        st.session_state.pdf_text = ""
        st.session_state.pdf_names = []
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Google Gemini AI")

# PDF Upload
st.subheader("📂 Upload Your Documents")

uploaded_files = st.file_uploader(
    "Select one or multiple PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    combined_text = ""
    names = []

    for uploaded_file in uploaded_files:
        names.append(uploaded_file.name)

        reader = PdfReader(uploaded_file)

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            combined_text += (
                f"\n[Document: {uploaded_file.name} | Page: {page_number}]\n"
                f"{text}\n"
            )

    if names != st.session_state.pdf_names:
        st.session_state.pdf_text = combined_text
        st.session_state.pdf_names = names
        st.session_state.messages = []

    st.success("PDF documents uploaded successfully!")

    st.write("**Uploaded Documents:**")
    for name in names:
        st.write("📄 " + name)

# Main Features
if st.session_state.pdf_text:

    st.divider()

    col1, col2 = st.columns(2)

    # Summary
    with col1:
        if st.button("📝 Generate Summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
                    Create a clear and detailed summary of these PDF documents.
                    Use headings and bullet points.

                    DOCUMENTS:
                    {st.session_state.pdf_text[:50000]}
                    """
                )

                st.session_state.summary = response.text

    # MCQ Generator
    with col2:
        if st.button("🧠 Generate 5 MCQs", use_container_width=True):
            with st.spinner("Creating questions..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
                    Create 5 multiple choice questions from these documents.
                    Give four options for each question and mark the correct answer.
                    Do not use information outside the documents.

                    DOCUMENTS:
                    {st.session_state.pdf_text[:50000]}
                    """
                )

                st.session_state.mcqs = response.text

    # Display Summary
    if "summary" in st.session_state:
        st.subheader("📋 Document Summary")
        st.markdown(st.session_state.summary)

        st.download_button(
            "⬇️ Download Summary",
            data=st.session_state.summary,
            file_name="PDF_Summary.txt",
            mime="text/plain"
        )

    # Display MCQs
    if "mcqs" in st.session_state:
        st.subheader("🧠 AI Generated MCQs")
        st.markdown(st.session_state.mcqs)

    st.divider()

    # Chat Assistant
    st.subheader("💬 Ask Questions From Your PDF")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask anything about your documents...")

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("AI is reading your documents..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
                    You are a helpful PDF assistant.

                    Answer the question using ONLY the provided documents.

                    Important instructions:
                    1. Give simple and clear answers.
                    2. Mention the document name and page number
                       when the relevant page is identifiable.
                    3. If information is missing, say it is not
                       available in the uploaded documents.
                    4. Never invent page references.

                    DOCUMENTS:
                    {st.session_state.pdf_text[:50000]}

                    QUESTION:
                    {question}
                    """
                )

                answer = response.text
                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

else:
    st.info("👆 Please upload a PDF to start using your AI Assistant.")

    st.markdown("""
    ### Welcome to Smart PDF AI Assistant!

    - Upload your study documents.
    - Generate AI summaries.
    - Create MCQs automatically.
    - Ask questions from your PDFs.
    - View your chat history.
    """)
