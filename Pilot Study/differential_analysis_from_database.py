import json
import sqlite3
import os

# connect to database
conn = sqlite3.connect('database/infer_results.db')

result_dir = './results'

c = conn.cursor()
# fetch all increases (no 'Top' values)
c.execute(
    "SELECT * FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash AND f1.procedure_id = f2.procedure_id WHERE f1.release_id < f2.release_id "
    "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
    "f2.polynomial <> 'Top' AND CAST(f1.polynomial AS INTEGER) < CAST(f2.polynomial AS INTEGER)")
conn.commit()
all_increases = c.fetchall()
add_counter = 0
for increase in all_increases:
    function_hash = increase[0]
    release_id_before_change = int(increase[1])
    project_id = increase[2]
    procedure_id = increase[12]
    # try to evaluate the polynomial difference numerically
    try:
        polynomial_difference = int(increase[13]) - int(increase[5])
    # for values like 'log' we have to store differently
    except ValueError:
        polynomial_difference = "From " + increase[5] + " to " + increase[13]
    c.execute("SELECT VERSION FROM RELEASE WHERE ID = ? AND PROJECT_ID = ?", (release_id_before_change,
                                                                              project_id))
    release_version_prior = c.fetchone()[0]
    c.execute("SELECT VERSION FROM RELEASE WHERE ID = ? AND PROJECT_ID = ?", ((release_id_before_change + 1),
                                                                              project_id))
    release_version_after = c.fetchone()[0]

    c.execute("SELECT NAME FROM PROJECT WHERE ID = ?", (project_id,))
    project_name = c.fetchone()[0]
    try:
        with open(os.path.join(result_dir, project_name, release_version_prior + "_" + release_version_after,
                               "differential", "introduced.json"), 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found")
        continue

    found = False
    for bug in data:
        if bug.get('hash') == function_hash and bug.get('procedure') == procedure_id:
            found_counter = found_counter + 1
            bug_trace = bug.get('bug_trace')
            for o in bug_trace:
                if "Loop" in o.get('description'):
                    found = True
                    add_counter = add_counter + 1
                    c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                              "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                                release_id_before_change, "Loop",
                                                                                o.get('level'), True,
                                                                                polynomial_difference))
                    conn.commit()
                    break
                if 'Modeled call to' in o.get('description'):
                    found = True
                    add_counter = add_counter + 1
                    c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                              "increase,difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                               release_id_before_change,
                                                                               o.get('description'),
                                                                               o.get('level'), True,
                                                                               polynomial_difference))
                    conn.commit()
                    break
    if not found:
        add_counter = add_counter + 1
        c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior,"
                  "increase, difference) VALUES(?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                release_id_before_change, True, polynomial_difference))
        conn.commit()
print("Amount of increases: " + str(len(all_increases)))
print("Amount of found: " + str(found_counter))
# Select all changes from database
# identify name of release
# find change via hash and procedure_id
# evaluate change, store in database

#### DECREASE SECTION
print("DECREASE")

c.execute(
    "SELECT * FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash AND f1.procedure_id = f2.procedure_id WHERE f1.release_id < f2.release_id "
    "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
    "f2.polynomial <> 'Top' AND CAST(f1.polynomial AS INTEGER) > CAST(f2.polynomial AS INTEGER)")
conn.commit()
all_decreases = c.fetchall()
found_counter = 0
for increase in all_decreases:
    function_hash = increase[0]
    release_id_before_change = int(increase[1])
    project_id = increase[2]
    procedure_id = increase[12]
    try:
        polynomial_difference = int(increase[5]) - int(increase[13])
    except ValueError:
        polynomial_difference = "From " + increase[5] + " to " + increase[13]
    c.execute("SELECT VERSION FROM RELEASE WHERE ID = ? AND PROJECT_ID = ?", (release_id_before_change,
                                                                              project_id))
    release_version_prior = c.fetchone()[0]
    c.execute("SELECT VERSION FROM RELEASE WHERE ID = ? AND PROJECT_ID = ?", ((release_id_before_change + 1),
                                                                              project_id))
    release_version_after = c.fetchone()[0]

    c.execute("SELECT NAME FROM PROJECT WHERE ID = ?", (project_id,))
    project_name = c.fetchone()[0]
    try:
        with open(os.path.join(result_dir, project_name, release_version_prior + "_" + release_version_after,
                               "differential", "fixed.json"), 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        continue

    found = False
    for bug in data:
        if bug.get('hash') == function_hash and bug.get('procedure') == procedure_id:
            found_counter = found_counter + 1
            bug_trace = bug.get('bug_trace')
            for o in bug_trace:
                if "Loop" in o.get('description'):
                    found = True
                    add_counter = add_counter + 1
                    c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                              "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                                release_id_before_change, "Loop",
                                                                                o.get('level'), False,
                                                                                polynomial_difference))
                    conn.commit()
                    break
                if 'Modeled call to' in o.get('description'):
                    found = True
                    add_counter = add_counter + 1
                    c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                              "increase,difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                               release_id_before_change,
                                                                               o.get('description'),
                                                                               o.get('level'), False,
                                                                               polynomial_difference))
                    conn.commit()
                    break
    if not found:
        add_counter = add_counter + 1
        c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior,"
                  "increase, difference) VALUES(?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                release_id_before_change, False, polynomial_difference))
        conn.commit()
print("Amount of increases: " + str(len(all_decreases)))
print("Amount of found: " + str(found_counter))
print(add_counter)
