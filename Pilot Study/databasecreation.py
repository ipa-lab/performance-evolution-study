import sqlite3

# connect to database
conn = sqlite3.connect('database/infer_results.db')

c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS PROJECT(id integer PRIMARY KEY AUTOINCREMENT, name text, url text, stars integer)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS RELEASE(id integer, project_id integer, version text, PRIMARY KEY (id, project_id),
FOREIGN KEY (project_id) REFERENCES PROJECT(id))
""")

c.execute("""
CREATE TABLE IF NOT EXISTS FUNCTION(hash string, release_id integer, project_id integer, procedure_name text,
 procedure_id text, polynomial text, bigo text, trace text, PRIMARY KEY (hash, procedure_id, release_id, project_id),  FOREIGN KEY(release_id) 
 REFERENCES RELEASES(ID), FOREIGN KEY(project_id) REFERENCES PROJECT(ID))
""")

conn.commit()
