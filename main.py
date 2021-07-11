from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
from subprocess import Popen, PIPE
app = Flask(__name__)

# APP_ROOT= os.path.dirname(os.path.abspath(__file__))
# target = os.path.join(APP_ROOT,'static/')
# app.config["DEBUG"] = True

# picFolder = os.path.join('static','User-Image')
# app.config["UPLOAD_FOLDER"] = picFolder

# pic1 = os.path.join(app.config['UPLOAD_FOLDER'],'HERO.jpg')

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# st=""
    
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/services')
def services():
    return render_template("services.html")

@app.route('/videocaption')
def videocaption():
    os.chdir("/home/godz/Downloads/HackMountains/CapTor/camera")
    p = Popen(['streamlit', 'run', 'feed.py'], stdin=PIPE, bufsize=0)
    return render_template("loader_2nd.html")

@app.route('/languagequery')
def languagequery():
    os.chdir("/home/godz/Downloads/HackMountains/CapTor/search")
    p = Popen(['streamlit', 'run', 'search.py'], stdin=PIPE, bufsize=0)
    return render_template("loader_2nd.html")

@app.route('/depthestmation')
def depthestmation():
    os.chdir("/home/godz/Downloads/HackMountains/DepthEst")
    p = Popen(['python3', 'DepthEstimation.py'], stdin=PIPE, bufsize=0)
    return render_template("loader.html")    

@app.route('/linecrossing')
def linecrossing():
    os.chdir("/home/godz/Downloads/HackMountains/Obj_Detect")
    p = Popen(['python3', 'obj_detec_line_crossing.py'], stdin=PIPE, bufsize=0)
    return render_template("loader_2nd.html")

# @app.route('/upload',methods=["GET","POST"])
# def upload():
#     if request.method == "POST":
#         file=request.files['uploadBills']
#         #file.save(secure_filename(file.filename))
#         #file.save(os.path.join("static/pics", file.filename))
#         #some custom file name that you want
#         if file and allowed_file(file.filename):
#             st=allowed_file(file.filename)
#             file.filename="abc."+st
#             file.save("static/content/"+file.filename)
#             time.sleep(3)  
#     return render_template("upload.html")   


# def allowed_file(filename):
#     return filename.rsplit('.', 1)[1].lower() 

if __name__ == "__main__":
    app.run()

