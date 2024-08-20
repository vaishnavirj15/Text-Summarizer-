import streamlit as st
from transformers import pipeline
from newspaper import Article
from fpdf import FPDF, HTMLMixin
import base64
import sentencepiece

# Custom PDF class
class MyFPDF(FPDF, HTMLMixin):
    pass


# Function to convert text to PDF
def convert_to_pdf(text):
    pdf = MyFPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
    pdf_output = "output.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Function to convert text to text file
def convert_to_text(text):
    text_file = "output.txt"
    with open(text_file, "w", encoding='utf-8') as file:
        file.write(text)
    return text_file

# Function to generate download link for files
def get_binary_file_downloader_html(bin_file, file_label):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">Download {file_label}</a>'
    return href

# Custom CSS styles
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #032c40;
    }
    footer {
        visibility: hidden;
    }
    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #808080;
        text-align: center;
        padding: 10px;
        font-size: 16px;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar content
st.sidebar.title("Article Summarizer and Translator")
summary_type = st.sidebar.radio("Choose the task ", ["Summarization", "Translation"])

# Summarization section
if summary_type == "Summarization":
    st.title("Article Summarizer")

    pipe = pipeline("summarization",model="t5-small")

    summary_type = st.radio("Summarize from:", ["Text Input", "URL"])
    max_length = st.slider("Maximum Summary Length:", min_value=50, max_value=500, value=300)
    min_length = st.slider("Minimum Summary Length:", min_value=30, max_value=300, value=100)

    if summary_type == "Text Input":
        input_text = st.text_area("Enter text to summarize:", height=150)
        if st.button("Summarize"):
            if input_text:
                truncated_text = input_text[:512]
                try:
                    with st.spinner('Summarizing...'):
                        pipe_out = pipe(truncated_text, max_length=max_length, min_length=min_length, clean_up_tokenization_spaces=True)
                    summary = pipe_out[0]["summary_text"]
                    st.write("Summary:")
                    st.write(summary)
                    pdf_file = convert_to_pdf(summary)
                    text_file = convert_to_text(summary)
                    st.markdown(get_binary_file_downloader_html(pdf_file, "Summary as PDF"), unsafe_allow_html=True)
                    st.markdown(get_binary_file_downloader_html(text_file, "Summary as Text"), unsafe_allow_html=True)
                except Exception as e:
                    st.error("Error summarizing the text. Please try again.")
                    st.error(str(e))

    elif summary_type == "URL":
        url = st.text_input("Enter URL to summarize:")
        if st.button("Fetch and Summarize"):
            if url and url.startswith(("http://", "https://")):
                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                    input_text = article.text[:512]
                    with st.spinner('Summarizing...'):
                        pipe_out = pipe(input_text, max_length=max_length, min_length=min_length, clean_up_tokenization_spaces=True)
                    summary = pipe_out[0]["summary_text"]
                    st.write("Summary:")
                    st.write(summary)
                    pdf_file = convert_to_pdf(summary)
                    text_file = convert_to_text(summary)
                    st.markdown(get_binary_file_downloader_html(pdf_file, "Summary as PDF"), unsafe_allow_html=True)
                    st.markdown(get_binary_file_downloader_html(text_file, "Summary as Text"), unsafe_allow_html=True)
                except Exception as e:
                    st.error("Error fetching or summarizing the article. Please try again.")
                    st.error(str(e))
            else:
                st.warning("Please enter a valid URL (starting with http:// or https://).")

# Translation section
elif summary_type == "Translation":
    st.title("Text Translator")

    source_lang = st.selectbox('Select the source language', ['en', 'fr', 'hi'])
    target_lang = st.selectbox('Select the target language', ['en', 'fr', 'hi'])

    model_map = {
        ('en', 'fr'): "Helsinki-NLP/opus-mt-en-fr",
        ('en', 'hi'): "Helsinki-NLP/opus-mt-en-hi",
        ('fr', 'en'): "Helsinki-NLP/opus-mt-fr-en",
        ('hi', 'en'): "Helsinki-NLP/opus-mt-hi-en",
        ('hi', 'fr'): "Helsinki-NLP/opus-mt-hi-fr",
        ('fr', 'hi'): "Helsinki-NLP/opus-mt-fr-hi"
    }

    if (source_lang, target_lang) in model_map:
        model_name = model_map[(source_lang, target_lang)]
    else:
        model_name = "Helsinki-NLP/opus-mt-en-hi"

    st.write("Source Language:", source_lang)
    st.write("Target Language:", target_lang)

    translator = pipeline("translation", model=model_name)

    input_text = st.text_area("Enter text to translate:", height=150)
    if st.button("Translate"):
        if input_text:
            try:
                with st.spinner('Translating...'):
                    translation = translator(input_text)[0]["translation_text"]
                st.write("Translation:")
                st.write(translation)
                pdf_file = convert_to_pdf(translation)
                text_file = convert_to_text(translation)
                st.markdown(get_binary_file_downloader_html(pdf_file, "Translation as PDF"), unsafe_allow_html=True)
                st.markdown(get_binary_file_downloader_html(text_file, "Translation as Text"), unsafe_allow_html=True)
            except Exception as e:
                st.error("Error translating the text. Please try again.")
                st.error(str(e))

# Footer
st.markdown(
    """
    <div class="custom-footer">
        @created by Vaishnavi
    </div>
    """,
    unsafe_allow_html=True,
)
