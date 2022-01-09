import requests
from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import os
import json

UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__, static_url_path='/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
my_secret = os.environ['apikey']

def demo_cal(num):
    if int(num)==1:
        data_load = "testdata2burger.json"
    else:
        data_load= "testdata.json"
    with open(data_load, "r") as f:
        data = json.load(f)
    return data

def get_cal(fname):
    try:
        img = f"static/uploads/{fname}"
        api_user_token = my_secret
        headers = {'Authorization': 'Bearer ' + api_user_token}

        # Single/Several Dishes Detection
        url = 'https://api.logmeal.es/v2/recognition/complete'
        resp = requests.post(url,files={'image': open(img, 'rb')},headers=headers)
        print(resp.json())
        #print("response21:\n")
        # Nutritional information
        url = 'https://api.logmeal.es/v2/recipe/nutritionalInfo'
        resp = requests.post(url,json={'imageId': resp.json()['imageId']}, headers=headers)
        print(resp.json()) # display nutritional info
        return resp.json() 
    except:
        return "Error"

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/api")
def testdata():
    data = demo_cal(1)
    return data

@app.route("/demo/<num>")
def demo(num):
    data = demo_cal(num)
    fname = "damplefood.jpg"
    if int(num)==1:
        fname = "istockphoto-1125149183-612x612.jpg"
    else:
        fname = "depositphotos_50523105-stock-photo-pizza-with-tomatoes.jpg"
    #print(num)
    return render_template("demo.html",fname=fname, data=data)

@app.route('/result', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      fname = secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
      data = get_cal(fname)
      if data=="Error":
          return "Service has been exhausted please try after 24hrs!"
      an_object = data["foodName"]
      check_list = isinstance(an_object, list)
      if check_list==True:
          data["foodName"] = data["foodName"][0]
      return render_template("result.html",fname=fname, data=data)
      #return redirect(url_for('static', filename='uploads/' + fname), code=301)

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
