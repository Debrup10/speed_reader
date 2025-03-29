import streamlit as st
import time
from textblob import TextBlob
import numpy as np
from PyPDF2 import PdfReader
import io

def split_text_into_chunks(text, words_per_chunk, separator=None):
    """Split text into chunks of specified number of words or by separator."""
    if separator:
        # Split by separator and clean up
        sentences = [s.strip() for s in text.split(separator) if s.strip()]
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            if current_word_count + len(sentence_words) <= words_per_chunk:
                current_chunk.append(sentence)
                current_word_count += len(sentence_words)
            else:
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = len(sentence_words)
        
        if current_chunk:
            chunks.append(separator.join(current_chunk))
    else:
        # Original word-based splitting
        words = text.split()
        chunks = [' '.join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
    
    return chunks

def display_text_chunk(chunk, font_size, text_color, background_color):
    """Display a chunk of text with specified styling."""
    st.markdown(
        f'<div style="font-size: {font_size}px; color: {text_color}; '
        f'background-color: {background_color}; padding: 40px; '
        f'border-radius: 10px; text-align: center; '
        f'min-height: 200px; display: flex; align-items: center; '
        f'justify-content: center; margin: 20px 0;">{chunk}</div>',
        unsafe_allow_html=True
    )

def extract_text_from_pdf(pdf_file, page_number):
    """Extract text from a specific page of a PDF file."""
    try:
        pdf_reader = PdfReader(pdf_file)
        if page_number < 0 or page_number >= len(pdf_reader.pages):
            return None
        page = pdf_reader.pages[page_number]
        return page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def main():
    st.title("Speed Reader")
    st.write("Customize your reading experience and improve your reading speed!")

    # Sidebar for customization options
    st.sidebar.header("Customization Options")
    
    # Reading speed (words per minute)
    wpm = st.sidebar.slider("Reading Speed (WPM)", 100, 1000, 300, 50)
    
    # Words per chunk
    words_per_chunk = st.sidebar.slider("Words per Chunk", 1, 5, 2)
    
    # Font size
    font_size = st.sidebar.slider("Font Size", 20, 60, 30)
    
    # Color options
    text_color = st.sidebar.color_picker("Text Color", "#000000")
    background_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
    
    # Separator option
    separator = st.sidebar.selectbox(
        "Split by",
        ["Words", "Sentences (.)", "Paragraphs (\\n)"],
        index=0
    )
    
    # Map selection to actual separator
    separator_map = {
        "Words": None,
        "Sentences (.)": ".",
        "Paragraphs (\\n)": "\n"
    }
    selected_separator = separator_map[separator]

    # Input method selection
    input_method = st.radio("Choose input method:", ["Text Input", "PDF File"])

    if input_method == "Text Input":
        # Text input
        text = st.text_area("Enter your text here:", height=200)
    else:
        # PDF file upload
        pdf_file = st.file_uploader("Upload PDF file", type=['pdf'])
        if pdf_file:
            # Get PDF info
            pdf_reader = PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            st.write(f"Total pages: {num_pages}")
            
            # Page selection
            page_number = st.number_input("Select page number", min_value=0, max_value=num_pages-1, value=0)
            
            # Extract text from selected page
            text = extract_text_from_pdf(pdf_file, page_number)
            if text:
                st.write(f"Text from page {page_number + 1}:")
                st.text_area("Preview:", text, height=200)
    
    if st.button("Start Reading"):
        if not text:
            st.warning("Please enter some text or upload a PDF file!")
            return

        # Split text into chunks
        chunks = split_text_into_chunks(text, words_per_chunk, selected_separator)
        
        # Calculate delay between chunks based on WPM
        delay = 60 / wpm  # seconds per word
        
        # Create a placeholder for the text display
        ph = st.empty()
        
        # Display chunks with specified delay
        for i, chunk in enumerate(chunks):
            visible_chunks = chunks[max(0, i-1):i+1]
            # Clear previous content
            ph.markdown(
        f"""
        <div style='background-color: {background_color}; padding: 40px; 
                    border-radius: 10px; text-align: center; color: {text_color};
                    min-height: 200px; display: flex; align-items: center;
                    justify-content: center; margin: 20px 0;'>
            {" ".join(visible_chunks)}
        </div>
        """,
        unsafe_allow_html=True
    )
           
    
            if selected_separator != "Words":
                time.sleep(delay * len(chunks[i].split(" ")))
            else:
                time.sleep(delay*words_per_chunk)

if __name__ == "__main__":
    main() 