#!/usr/bin/env python3
import os
from flask import Flask
from flask import request, send_from_directory, url_for
import csv
import config # diverse configurable variables
import SqlWrapper # jasper's sql functions for communication with the DB without sqlAlchemy
from io import StringIO
from flask import render_template
from flask import session, redirect
import random
import sys
import json
import login

# set up server directory for web
STATIC_DIR = 'static'
STATIC_DIR_WITH_SLASH = "/{}".format(STATIC_DIR)
# set up global server variable and global database variable, based on environment variables
FLASK_SERVER = Flask(__name__, static_url_path=STATIC_DIR_WITH_SLASH, static_folder=STATIC_DIR)
DB_URL = os.environ.get("RUNTIME_POSTGRES_DB_SERVER")
DB_PORT = os.environ.get("RUNTIME_POSTGRES_DB_PORT")
DB_NAME = os.environ.get("RUNTIME_POSTGRES_DB_NAME")
DB_USER = os.environ.get("RUNTIME_POSTGRES_DB_USER")
DB_PW = os.environ.get("RUNTIME_POSTGRES_DB_PW")
FLASK_SERVER.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PW, DB_URL, DB_PORT, DB_NAME)
FLASK_SERVER.config['PEOPLE_API_URL'] = os.environ.get("RUNTIME_SERVIS_PEOPLE_API_SERVER")
FLASK_SERVER.config['PEOPLE_API_PORT'] = os.environ.get("RUNTIME_SERVIS_PEOPLE_API_PORT")
FLASK_SERVER.config['PEOPLE_API_KEY'] = os.environ.get("RUNTIME_SERVIS_PEOPLE_API_KEY")
DEBUG_VERSION = "ababc"

def main():
    initDatabase()
    fillDatabase()
    FLASK_SERVER.config["SECRET_KEY"] = config.SECRET
    FLASK_SERVER.run('0.0.0.0', port=80)

