from flask import (Blueprint, redirect, render_template, request, session, url_for, flash, jsonify)
from .io import write_metadata, save_like_data, save_tweet_data
import json 
import os 

## Initialize blueprint.
bp = Blueprint('experiment', __name__)
userid = '000'

@bp.route('/experiment')
def experiment():
    """Present jsPsych experiment to participant."""

    # Update participant metadata.
    session['experiment'] = True
    write_metadata(session, ['experiment'], 'a')

    # Present experiment.
    # return render_template('experiment.html', workerId=session['workerId'], assignmentId=session['assignmentId'], hitId=session['hitId'], code_success=session['code_success'], code_reject=session['code_reject'])
    return render_template('userid.html')

@bp.route('/userid', methods = ["GET", "POST"])
def userid():
    if request.method == "POST":
       session['id'] = request.form['id']
    return render_template('upload.html')
  
# downloads 'tweet.js' data
@bp.route('/success1', methods = ['POST'])   
def success1():   
    f = request.files['file'] 
    # If file name isn't "tweets.js", return to upload page & show error 
    # could change this to throwing error and passing to upload if incorrect 
    if (f.filename != "tweets.js"):
        flash("Make sure you're uploading tweets.js")
        # return redirect('upload.html')
        return render_template('upload.html')

    else:
        # Saves data to disk
        userid = session['id']
        session['tweets_uploaded'] = True 
        save_tweet_data(session, f, userid)

        ## Flag experiment as complete.
        session['complete'] = 'success'
        write_metadata(session, ['complete','code_success'], 'a')
        
        # sends to 'like.js' page
        return render_template("upload_like.html")
        # return render_template("acknowledgement.html", name = f.filename) 

@bp.route('/alert', methods=['GET'])
def alert():
    return render_template('alert.html')

@bp.route('/like', methods = ['GET', 'POST'])
def like():
    return render_template('upload_like.html')

@bp.route('/end', methods=['GET'])
def end():
    return render_template('end.html')

# like data 
@bp.route('/success', methods=['POST'])
def success():
    f = request.files['file'] 
    if (f.filename != "like.js"):
        flash("Make sure you're uploading like.js")
        return render_template('upload_like.html')
    else:
        # Saves data to disk
        userid = session['id']
        session['like_uploaded'] = True 
        save_like_data(session, f, userid)

        ## Flag experiment as complete.
        session['complete'] = 'success'
        write_metadata(session, ['complete','code_success'], 'a')
        
        # returns to finish page
        return render_template("end.html") 


@bp.route('/experiment', methods=['POST'])
def pass_message():
    """Write jsPsych message to metadata."""

    if request.is_json:

        ## Retrieve jsPsych data.
        msg = request.get_json()

        ## Update participant metadata.
        session['MESSAGE'] = msg
        write_metadata(session, ['MESSAGE'], 'a')

    ## DEV NOTE:
    ## This function returns the HTTP response status code: 200
    ## Code 200 signifies the POST request has succeeded.
    ## For a full list of status codes, see:
    ## https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    return ('', 200)

