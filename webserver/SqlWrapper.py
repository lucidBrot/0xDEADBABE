import psycopg2

"""
nethz is limited to 32 characters
"""
def MakeOrGetUser (nethz):
        conn = psycopg2.connect("dbname=test user=postgres")
        cur = conn.cursor()     
        cur.execute("DO $$ BEGIN PERFORM MakeOrGetUser(%s); END; $$;", (nethz,))    
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
        cur.execute("DO $$ BEGIN PERFORM MakeOrGetLecture(%s::varchar(128)); END; $$;", (lecture_name,)) 
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
        cur.execute("DO $$ BEGIN PERFORM MakeOrGetExercise(%s::varchar(32), %s::varchar(128)); END; $$;", (nethz, lecture_name)) 
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
Initialize Database
"""
def InitializeDatabase (initSqlFile, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute(initSqlFile)       
        conn.commit()
        cur.close()
        conn.close()
