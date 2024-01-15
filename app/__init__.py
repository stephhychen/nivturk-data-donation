import os, sys, re, configparser, warnings
from flask import (Flask, redirect, render_template, request, session, url_for)
from app import alert, experiment, complete, error
from .io import write_metadata
from .utils import gen_code
__version__ = '1.2.6'

## Define root directory.
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

## Load and parse configuration file.
cfg = configparser.ConfigParser()
cfg.read(os.path.join(ROOT_DIR, 'app.ini'))

## Ensure output directories exist.
data_dir = os.path.join(ROOT_DIR, cfg['IO']['DATA'])
if not os.path.isdir(data_dir): os.makedirs(data_dir)
# /like and /tweets subdirectories 
data_like_dir = os.path.join(data_dir, 'like')
if not os.path.isdir(data_like_dir): os.makedirs(data_like_dir)
data_tweets_dir = os.path.join(data_dir, 'tweets')
if not os.path.isdir(data_tweets_dir): os.makedirs(data_tweets_dir)

meta_dir = os.path.join(ROOT_DIR, cfg['IO']['METADATA'])
if not os.path.isdir(meta_dir): os.makedirs(meta_dir)
incomplete_dir = os.path.join(ROOT_DIR, cfg['IO']['INCOMPLETE'])
if not os.path.isdir(incomplete_dir): os.makedirs(incomplete_dir)
reject_dir = os.path.join(ROOT_DIR, cfg['IO']['REJECT'])
if not os.path.isdir(reject_dir): os.makedirs(reject_dir)

## Check Flask mode; if debug mode, clear session variable.
debug = cfg['FLASK'].getboolean('DEBUG')
if debug:
    warnings.warn("WARNING: Flask currently in debug mode. This should be changed prior to production.")

## Check Flask password.
secret_key = cfg['FLASK']['SECRET_KEY']
if secret_key == "PLEASE_CHANGE_THIS":
    warnings.warn("WARNING: Flask password is currently default. This should be changed prior to production.")

## Check restart mode; if true, participants can restart experiment.
allow_restart = cfg['FLASK'].getboolean('ALLOW_RESTART')

## Initialize Flask application.
app = Flask(__name__)
app.secret_key = secret_key

## Apply blueprints to the application.
# app.register_blueprint(consent.bp)
app.register_blueprint(alert.bp)
app.register_blueprint(experiment.bp)
app.register_blueprint(complete.bp)
app.register_blueprint(error.bp)

## Define root node.
@app.route('/')
def index():

    ## Debug mode: clear session.
    if debug:
        session.clear()

    ## Store directories in session object.
    session['data'] = data_dir
    session['data_tweets'] = data_tweets_dir
    session['data_like'] = data_like_dir
    session['metadata'] = meta_dir
    session['incomplete'] = incomplete_dir
    session['reject'] = reject_dir
    session['allow_restart'] = allow_restart

    ## Record incoming metadata.
    info = dict(
        workerId     = '000',                               # Placeholder ID
        assignmentId = request.args.get('SESSION_ID'),      # Prolific metadata
        hitId        = request.args.get('STUDY_ID'),        # Prolific metadata
        subId        = gen_code(24),                        # NivTurk metadata
        address      = request.remote_addr,                 # NivTurk metadata
        user_agent   = request.user_agent.string,           # User metadata
        code_success = cfg['PROLIFIC'].get('CODE_SUCCESS', gen_code(8).upper()),
        code_reject  = cfg['PROLIFIC'].get('CODE_REJECT', gen_code(8).upper()),
    )

    # ## Case 1: workerId absent form URL.
    # if info['workerId'] is None:

    #     ## Redirect participant to error (missing workerId).
    #     return redirect(url_for('error.error', errornum=1000))

    ## Case 2: mobile / tablet / game console user.
    if any([device in info['user_agent'].lower() for device in ['mobile','android','iphone','ipad','kindle','nintendo','playstation','xbox']]):

        ## Redirect participant to error (platform error).
        return redirect(url_for('error.error', errornum=1001))

    ## Case 7: first visit, workerId present.
    else:

        ## Update metadata.
        for k, v in info.items(): session[k] = v
        write_metadata(session, ['workerId','hitId','assignmentId','subId','address','user_agent'], 'w')

        ## Redirect participant to landing page
        return redirect(url_for('alert.alert'))
