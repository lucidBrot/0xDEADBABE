#!/usr/bin/env python3
import os
from flask import Flask
from flask import request, send_from_directory, url_for
import csv
import config # diverse configurable variables
import SqlWrapper # jasper's sql functions for communication with the DB without sqlAlchemy
from io import StringIO
from flask import render_template

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
DEBUG_VERSION = "abab"

def main():
    initDatabase()
    FLASK_SERVER.run('0.0.0.0', port=80)

def initDatabase():
# read whole initialization file into one string
    with open(config.SQL_INITIALIZATION_FILE, 'r') as content_file:
        sqlFile = content_file.read()
    try:
        SqlWrapper.InitializeDatabase(sqlFile, 
                DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        return ""
    except Exception as e:
        return "Init of DB Failed!<br/><br/>{}".format(str(e))

    
# Server Routes: ---------------------------------------------------------

# Sample to receive GET request and argument /?name=asdf
@FLASK_SERVER.route('/', methods=["GET"])
def heloworld():
    name = request.args.get('name', default = 'Josi', type = str)
    return "{} Helo {}<br/>{}".format(DEBUG_VERSION, name, DB_USER)

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
    return "user: {0}\n{1}\n\n{2}".format(str(usr), str(csvdict), debug_log)

"""
Tell database to create user if doesn't exist
nethz: which user logged in
"""
@FLASK_SERVER.route('/userLogin', methods=["POST"])
def userLogin():
    nethz = request.form.get('nethz')
    retStr = "{} logged in. Tellling DB...<br/>".format(nethz)
    try:
        SqlWrapper.MakeOrGetUser(nethz, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        retStr += "done.<br/>"
    except Exception as e:
        retStr += "failed: {} <br/>".format(str(e))
    return retStr

# Dynamic Templates: ------------------------------------------------------

@FLASK_SERVER.route('/courses.html')
def courses_template():
    try:
        lectures = SqlWrapper.GetActiveLectures(DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    except Exception as e:
        return "Internal Server Error. Request failed :( Please try again.<br/>{}".format(str(e))

    return render_template('courses.html', courses=lectures)

# TA_id, course_id
@FLASK_SERVER.route('/main_profile.html', methods=["GET"])
def main_profile_template():
    TA_id = request.args.get('TA_id', default=0, type = int)
    course_id = request.args.get('course_id', default=0, type=int)
    # get Facts from database
    try:
        (ex_ID, assi_ID, assi_nethz, lec_id, lec_name) = SqlWrapper.GetExercise(course_id, TA_id, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        # TODO: load attributes from database!
        ratings = SqlWrapper.GetExerciseRatings(ex_ID, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        attributes = []
        for rating in ratings:
            (ex_id, title, value) = rating
            # percentage = 10*points
            percentage = 10*value
            attributes.append({"title" : title, "percentage" : percentage})
        comments = []
        return render_template('main_profile.html',TA_name=assi_nethz, lecture=lecture_name, attributes=attributes, comments=comments)
    except Exception as e:
        return "Exception! {}".format(str(e))

@FLASK_SERVER.route('/course.html', methods=["GET"])
def course():
    course_ID = request.args.get('course_id', default = '0', type = int)
#    TA = {"name": "Christian Hanspeter von-Günther Knieling", "id":"1243", "nethz":"lmao"}
#    (ex_id, assi_id, assi_nethz, lec_id, lec_name)[]
    resultlist = SqlWrapper.GetLectureExercises(course_ID, DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    # list of TA dicts: name, id, nethz
    TAlist = [{name, ta_id, ta_nethz} for _, ta_id, ta_nethz, __, name in resultlist]
    (_, _, _, _, lec_name) = resultlist[0]
    return render_template('course.html',course_id = course_ID, TA_data=TAlist, course_name=lec_name)


# CSV Logic: --------------------------------------------------------------

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
