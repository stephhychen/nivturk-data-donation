from flask import (Blueprint, redirect, render_template, request, session, url_for, flash, jsonify)
from .io import save_like_data, save_tweet_data
import json 
import os 

# Initialize blueprint.
bp = Blueprint('experiment', __name__)

# Routes to participant ID request 
@bp.route('/experiment')
def experiment():

    # Update participant metadata.
    session['experiment'] = True
    # write_metadata(session, ['experiment'], 'a')

    # Direct participant to participant ID entry
    return render_template('userid.html')

@bp.route('/userid', methods = ["GET", "POST"])
def userid():
    # Stores participant ID in Flask session, directs to upload page
    if request.method == "POST":
       session['id'] = request.form['id']
    return render_template('upload_tweets.html')
  
# Downloads 'tweets.js' data
@bp.route('/success1', methods = ['POST'])   
def success1():   
    f = request.files['file'] 
    # Checks file name is "tweets.js"
    if (f.filename != "tweets.js"):
        flash("Make sure you're uploading tweets.js")
        # return redirect('upload_tweets.html')
        return render_template('upload_tweets.html')

    else:
        # Saves data to disk
        save_tweet_data(session, f, session['id'])

        ## Flag experiment as complete.
        session['complete'] = 'success'
        # write_metadata(session, ['complete','code_success'], 'a')
        
        # Redirects to uploading 'like.js'
        return render_template("upload_like.html")

# Downloads 'like.js' data  
@bp.route('/success', methods=['POST'])
def success():
    f = request.files['file'] 
    # Checks that upload is 'like.js' 
    if (f.filename != "like.js"):
        flash("Make sure you're uploading like.js")
        return render_template('upload_like.html')
    else:
        # Saves data to disk
        session['like_uploaded'] = True 
        save_like_data(session, f, session['id'])

        # Flag experiment as complete.
        session['complete'] = 'success'
        # write_metadata(session, ['complete','code_success'], 'a')
        
        # Returns  to finish page
        return render_template("end.html") 

