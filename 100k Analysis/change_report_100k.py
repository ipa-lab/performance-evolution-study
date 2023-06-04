import sqlite3

# connect to database
conn = sqlite3.connect('database/infer_results.db')

c = conn.cursor()

print("Number of projects analyzed: ")
c.execute("SELECT COUNT(distinct project_id) FROM RELEASE")
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

print("Number of bugs introduced (without TOP) where reason = Loop/Modeled Call")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND REASON = 'Loop/Modeled Call'")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where reason = Loop")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND REASON = 'Loop'")
print(c.fetchall())
conn.commit()

print("Number of bugs introduced (without TOP) where reason is not Loop but known")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND REASON != 'Loop' AND REASON != 'Loop/Modeled Call' AND REASON IS NOT NULL")
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
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = TRUE AND difference = 2")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP)")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where reason = Loop/Modeled Call")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON = 'Loop/Modeled Call'")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where reason = Loop")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON = 'Loop'")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where reason is not Loop but known")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON != 'Loop' AND REASON != 'Loop/Modeled Call' AND REASON IS NOT NULL")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where is unknown")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND REASON IS NULL")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where polynomial difference is 1")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND difference = 1 ")
print(c.fetchall())
conn.commit()

print("Number of bugs fixed (without TOP) where polynomial difference is not 1")
c.execute("SELECT COUNT(*) FROM Change WHERE INCREASE = FALSE AND difference = 2")
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
          "WHERE INCREASE is FALSE")
print(c.fetchall())
conn.commit()

print("Level of changes for increases")
c.execute("SELECT COUNT(CASE WHEN change_level = 0 THEN 1 END) as zero, "
          "COUNT(CASE WHEN change_level = 1 THEN 1 END) as one, "
          "COUNT(CASE WHEN change_level = 2 THEN 1 END) as two, "
          "COUNT(CASE WHEN change_level = 3 THEN 1 END) as three, "
          "COUNT(CASE WHEN change_level = 4 THEN 1 END) as four, "
          "COUNT(CASE WHEN change_level = 5 THEN 1 END) as five, "
          "COUNT(CASE WHEN change_level = 6 THEN 1 END) as six, "
          "COUNT(CASE WHEN change_level = 7 THEN 1 END) as seven, "
          "COUNT(CASE WHEN change_level = 8 THEN 1 END) as eight, "
          "COUNT(CASE WHEN change_level = 9 THEN 1 END) as nine, "
          "COUNT(CASE WHEN change_level = 10 THEN 1 END) as ten, "
          "COUNT(CASE WHEN change_level = 11 THEN 1 END) as eleven, "
          "COUNT(CASE WHEN change_level = 12 THEN 1 END) as twelve "
          "FROM (SELECT * FROM CHANGE GROUP BY hash, release_prior) as rows WHERE INCREASE = TRUE")
print(c.fetchall())
conn.commit()

print("Level of changes for increases")
c.execute("SELECT COUNT(CASE WHEN change_level = 0 THEN 1 END) as zero, "
          "COUNT(CASE WHEN change_level = 1 THEN 1 END) as one, "
          "COUNT(CASE WHEN change_level = 2 THEN 1 END) as two, "
          "COUNT(CASE WHEN change_level = 3 THEN 1 END) as three, "
          "COUNT(CASE WHEN change_level = 4 THEN 1 END) as four, "
          "COUNT(CASE WHEN change_level = 5 THEN 1 END) as five, "
          "COUNT(CASE WHEN change_level = 6 THEN 1 END) as six, "
          "COUNT(CASE WHEN change_level = 7 THEN 1 END) as seven, "
          "COUNT(CASE WHEN change_level = 8 THEN 1 END) as eight, "
          "COUNT(CASE WHEN change_level = 9 THEN 1 END) as nine, "
          "COUNT(CASE WHEN change_level = 10 THEN 1 END) as ten, "
          "COUNT(CASE WHEN change_level = 11 THEN 1 END) as eleven, "
          "COUNT(CASE WHEN change_level = 12 THEN 1 END) as twelve "
          "FROM (SELECT * FROM CHANGE GROUP BY hash, release_prior) as rows WHERE INCREASE = FALSE")
print(c.fetchall())
conn.commit()

c.execute("SELECT COUNT(*) FROM (SELECT * FROM CHANGE GROUP BY hash, release_prior) as rows WHERE INCREASE = TRUE AND REASON IS NOT NULL")
print(c.fetchall())
conn.commit()