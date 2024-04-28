import pandas as pd
from io import BytesIO
import re
import streamlit as st
import tiktoken
from typing import Tuple

def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    # Remove extra spaces and newlines
    text = re.sub(r"\s*\n\s*", " ", text)
    return text

def parse_pdf(file: BytesIO) -> str:
    def trim(text):
        # Combine hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Remove extra spaces and newlines
        text = re.sub("\s*\n\s*", " ", text)
        return text
    doc = fitz.open(stream=file.read(), filetype="pdf")
    total_pages = doc.page_count
    text_list = []

    for page in range(total_pages):
        text = doc.load_page(page).get_text()
        text = trim(text)
        text_list.append(text)

    doc.close()
    return "".join(text_list)

def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    # Remove extra spaces and newlines
    text = re.sub(r"\s*\n\s*", " ", text)
    return text

def parse_xlsx(file: BytesIO) -> str:
    df = pd.read_excel(file)  # Read the Excel file into a pandas DataFrame
    # Assuming the data is in a single column (e.g., 'text') of the DataFrame
    text = ' '.join(df['text'].astype(str))  # Join all rows in the 'text' column into a single string
    # Remove extra spaces and newlines
    text = re.sub(r"\s*\n\s*", " ", text)
    return text

def count_tokens(text: str) -> Tuple[str, int]:
    model = st.session_state.get("MODEL")
    prompt = st.session_state.get("PROMPT")
    
    total = prompt + text
    price = 0
    
    enc = tiktoken.encoding_for_model(model)
    length = len(enc.encode(total))
    
    model_price_pairs = {
        'gpt-3.5-turbo-0613': 0.0015,
        'gpt-3.5-turbo-1106': 0.001,
        'gpt-3.5-turbo': 0.0005,
        'gpt-3.5-turbo-16k': 0.003,
        'gpt-4-8k': 0.003,
        'gpt-4-32k': 0.006,
        'gpt-4-turbo-preview': 0.001,
        'ada': 0.0004,
        'babbage': 0.0005,
        'curie': 0.002,
        'davinci': 0.02
    }
    
    price = (int(length) / 1000) * model_price_pairs[model] 
    
    return length, price
