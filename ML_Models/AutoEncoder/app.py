from flask import Flask, render_template, request
import json

import evaluate

app = Flask(__name__)

@app.route('/vectorize')
def vectorize():
    img_path = request.args.get("img_path", "")
    vector = evaluate.get_img(img_path)
    pred_vector = evaluate.model.predict(vector)
    return '%s' % pred_vector[0]	
    
@app.route('/getImagesScores')
def getImagesScores():
    img1_path = request.args.get("img1_path", "")
    img2_path = request.args.get("img2_path", "")
    similarity = evaluate.getImagesScore(img1_path, img2_path)
    return '%f' % similarity

@app.route('/')
def hello_world():
    return "Invalid URL pattern entered. Kindly enter a valid URL."

if __name__ == '__main__':
    app.run()