def initDatabase():
# read whole initialization file into one string
    with open(config.SQL_INITIALIZATION_FILE, 'r') as content_file:
        sqlFile = content_file.read()
    try:
        SqlWrapper.InitializeDatabase(sqlFile,
                DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        print("Successfully initialzed")
    except Exception as e:
        print( "Init of DB Failed!<br/><br/>{}".format(str(e)))
        print("Line: {}".format(sys.exc_info()[-1].tb_lineno))

# Require Login: ---------------------------------------------------------

@FLASK_SERVER.before_request
def check_valid_login():
    """
    Checks if a given user is logged in. A user is logged in if a value for 'user' is set in the cookie
    of the user. The cookie is signed with the private key of the app to prevent modification
    of the values in the cookie (Flask does that).
    This happens before the request is handled. If the endpoint requested has the
    decorator login_required and thus the attribute needs_login
    the user will be redirected to the root page.
    """
    login_valid = session.get("nethz_cookie")  # or whatever you use to check valid login

    if (request.endpoint and getattr(FLASK_SERVER.view_functions[request.endpoint],
                                     'needs_login', False)
        and not login_valid):
        return redirect("/static/userLogin.html", code=303)


def login_required(func):
    """
    This decorator marks the route to be used for logged in users only. The user must be logged in to use this route. If
    the user is not logged in he will be redirected to the login page.
    """
    func.needs_login = True
    return func

# Server Routes: ---------------------------------------------------------

# Sample to receive GET request and argument /?name=asdf
@FLASK_SERVER.route('/', methods=["GET"])
def heloworld():
    #name = request.args.get('name', default = 'Josi', type = str)
    #return "{} Helo {}<br/>{}".format(DEBUG_VERSION, name, DB_USER)
    return redirect("/static/userLogin.html")

# Sample to receive post request
@FLASK_SERVER.route('/post', methods=["POST"])
def helopost():
    return "post response {}".format(str(request.form))

# Sample to route file that is called differently (but not for static)
# @FLASK_SERVER.route('/static/content')
# def sample_route():
#    return send_from_directory(STATIC_DIR, 'messages_typora.html')

"""
only debug
"""
@FLASK_SERVER.route('/loadDebugCSV')
def loadDebugCSV():
    out=""
    # read whole initialization file into one string
    out+=initDatabase()
    # parse CSV
    csvData = parseDebugCSV()
    # tell database about csv content
    out += dbInitializeTeachingAssistants(csvData)
    # add version
    version = DEBUG_VERSION
    return "{}<br/><br/>csvData: {}\<br/><br/>Out:{}".format(version, str(csvData), str(out))

"""
Allow client to send the database a CSV file
nethz: their login name
file: the csv file containing config.CSV_... content
"""
@login_required
@FLASK_SERVER.route('/setCSV', methods=["POST"])
def setCSV():
    data = request.files['file'].read()
    f = StringIO(data.decode())
    reader = csv.reader(f, delimiter=',')
    csvdata = [line for line in reader]
    keys = csvdata[0]
    values = csvdata[1:]
    csvdict = [{k: v for k, v in zip(keys, value)} for value in values]
    usr = request.form.get('nethz') # the user who sent the request
    debug_log = dbInitializeTeachingAssistants(csvdict)
#    return "user: {0}\n{1}\n\n{2}".format(str(usr), str(csvdict), debug_log)
    return redirect("/courses.html", code=302)

"""
Tell database to create user if doesn't exist
nethz: which user logged in
"""
@FLASK_SERVER.route('/userLogin', methods=["POST"])
def userLogin():
    nethz = request.form.get('nethz')
    password = request.form.get('password')
    # verify authentication
    loginOkay = login.login(nethz, password)
    if not loginOkay:
        return redirect("/static/userLogin.html")
    retStr = "{} logged in... Tellling DB...<br/>".format(nethz)
    try:
        SqlWrapper.MakeOrGetUser(nethz, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        session["nethz_cookie"] = nethz
        retStr += "done.<br/>"
    except Exception as e:
        retStr += "failed: {} <br/>".format(str(e))
#    return retStr
    return redirect("/courses.html", code=302)

@login_required
@FLASK_SERVER.route('/submitRatings', methods=["POST"])
def submitRatings():
    ratingsDictListJSON = request.form.get('ratings')
    # ratingsDictJSON contains keys and values as a dictionary. And that repeated, in a list.
    ratingsDictList = json.loads(ratingsDictListJSON)
    ratingsList = list(map(lambda dictionary: (dictionary['exercise_id'],
                                          dictionary['rating_title'],
                                          dictionary['rating_value']), ratingsDictList))
    FLASK_SERVER.logger.warning("ratings list: "+str(ratingsList))
    #
    user_nethz = session["nethz_cookie"]
    retStr = "Got ratings: {}".format(str(ratingsList))
    try:
        user_id = SqlWrapper.MakeOrGetUser(user_nethz, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        FLASK_SERVER.logger.warning("USER ID: " + str(user_id))
        SqlWrapper.AddExerciseRatingsFromTitles(ratingsList, user_id, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        retStr+="<br/>...done."
    except Exception as e:
        retStr += "<br/>...failed: {} <br/>".format(str(e))
    return retStr

@login_required
@FLASK_SERVER.route('/submitComment', methods=["POST"])
def submitComment():
    msg = request.form.get('message')
    nethz_name = session["nethz_cookie"]
    msg_title = request.form.get('message_title')
    ex_ID = request.form.get('exercise_id')
    try:
        user_id = SqlWrapper.MakeOrGetUser (nethz_name, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        SqlWrapper.AddComment(ex_ID, user_id, msg_title, msg, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    except Exception as e:
        return "Exception: {}".format(str(e))
    return "success."

# Dynamic Templates: ------------------------------------------------------

@login_required
@FLASK_SERVER.route('/courses.html')
def courses_template():
    try:
        lectures = SqlWrapper.GetActiveLectures(DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    except Exception as e:
        return "Internal Server Error. Request failed :( Please try again.<br/>{}".format(str(e))

    return render_template('courses.html', courses=lectures)

@login_required
@FLASK_SERVER.route('/main_profile.html', methods=["GET"])
def main_profile_template():
    TA_id = request.args.get('TA_id', default=0, type = int)
    course_id = request.args.get('course_id', default=0, type=int)
    # get Facts from database
    try:
        (ex_ID, assi_ID, assi_nethz, lec_id, lec_name) = SqlWrapper.GetExercise(course_id, TA_id, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT) or (None, None, None, None, None)
        ratings = SqlWrapper.GetExerciseRatings(ex_ID, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        attributes = []
        for rating in ratings:
            (_, title, value) = rating
            percentage = config.RATING_SCALE_FACTOR*value
            attributes.append({"title" : title, "percentage" : percentage})

        nethz = session["nethz_cookie"]
        usr_id = SqlWrapper.MakeOrGetUser(nethz, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)

        # load comments from database
        commentsList = SqlWrapper.GetExerciseComments(ex_ID, usr_id, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        comments=[]
        for comment in commentsList:
            like_count_c = -1 #JASPER
            (_, user_id, author_nethz, creation_date, like_count_c, user_liked, title_c, text_c) = comment
            comments.append({
                "title": title_c, "text": text_c, "like_count":like_count_c, "user_liked":user_liked, "author":author_nethz
                })
        return render_template('main_profile.html',TA_name=assi_nethz, lecture=lec_name, attributes=attributes,
            comments=comments, exercise_id=ex_ID, nethzName=session["nethz_cookie"], TA_id=TA_id, course_id=course_id)
    except Exception as e:
        return "Exception! {}".format(str(e))

# exactly same thing again, but without comments
@login_required
@FLASK_SERVER.route('/main_profile_edit.html', methods=["GET"])
def main_profile_edit_template():
    TA_id = request.args.get('TA_id', default=0, type = int)
    course_id = request.args.get('course_id', default=0, type=int)
    # get Facts from database
    try:
        (ex_ID, assi_ID, assi_nethz, lec_id, lec_name) = SqlWrapper.GetExercise(course_id, TA_id, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT) or (None, None, None, None, None)
        ratings = SqlWrapper.GetExerciseRatings(ex_ID, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        attributes = []
        for rating in ratings:
            (_, title, value) = rating
            percentage = config.RATING_SCALE_FACTOR*value
            attributes.append({"title" : title, "percentage" : percentage})
        comments = []
        return render_template('main_profile_edit.html',TA_name=assi_nethz, lecture=lec_name, attributes=attributes, comments=comments, exercise_id=ex_ID, nethzName=session["nethz_cookie"], TA_id=TA_id, course_id=course_id)
    except Exception as e:
        return "Exception! {}".format(str(e))


@login_required
@FLASK_SERVER.route('/course.html', methods=["GET"])
def course():
    course_ID = request.args.get('course_id', default = '0', type = int)
#    TA = {"name": "Christian Hanspeter von-Günther Knieling", "id":"1243", "nethz":"lmao"}
#    (ex_ID, assi_id, assi_nethz, lec_id, lec_name)[]
    resultlist = SqlWrapper.GetLectureExercises(course_ID, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    # list of TA dicts: id, nethz
    TAlist = [{'id': TA_id, 'nethz': ta_nethz} for _, TA_id, ta_nethz, __, name, in resultlist]

    # Setting the lecture name. If resultlist is empty for some reason, this is the default we use for now
    lec_name = "Empty lecture"
    if len(resultlist) != 0:
        (_, _, _, _, lec_name) = resultlist[0]
    return render_template('course.html',course_id = course_ID, TA_data=TAlist, course_name=lec_name)

@login_required
@FLASK_SERVER.route('/adminPage')
def adminPage():
    return render_template('adminPage.html')


# CSV Logic: --------------------------------------------------------------

def fillDatabase():
    # Reusing the functions from Eric
    # Filling the database with exercises also adds the TAs and lectures
    data = parseDebugCSV()
    log = dbInitializeTeachingAssistants(data)
    print(log)

    # Extract key and value from the dict from parseDebugCSV() and get the resp. exercise ID

    exercise_ids = [SqlWrapper.MakeOrGetExercise(line['ta_nethz'], line['lecture_name'], DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
                        for line in data]
    fake_reviewers_nethz = ["alibaba", "unclebens", "suntzu"]
    fake_reviewers_ids = []
    rating_titles = ["Speech Clarity", "Quality of Exercises", "Quality of Theory"]
    rating_title_ids = []

    for nethz in fake_reviewers_nethz:
        reviewer_id = SqlWrapper.MakeOrGetUser(nethz, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        fake_reviewers_ids.append(reviewer_id)
    for title in rating_titles:
        title_id = SqlWrapper.MakeOrGetRatingField(title, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        rating_title_ids.append(title_id)

    ratings = []
    for ex_ID in exercise_ids:
        for title_id in rating_title_ids:
            value = random.randint(1,5)
            ratings.append((ex_ID, title_id, value))
    try:
        for reviewer_id in fake_reviewers_ids:
            SqlWrapper.AddExerciseRatings(ratings, reviewer_id, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    except Exception as e:
        print("Exception! {}".format(str(e)))
        print("Line: {}".format(sys.exc_info()[-1].tb_lineno))



"""
return: a list of OrderedDictionaries with the keys config.CSV_TA_NETHZ and CSV_TA_NETHZ
"""
def parseCSV(csvFile):
    with open(csvFile, 'r') as f:
        reader = csv.DictReader(f)
        mylist = [line for line in reader]
        print(mylist)
        # use config.CSV_TA_NETHZ and config.CSV_LECTURE_NAME
    return mylist

def parseDebugCSV():
    return parseCSV('./debug_inputs/inputs.csv')

def dbInitializeTeachingAssistants(csvData):
    returnString = ""
    # Clear Exercises
    try:
        SqlWrapper.ClearExercises(DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    except Exception as e:
        returnString+="Clearing Exercises:<br/>{}<br/><br/>".format(str(e))
    # For data row, add to database if needed
    for i in range(len(csvData)):
        try:
            returnString += "<br/>Adding ({0},{1})".format(csvData[i][config.CSV_TA_NETHZ], csvData[i][config.CSV_LECTURE_NAME])
            SqlWrapper.MakeOrGetExercise(
                    csvData[i][config.CSV_TA_NETHZ], csvData[i][config.CSV_LECTURE_NAME],
                    DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        except Exception as e:
            returnString+=" failed with exception {}<br/>".format(str(e))

    return returnString


if __name__ == '__main__':
    main()
