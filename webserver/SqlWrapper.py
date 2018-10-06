import psycopg2

def NotifyUserLogin (username):
	conn = psycopg2.connect("dbname=test user=postgres")
	cur = conn.cursor()	
	cur.execute("DO $$ BEGIN PERFORM NotifyUserLogin(%s); END; $$;", (username))	
	conn.commit()
	cur.close()
    conn.close()
	
def MakeAssistant (username):
	conn = psycopg2.connect("dbname=test user=postgres")
	cur = conn.cursor()	
	cur.execute("DO $$ BEGIN PERFORM MakeAssistant(%s); END; $$;", (username))	
	conn.commit()
	cur.close()
    conn.close()