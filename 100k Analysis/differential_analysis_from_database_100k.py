import json
import sqlite3
import os

# connect to database
conn = sqlite3.connect('database/infer_results.db')

# internal counters, not important
add_counter = 0
found_counter = 0
not_found_counter = 0
no_reason_found = 0

# THIS IS THE INCREASE EVALUATION
print("INCREASE")
c = conn.cursor()
# select all detected changes through function table
c.execute(
    "SELECT * FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash AND f1.procedure_id = f2.procedure_id WHERE f1.release_id < f2.release_id "
    "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
    "f2.polynomial <> 'Top' AND CAST(f1.polynomial AS INTEGER) < CAST(f2.polynomial AS INTEGER)")
conn.commit()
all_increases = c.fetchall()

# iterate through detected changes
for increase in all_increases:
    function_hash = increase[0]
    release_id_before_change = int(increase[1])
    project_id = increase[2]
    procedure_id = increase[12]
    # try to get the numerical polynomial difference, in cases like 'log' we get ValueError and save 'From - To '-string
    try:
        polynomial_difference = int(increase[13]) - int(increase[5])
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
    # we try to open Infer's differential file to access the changes
    try:
        with open(os.path.join("results", project_name, release_version_prior + "___" + release_version_after,
                               "differential", "introduced.json"), 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found: " + project_name + " " + release_version_prior + "___" + release_version_after)
        continue

    found = False
    # we iterate through the file to see if Infer detected the change
    for bug in data:
        if bug.get('hash') == function_hash and bug.get('procedure') == procedure_id:
            bug_trace = bug.get('bug_trace')
            loop = False
            modeled_call = False
            max_level = 0
            modeled_call_description = ''
            for o in bug_trace:
                if "Loop" in o.get('description'):
                    found = True
                    loop = True
                    if int(o.get('level')) > max_level:
                        max_level = o.get('level')
                if 'Modeled call to' in o.get('description'):
                    found = True
                    modeled_call = True
                    modeled_call_description = o.get('description')
                    if int(o.get('level')) > max_level:
                        max_level = o.get('level')
            # if we find the change, we enter the reason (loop/modeled call/both) and save it in Change table
            if loop and modeled_call:
                c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                          "increase,difference, infer_detected) VALUES(?,?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                           release_id_before_change,
                                                                           'Loop/Modeled Call',
                                                                           max_level, True,
                                                                           polynomial_difference, 1))
                conn.commit()
                add_counter = add_counter + 1
                found_counter = found_counter + 1
            elif loop:
                c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                          "increase, difference, infer_detected) VALUES(?,?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                            release_id_before_change, "Loop",
                                                                            max_level, True,
                                                                            polynomial_difference, 1))
                conn.commit()
                add_counter = add_counter + 1
                found_counter = found_counter + 1
            elif modeled_call:
                c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                          "increase,difference, infer_detected) VALUES(?,?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                           release_id_before_change,
                                                                           modeled_call_description,
                                                                           max_level, True,
                                                                           polynomial_difference, 1))

                conn.commit()
                add_counter = add_counter + 1
                found_counter = found_counter + 1

    # if we do not find it, we still Enter in Change table but do not add a reason/level
    if not found:
        add_counter = add_counter + 1
        not_found_counter += 1
        c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior,"
                  "increase, difference) VALUES(?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                release_id_before_change, True, polynomial_difference))
        conn.commit()

print("Amount of increases: " + str(len(all_increases)))
print("Amount of found: " + str(found_counter))
print("Amount of not found: " + str(not_found_counter))
print("Added: " + str(add_counter))
print("Amount of no reason found: " + str(no_reason_found))
#Select all changes from database
#identify name of release
#find change via hash and procedure_id
#evaluate change, store in database

#### DECREASE SECTION
print("DECREASE")

found_counter = 0
not_found_counter = 0
add_counter = 0
no_reason_found = 0

