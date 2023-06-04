import sqlite3

# connect to database
conn = sqlite3.connect('infer_results_server.db')

c = conn.cursor()

print("Number of projects analyzed: ")
c.execute("SELECT COUNT(id) FROM PROJECT")
print(c.fetchall())
conn.commit()

print("Number of releases analyzed: ")
c.execute("SELECT COUNT(id) FROM RELEASE")
print(c.fetchall())
conn.commit()

print("Number of projects analyzed: ")
c.execute("SELECT COUNT(DISTINCT project_id) FROM RELEASE")
print(c.fetchall())
conn.commit()

print("Number of unique functions analyzed: ")
c.execute("SELECT COUNT(*) FROM (SELECT DISTINCT hash, procedure_id FROM FUNCTION) as sub")
print(c.fetchall())
conn.commit()

print("Number of changes (without TOP) in values")
c.execute("SELECT f1.polynomial, f2.polynomial FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
          "AND f1.project_id = f2.project_id "
          "WHERE f1.release_id < f2.release_id AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial "
          "AND f1.polynomial <> 'Top' AND f2.polynomial <> 'Top' ")
print(c.fetchall())
conn.commit()

print("Number of changes (without TOP)")
c.execute("SELECT COUNT(*) FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
          "AND f1.project_id = f2.project_id WHERE f1.release_id < f2.release_id "
          "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
          "f2.polynomial <> 'Top'")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP)")
c.execute("SELECT COUNT(*) FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
          "AND f1.project_id = f2.project_id WHERE f1.release_id < f2.release_id "
          "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
          "f2.polynomial <> 'Top' AND CAST(f1.polynomial AS INTEGER) < CAST(f2.polynomial AS INTEGER)")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP)")
c.execute("SELECT COUNT(*) FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
          "AND f1.project_id = f2.project_id WHERE f1.release_id < f2.release_id "
          "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
          "f2.polynomial <> 'Top' AND CAST(f1.polynomial AS INTEGER) > CAST(f2.polynomial AS INTEGER)")
print(c.fetchall())
conn.commit()

print("Number of changes (only TOP)")
c.execute("SELECT COUNT(*) FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
          "AND f1.project_id = f2.project_id WHERE f1.release_id < f2.release_id "
          "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND (f1.polynomial = 'Top' OR "
          "f2.polynomial = 'Top')")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (only TOP)")
c.execute("SELECT COUNT(*) FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
           "AND f1.project_id = f2.project_id WHERE f1.release_id < f2.release_id "
           "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND (f1.polynomial = 'Top' OR "
           "f2.polynomial = 'Top') AND f1.polynomial = 'Top'")
print(c.fetchall())
conn.commit()
#
print("Number of bugs fixed (only TOP)")
c.execute("SELECT COUNT(*) FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash "
          "AND f1.procedure_id = f2.procedure_id "
          "AND f1.project_id = f2.project_id WHERE f1.release_id < f2.release_id "
          "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND (f1.polynomial = 'Top' OR "
          "f2.polynomial = 'Top') AND f2.polynomial = 'Top'")
print(c.fetchall())
conn.commit()
