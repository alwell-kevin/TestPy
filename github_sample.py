from flask import Flask, request, render_template, make_response
from lxml import etree

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/', methods=['POST'])
def parse_xml():
  parsed_xml = None
  xml = request.form['xml']
  parser = etree.XMLParser()
  try:
    doc = etree.fromstring(xml, parser)
    parsed_xml = etree.tostring(doc)
    return render_template('parsed.html', parsed=parsed_xml.decode())
  except Exception as e:
    print(e)
    pass
  return render_template('index.html', error="Please enter valid XML content")

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
