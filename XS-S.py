from os.path import join
from flask import Flask, request, redirect, url_for, send_file, render_template

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/data/images'

def allowed_file(filename):
  return '.' in filename or filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    upload = request.files.get('file', '')
    if upload.filename == '':
      flash('No file selected')
      return redirect(request.url)
    elif upload and allowed_file(upload.filename):
      filename = upload.filename
      upload.save(join(UPLOAD_FOLDER, filename))
      return redirect(url_for('view_file', filename=filename))
  return render_template('index.html')

@app.route('/view/<filename>')
def view_file(filename):
  return render_template('view.html', filename=filename)

@app.route('/uploads')
def deliver_file():
  filename = request.args.get('filename')
  return send_file(join(UPLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
