from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from PIL import Image, ImageDraw, ImageFont
import os
import summarizer  # summarizer 모듈을 가져옴

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "amplified-grail-426504-k8-fe1e47809d84.json"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = 'your_secret_key'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    blog_url = request.form['url']
    image_file = request.files['image']

    if image_file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(image_path)

        summarized_text = summarizer.summarize_blog(blog_url, 9)
        session['summarized_text'] = summarized_text
        session['image_path'] = image_path

        return render_template('review.html', summarized_text=summarized_text)

    return redirect(url_for('home'))

@app.route('/generate', methods=['POST'])
def generate_image():
    summarized_text = request.form.getlist('sentence')
    font_sizes = request.form.getlist('fontsize')
    image_path = session.get('image_path')
    generated_images = []

    for i, (sentence, font_size) in enumerate(zip(summarized_text, font_sizes)):
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # 폰트 크기를 사용자가 지정한 크기로 설정
        font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
        font = ImageFont.truetype(font_path, size=int(font_size))
        
        # 사용자가 지정한 줄바꿈을 그대로 사용
        lines = sentence.split('\n')
        max_width = max(draw.textlength(line, font=font) for line in lines)
        line_height = (draw.textbbox((0, 0), 'A', font=font)[3] - draw.textbbox((0, 0), 'A', font=font)[1]) * 2  # 줄 간격을 두 배로 조정
        total_height = line_height * len(lines)

        # 중앙 위치 계산 (이미지의 중앙에서 텍스트의 절반 너비와 높이를 뺀 위치)
        text_x = (image.width - max_width) / 2
        text_y = (image.height - total_height) / 2

        # 텍스트 배경 그리기 및 텍스트 그리기
        current_y = text_y
        for line in lines:
            bbox = draw.textbbox((text_x, current_y), line, font=font)
            background_position = (bbox[0] - int(int(font_size) * 0.28), bbox[1] - int(int(font_size) * 0.14), bbox[2] + int(int(font_size) * 0.28), bbox[3] + int(int(font_size) * 0.14))
            draw.rectangle(background_position, fill="black")
            draw.text((text_x, current_y), line, font=font, fill="white")
            current_y += line_height

        output_image_filename = f'output_{i+1}_{os.path.basename(image_path)}'
        output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], output_image_filename)
        image.save(output_image_path, quality=95)
        generated_images.append(output_image_filename)

    return render_template('result.html', image_urls=generated_images)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
