from flask import Flask
import os

UPLOAD_FOLDER = '/tmp/upload/'
DOWNLOAD_FOLDER = '/tmp/download/'

if not os.path.exists('/tmp/upload'):
    os.makedirs('/tmp/upload')

if not os.path.exists('/tmp/download'):
    os.makedirs('/tmp/download')

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

