from flask import Flask, request, render_template, session
from werkzeug.utils import secure_filename
from flask_session import Session
import replicate
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

Session(app)

@app.route('/')
def index():
    session.clear()
    chat = session.get('chat', [])
    print(chat)
    return render_template('index.html', chat=chat, filename=session.get('filename'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        filename = secure_filename(file.filename)
        file.save('static/images/' + filename)
        session['filename'] = filename
        return render_template('index.html', filename=filename, chat=[])

@app.route('/submit', methods=['POST'])
def submit():
    chat = session.get('chat', [])
    filename = session.get('filename')
    if filename is None:
        return 'No image uploaded'
    question = request.form.get('question')
    print(question)
    with open('static/images/' + filename, "rb") as image_file:
        output = replicate.run(
            'salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746',
            input={'image': image_file, 
                   'task': "visual_question_answering", 
                   'question': question}
        )
    chat.append({'question': question, 'answer': output})
    session['chat'] = chat
    return render_template('index.html', filename=filename, chat=chat)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
