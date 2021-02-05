from flask import Flask, render_template, request
import embed

app = Flask(__name__)

@app.route('/getNeighbours')
def vectorize():
    word = request.args.get("word", "")
    k = request.args.get("k", "")
    return '%s' % embed.getNearestNeighbours(word, int(k))

if __name__ == '__main__':
    embed.init()
    app.run(host='0.0.0.0')