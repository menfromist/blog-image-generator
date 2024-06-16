from flask import Flask, request, render_template
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import io
import summarizer
import base64

app = Flask(__name__)

# 폰트 경로
font_path = "fonts/AppleSDGothicNeo.ttc"

def draw_text(draw, text, position, font, max_width, line_spacing):
    """
    주어진 텍스트를 이미지에 그립니다.
    """
    lines = textwrap.wrap(text, width=max_width)
    y = position[1]
    for line in lines:
        bbox = draw.textbbox(position, line, font=font)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rectangle([position, (position[0] + width, y + height)], fill="black")
        draw.text((position[0], y), line, font=font, fill="white")
        y += height + line_spacing

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    blog_url = request.form['url']
    summarized_text = summarizer.summarize_blog(blog_url
