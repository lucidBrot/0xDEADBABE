#!/usr/bin/env python3
import os
from flask import Flask
from flask import request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import csv
import config # diverse configurable variables
import SqlWrapper # jasper's sql functions for communication with the DB without sqlAlchemy

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
DB = SQLAlchemy(FLASK_SERVER)
DEBUG_VERSION = "a"

def main():
    FLASK_SERVER.run('0.0.0.0', port=80)
    
# Server Routes: ---------------------------------------------------------

# Sample to receive GET request and argument /?name=asdf
@FLASK_SERVER.route('/', methods=["GET"])
def heloworld():
    name = request.args.get('name', default = 'Josi', type = str)
    return "Helo {}".format(name)

# Sample to receive post request
@FLASK_SERVER.route('/post', methods=["POST"])
def helopost():
    return "post response {}".format(str(request.form))

# Sample to route file that is called differently (but not for static)
# @FLASK_SERVER.route('/static/content')
# def sample_route():
#    return send_from_directory(STATIC_DIR, 'messages_typora.html')

# Sample to call Stored Procedures
# def callStoredProcedure():
#    data = DB.session.query(func.SCHEMA.FUNC_NAME()).all()

@FLASK_SERVER.route('/loadDebugCSV')
def loadDebugCSV():
    # parse CSV
    csvData = parseDebugCSV()
    # tell database about csv content
    problem = dbInitializeTeachingAssistants(csvData)
    # add version
    version = DEBUG_VERSION
    return "{}<br/><br/>csvData: {}\<br/><br/>Problem:{}".format(version, str(csvData), str(problem))

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
    # TODO: do for all data
    try:
        SqlWrapper.MakeAssistant(csvData[0][config.CSV_TA_NETHZ],
            DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        return ""
    except Exception as e: return str(e)


if __name__ == '__main__':
    main()