# we do the same for decreases
c.execute(
    "SELECT * FROM Function f1 JOIN Function f2 ON f1.hash = f2.hash AND f1.procedure_id = f2.procedure_id WHERE f1.release_id < f2.release_id "
    "AND f2.release_id - f1.release_id = 1 AND f1.polynomial <> f2.polynomial AND f1.polynomial <> 'Top' AND "
    "f2.polynomial <> 'Top' AND CAST(f1.polynomial AS INTEGER) > CAST(f2.polynomial AS INTEGER)")
conn.commit()
all_decreases = c.fetchall()

# we iterate through decreases
for decrease in all_decreases:
    function_hash = decrease[0]
    release_id_before_change = int(decrease[1])
    project_id = decrease[2]
    procedure_id = decrease[12]
    try:
        polynomial_difference = int(decrease[5]) - int(decrease[13])
    except ValueError:
        polynomial_difference = "From " + decrease[5] + " to " + decrease[13]
    c.execute("SELECT VERSION FROM RELEASE WHERE ID = ? AND PROJECT_ID = ?", (release_id_before_change,
                                                                              project_id))
    release_version_prior = c.fetchone()[0]
    c.execute("SELECT VERSION FROM RELEASE WHERE ID = ? AND PROJECT_ID = ?", ((release_id_before_change + 1),
                                                                              project_id))

    result = c.fetchone()
    if result is None:
        continue

    release_version_after = result[0]

    c.execute("SELECT NAME FROM PROJECT WHERE ID = ?", (project_id,))
    project_name = c.fetchone()[0]

    # we try to find the file generated by Infer's differential mode
    try:
        with open(os.path.join("results", project_name, release_version_prior + "___" + release_version_after,
                               "differential", "fixed.json"), 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found: " + project_name + " " + release_version_prior + "___" + release_version_after)
        continue

    found = False

    # we iterate through the file to see if Infer detected the change
    for bug in data:
        if bug.get('hash') == function_hash and bug.get('procedure') == procedure_id:
            bug_trace = bug.get('bug_trace')
            loop = False
            modeled_call = False
            max_level = 0
            modeled_call_description = ''
            for o in bug_trace:
                if "Loop" in o.get('description'):
                    found = True
                    loop = True
                    if int(o.get('level')) > max_level:
                        max_level = o.get('level')
                if 'Modeled call to' in o.get('description'):
                    found = True
                    modeled_call = True
                    modeled_call_description = o.get('description')
                    if int(o.get('level')) > max_level:
                        max_level = o.get('level')
            if loop and modeled_call:
                c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                          "increase,difference, infer_detected) VALUES(?,?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                           release_id_before_change,
                                                                           'Loop/Modeled Call',
                                                                           max_level, False,
                                                                           polynomial_difference, 1))
                conn.commit()
                add_counter = add_counter + 1
                found_counter = found_counter + 1
            elif loop:
                c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                          "increase, difference, infer_detected) VALUES(?,?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                            release_id_before_change, "Loop",
                                                                            max_level, False,
                                                                            polynomial_difference, 1))
                conn.commit()
                add_counter = add_counter + 1
            elif modeled_call:
                c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                          "increase,difference, infer_detected) VALUES(?,?,?,?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                           release_id_before_change,
                                                                           modeled_call_description,
                                                                           max_level, False,
                                                                           polynomial_difference, 1))
                conn.commit()
                add_counter = add_counter + 1
                found_counter = found_counter + 1

    # if we do not find it, we still Enter in Change table but do not add a reason/level
    if not found:
        add_counter = add_counter + 1
        not_found_counter += 1
        c.execute("INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior,"
                  "increase, difference) VALUES(?,?,?,?,?,?)", (project_id, function_hash, procedure_id,
                                                                release_id_before_change, False, polynomial_difference))
        conn.commit()
print("Amount of increases: " + str(len(all_increases)))
print("Amount of found: " + str(found_counter))
print("Amount of not found: " + str(not_found_counter))
print("Added: " + str(add_counter))
print("Amount of no reason found: " + str(no_reason_found))