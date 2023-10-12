from flask import Flask, request, render_template, session
from werkzeug.utils import secure_filename
import replicate
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'  # replace 'secret' with a real secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        filename = secure_filename(file.filename)
        file.save('static/images/' + filename)
        session['filename'] = filename
        return render_template('index.html', filename=filename)

@app.route('/submit', methods=['POST'])
def submit():    
    filename = session.get('filename')
    if filename is None:
        return 'No image uploaded'
    question = request.form.get('question') 
    print(question)
    with open('static/images/' + filename, "rb") as image_file:
        output = replicate.run(
            'salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746',
            input={'image': image_file, 
                   'task' : "visual_question_answering",
                   'question': question}
        )
    return render_template('index.html', filename=filename, output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)