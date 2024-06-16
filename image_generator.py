from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import io
import summarizer

app = Flask(__name__)

# 폰트 경로
font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

def draw_text(draw, text, position, font, max_width, line_spacing):
    """
    주어진 텍스트를 이미지에 그립니다.
    """
    lines = textwrap.wrap(text, width=max_width)
    y = position[1]
    for line in lines:
        width, height = draw.textsize(line, font=font)
        draw.rectangle([position, (position[0] + width, y + height)], fill="black")
        draw.text((position[0], y), line, font=font, fill="white")
        y += height + line_spacing

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    blog_url = request.form['url']
    summarized_text = summarizer.summarize_blog(blog_url, 9)
    return render_template('review.html', summarized_text=summarized_text)

@app.route('/generate', methods=['POST'])
def generate_image():
    summarized_text = request.form.getlist('summarized_text')
    font_size = int(request.form['font_size'])
    font = ImageFont.truetype(font_path, size=font_size)
    images = []

    for i, text in enumerate(summarized_text):
        # 새로운 이미지 생성
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 텍스트 줄간격 설정 (기존 줄간격의 2배)
        line_spacing = font_size

        # 텍스트 그리기
        draw_text(draw, text, (10, 10), font, max_width=60, line_spacing=line_spacing)

        # 이미지 저장
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        images.append(output)

    return render_template('result.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
