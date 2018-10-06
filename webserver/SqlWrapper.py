import psycopg2

"""
nethz is limited to 32 characters
"""
def MakeOrGetUser (nethz, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT MakeOrGetUser(%s);", (nethz,))    
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
        cur.execute("SELECT MakeOrGetLecture(%s::varchar(128));", (lecture_name,)) 
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
        cur.execute("SELECT MakeOrGetExercise(%s::varchar(32), %s::varchar(128));", (nethz, lecture_name)) 
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
Gets all active lectures as list of tuples
(Lecture_ID, Lecture_Name)[]
"""
def GetActiveLectures (dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("SELECT GetActiveLectures();") 
        lectures = cur.fetchmany()
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
        cur.execute("SELECT GetActiveExercises();") 
        exercises = cur.fetchmany()
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
        cur.execute("SELECT GetExercise(%s, %s);", (lecture_id, assistant_id)) 
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
        cur.execute("SELECT GetLectureExercises(%s);", (lecture_id,)) 
        exercises = cur.fetchmany()
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
        cur.execute("SELECT GetExerciseRatings(%s);", (exercise_id,)) 
        ratings = cur.fetchmany()
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
