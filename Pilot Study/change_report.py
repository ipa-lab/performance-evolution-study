import sqlite3

# connect to database
conn = sqlite3.connect('database/infer_results2.db')

c = conn.cursor()

print("Number of projects analyzed: ")
c.execute("SELECT COUNT(id) FROM PROJECT")
print(c.fetchall())
conn.commit()

print("Number of releases analyzed: ")
c.execute("SELECT COUNT(id) FROM RELEASE")
print(c.fetchall())
conn.commit()

print("Number of unique functions analyzed: ")
c.execute("SELECT COUNT(DISTINCT  (procedure_id)) FROM FUNCTION")
print(c.fetchall())
conn.commit()

print("Number of changes (without TOP)")
c.execute("SELECT COUNT(*) FROM Change")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP)")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where reason = Loop")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND REASON = 'Loop'")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where reason is not Loop but known")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND REASON != 'Loop' AND REASON IS NOT NULL")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where is unknown")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND REASON IS NULL")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where polynomial difference is 1")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND difference = 1")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where polynomial difference is not 1")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND difference != 1")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP)")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where reason = Loop")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON = 'Loop'")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where reason is not Loop but known")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON != 'Loop' AND REASON IS NOT NULL")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where is unknown")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON IS NULL")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where polynomial difference is 1")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND difference = 1")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where polynomial difference is not 1")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND difference != 1")
print(c.fetchall())
conn.commit()

print("Values of polynomial values before increase: ")
c.execute("SELECT DISTINCT(polynomial) FROM CHANGE c LEFT JOIN FUNCTION f ON c.hash = f.hash "
          "AND c.procedure_id = f.procedure_id "
          "AND c.release_prior = f.release_id AND c.project_id = f.project_id "
          "WHERE INCREASE is TRUE")
print(c.fetchall())
conn.commit()

print("Values of polynomial values before decrease: ")
c.execute("SELECT DISTINCT(polynomial) FROM CHANGE c LEFT JOIN FUNCTION f ON c.hash = f.hash "
          "AND c.procedure_id = f.procedure_id "
          "AND c.release_prior = f.release_id AND c.project_id = f.project_id "
          "WHERE INCREASE is TRUE")
print(c.fetchall())
conn.commit()

print("Level of changes for increases")
c.execute("SELECT COUNT(CASE WHEN change_level = 0 THEN 1 END) as zero, "
          "COUNT(CASE WHEN change_level = 1 THEN 1 END) as one, "
          "COUNT(CASE WHEN change_level = 2 THEN 1 END) as two, "
          "COUNT(CASE WHEN change_level = 3 THEN 1 END) as three, "
          "COUNT(CASE WHEN change_level = 4 THEN 1 END) as four, "
          "COUNT(CASE WHEN change_level = 5 THEN 1 END) as five, "
          "COUNT(CASE WHEN change_level = 6 THEN 1 END) as six "
          "FROM Change WHERE INCREASE = TRUE")
print(c.fetchall())
conn.commit()

print("Level of changes for decreases")
c.execute("SELECT COUNT(CASE WHEN change_level = 0 THEN 1 END) as zero, "
          "COUNT(CASE WHEN change_level = 1 THEN 1 END) as one, "
          "COUNT(CASE WHEN change_level = 2 THEN 1 END) as two, "
          "COUNT(CASE WHEN change_level = 3 THEN 1 END) as three, "
          "COUNT(CASE WHEN change_level = 4 THEN 1 END) as four, "
          "COUNT(CASE WHEN change_level = 5 THEN 1 END) as five, "
          "COUNT(CASE WHEN change_level = 6 THEN 1 END) as six "
          "FROM Change WHERE INCREASE = FALSE")
print(c.fetchall())
conn.commit()
