from flask import Flask, request, send_file, url_for, after_this_request
import os
import pypandoc
import io
import sys

sys.stdout = sys.stderr

from src.generate import generate

base_directory = os.path.dirname(os.path.abspath(__file__))

# Set Pandoc binary location
home_directory = os.path.expanduser('~')
os.environ.setdefault('PYPANDOC_PANDOC',
                      os.path.join(home_directory, '.local', 'bin', 'pandoc'))

app = Flask(__name__)

available_settings = [
    'grammarTitle', 'grammarSubtitle', 'author', 'format', 'theme',
    'csvColumnWord', 'csvColumnLocal', 'csvColumnDefinition',
    'csvColumnPronunciation', 'csvColumnPartOfSpeech', 'layout'
]


@app.route('/', methods=['POST'])
def index():
    # Get all available string settings from posted object
    settings = {}
    for key in available_settings:
        settings[key] = request.form.get(key, None)

    try:
        # Loop through the files posted to the endpoint, reading all
        # files as strings.
        markdown_file_strings = []
        lexicon_file_string = None
        for filename, blob in request.files.items():
            if filename.endswith('.csv'):
                lexicon_file_string = str(blob.read(), 'utf-8')
            else:
                markdown_file_strings.append(str(blob.read(), 'utf-8'))

        filename = generate(markdown_file_strings, lexicon_file_string,
                            settings)

        print("In index function, returning file: " + filename)
        return filename
    except Exception as e:
        return 'ERROR' + str(type(e).__name__) + ': ' + str(e)


@app.route('/download')
def download():
    filename = request.args.get('filename')

    filepath = os.path.join(base_directory, 'temp', filename)
    print("Downloading filepath: " + filepath)

    if filename.endswith('.html'):
        mimetype = 'text/html; charset=utf-8'
        attachment_filename = 'Grammar.html'
    elif filename.endswith('.pdf'):
        mimetype = 'application/pdf'
        attachment_filename = 'Grammar.pdf'
    else:
        return 'File not found', 404

    # Read the file into a BytesIO object, allowing it to be deleted before the
    # request is fulfilled.
    with open(filepath, 'rb') as f:
        file_object = io.BytesIO(f.read())

    os.remove(filepath)

    return send_file(
        file_object,
        mimetype=mimetype,
        as_attachment=True,
        attachment_filename=attachment_filename)


def check_pandoc_on_startup():
    '''On startup, checks if pandoc is installed. If it is, continues to main
    application. Otherwise, pandoc will be installed.'''
    print('Looking for pandoc...')

    try:
        version = pypandoc.get_pandoc_version()
        print('Found version {0}'.format(version))

    except OSError:
        print('Not found! Downloading...')

        pypandoc.pandoc_download.download_pandoc()

        print('Download complete!')


if __name__ == '__main__':
    check_pandoc_on_startup()
    app.run(debug=True, host='0.0.0.0')
