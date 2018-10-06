import psycopg2

"""
nethz is limited to 32 characters
"""
def MakeOrGetUser (nethz, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM MakeOrGetUser(%s);", (nethz,))    
        id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return id
        
"""
lecture_name is limited to 128 characters
"""
def MakeOrGetLecture (lecture_name, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM MakeOrGetLecture(%s::varchar(128));", (lecture_name,)) 
        id = cur.fetchone()[0]        
        conn.commit()
        cur.close()
        conn.close()
        return id
       
"""
nethz is limited to 32 characters
lecture_name is limited to 128 characters
"""       
def MakeOrGetExercise (nethz, lecture_name, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM MakeOrGetExercise(%s::varchar(32), %s::varchar(128));", (nethz, lecture_name)) 
        id = cur.fetchone()[0]        
        conn.commit()
        cur.close()
        conn.close()
        return id
        
"""
title is limited to 128 characters
"""       
def MakeOrGetRatingField (title, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM MakeOrGetRatingField(%s::varchar(128));", (title, )) 
        id = cur.fetchone()[0]        
        conn.commit()
        cur.close()
        conn.close()
        return id        
        
def ClearExercises (dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("DO $$ BEGIN PERFORM ClearExercises(); END; $$;") 
        conn.commit()
        cur.close()
        conn.close()

"""
Takes a list of triples (exercise_id, rating_title, rating_value)
"""
def AddExerciseRatings (ratings_list, user_nethz, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()
        # ratings_list is a list of several (Exercise_ID, Rating_Title, Rating_Value)
        for (exercise_id, rating_title, rating_value) in ratings_list:
            cur.execute("DO $$ BEGIN PERFORM AddExerciseRatings(%s, %s, %s, %s); END; $$;",(exercise_id, rating_title, user_nethz, rating_value))
        conn.commit()
        cur.close()
        conn.close()

"""
Adds a new comment from the given user to the given exercise with title and text.
"""
def AddComment (exercise_id, user_id, title, text, user_nethz, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()
        cur.execute("SELECT * FROM AddComment(%s::int, %s::int, %s::varchar(64), %s::varchar(1024));", (exec_id, usr_id, title, text))
        id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return id        

"""
Gets all active lectures as list of tuples
(Lecture_ID: int, Lecture_Name: varchar(128))[]
"""
def GetActiveLectures (dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM GetActiveLectures();") 
        lectures = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return lectures
      
"""
Gets all active exercises as list of tuples
(Exercise_ID, Assistant_ID, Assistant_Nethz, Lecture_ID, Lecture_Name)[]
"""      
def GetActiveExercises (dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM GetActiveExercises();") 
        exercises = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return exercises
        
"""
Gets a specific exercise
(Exercise_ID, Assistant_ID, Assistant_Nethz, Lecture_ID, Lecture_Name)
"""              
def GetExercise (lecture_id, assistant_id, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM GetExercise(%s, %s);", (lecture_id, assistant_id)) 
        exercise = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return exercise
        
"""
Gets all active exercises as list of tuples
(Exercise_ID, Assistant_ID, Assistant_Nethz, Lecture_ID, Lecture_Name)[]
"""      
def GetLectureExercises (lecture_id, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM GetLectureExercises(%s);", (lecture_id,)) 
        exercises = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return exercises
                
"""
Gets the ratings for a specific exercise
(Exercise_ID, Rating_Title, Rating_Value)
"""              
def GetExerciseRatings (exercise_id, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM GetExerciseRatings(%s);", (exercise_id,)) 
        ratings = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return ratings
        
"""
Gets the comments for a specific exercise
(Exercise_ID, User_ID, User_Nethz, Creation_Date, Title, Text)
"""              
def GetExerciseComments (exercise_id, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT * FROM GetExerciseComments(%s);", (exercise_id,)) 
        ratings = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return ratings

"""
Initialize Database
"""
def InitializeDatabase (initSqlFile, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute(initSqlFile)       
        conn.commit()
        cur.close()
        conn.close()
