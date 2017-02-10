from flask import Flask, request
import json

from src.generate import generate

app = Flask(__name__)

available_settings = ['grammarTitle', 'grammarSubtitle', 'author', 'format',
                      'theme']

@app.route('/', methods=['POST'])
def index():

    # Get all available string settings from posted object
    settings = {}
    for key in available_settings:
        settings[key] = request.form.get(key, None)

    # Loop through the files posted to the endpoint, reading all
    # files as strings.
    markdown_file_strings = []
    lexicon_file_string = None
    for filename, blob in request.files.items():
        if filename.endswith('.csv'):
            lexicon_file_string = str(blob.read(), 'utf-8')
        else:
            markdown_file_strings.append(str(blob.read(), 'utf-8'))

    generate(markdown_file_strings, lexicon_file_string, settings)

    return json.dumps({'success': True}), 200, {'ContentType':
                                                'application/json'}


if __name__ == '__main__':
    app.run(debug=True)
