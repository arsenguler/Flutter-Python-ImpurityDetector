from flask import Flask, jsonify, request
import werkzeug
from func import *

app = Flask(__name__)


@app.route("/")
def showHomePage():
    json_file = {}
    json_file['query'] = 'hello_world'
    return jsonify(json_file)


@app.route('/upload', methods=["POST"])
def upload():
    if request.method == "POST":
        imagefile = request.files['image']
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        imagefile.save("./uploadedimages/" + filename)
        data = request.form
        result = calculateVis(filename, data['liquid'])
        print(data['liquid'], "\n", filename)
        print(result)
        return jsonify({
            "message": result
        })


if __name__ == "__main__":
    app.run(debug=True, port=4000)
