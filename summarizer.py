import requests
from bs4 import BeautifulSoup
from google.cloud import language_v1
import os

# Google Cloud Language API 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/jaehunlee/Downloads/amplified-grail-426504-k8-fe1e47809d84.json"

def fetch_blog_text(blog_url):
    response = requests.get(blog_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    blog_text = ' '.join([para.text for para in paragraphs])
    return blog_text

def summarize_text_with_gemini(text, num_sentences=9):
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_syntax(document=document)

    sentences = [sentence.text.content for sentence in response.sentences]
    summarized = sentences[:num_sentences]
    return summarized

def summarize_blog(blog_url, num_sentences=9):
    blog_text = fetch_blog_text(blog_url)
    summary = summarize_text_with_gemini(blog_text, num_sentences)
    return summary

if __name__ == '__main__':
    blog_url = input("Enter the blog URL: ")
    summary = summarize_blog(blog_url)
    for sentence in summary:
        print(sentence)
