import os
import glob
import urllib.request
from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from google.cloud import storage
from fpdf import FPDF


storage_client = storage.Client.from_service_account_json('creds.json')
src_bucket = storage_client.get_bucket('txt-files-dump')
dest_bucket = storage_client.get_bucket('pdf-files-external')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the files part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                localfolder = app.config['UPLOAD_FOLDER']
                localfile = localfolder + filename
                blob = src_bucket.blob(filename)
                blob.upload_from_filename(localfile)		
        flash('File(s) successfully uploaded')
        tmp_files = glob.glob(app.config['UPLOAD_FOLDER'] + "*")
        for f in tmp_files:
            os.remove(f)
        return redirect('/')

@app.route('/task/convert')
def convert_pdf():
    # save FPDF() class into a
    # variable pdf
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    pdf.cell(200, 10, txt="Cloud Computing Demo", ln=1, align='C')

    files = src_bucket.list_blobs()
    fileList = [file.name for file in files if '.' in file.name]
    localfolder = app.config['DOWNLOAD_FOLDER']


    #convert from src_bucket and upload pdf to dest_bucket
    for item in fileList:
        blob = src_bucket.blob(item)
        fileName = blob.name.split('/')[-1]
        localfile = localfolder + fileName
        blob.download_to_filename(localfile)
        src_bucket.delete_blob(item)
        f = open(localfile, "r")
        for x in f:
            pdf.cell(200, 10, txt=x, ln=1, align='C')
        outputFile = localfolder + fileName.split('.')[0] + ".pdf"
        #write to pdf file
        pdf.output(outputFile)
        blob = dest_bucket.blob(fileName.split('.')[0] + ".pdf")
        blob.upload_from_filename(outputFile)

    #clean DOWNLOAD_FOLDER
    tmp_files = glob.glob(app.config['DOWNLOAD_FOLDER'] + "*")
    for f in tmp_files:
        os.remove(f)
    return render_template('upload.html')



if __name__ == "__main__":
    app.run()
