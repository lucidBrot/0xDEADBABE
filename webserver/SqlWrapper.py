import psycopg2

def NotifyUserLogin (username):
        conn = psycopg2.connect("dbname=test user=postgres")
        cur = conn.cursor()     
        cur.execute("DO $$ BEGIN PERFORM NotifyUserLogin(%s); END; $$;", (username))    
        conn.commit()
        cur.close()
        conn.close()
        
"""
assistant_nethz is limited to 32 characters
"""
def MakeAssistant (assistant_nethz, dbname, user, password, host, port):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()     
        cur.execute("DO $$ BEGIN PERFORM MakeAssistant(%s::varchar(32)); END; $$;", (assistant_nethz,))       
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