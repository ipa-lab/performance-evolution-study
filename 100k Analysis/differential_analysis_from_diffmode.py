import json
import sqlite3
import os

# connect to database
conn = sqlite3.connect('database/infer_results.db')

c = conn.cursor()

project_dir = './results'

# internal counters (not important for analysis)
found_counter = 0
total_counter = 0
already_entered_counter = 0
not_found_counter = 0
add_counter = 0

# iterate through projects
for project in os.listdir(project_dir):
    for release in os.listdir(os.path.join(project_dir, project)):
        if not release.endswith('.json'):
            # we look at all generated diff reports by Infer
            try:
                with open(os.path.join(project_dir, project, release,
                                       "differential", "introduced.json"), 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                continue
            res = None
            if len(release.split('___')) >= 2:
                c.execute("SELECT ID FROM RELEASE WHERE VERSION = ?", (release.split('___')[0],))
                res = c.fetchone()
            if res is None:
                continue
            release_id_prior = int(res[0])
            c.execute("SELECT ID FROM PROJECT WHERE NAME = ?", (project,))
            res = c.fetchone()
            project_id = int(res[0])
            if res is None:
                continue
            # iterate through the detected performance bugs by Infer
            for bug in data:
                # exclude 'Top' - complexity bugs
                if '`TOP`' in bug.get('qualifier'):
                    continue
                total_counter = total_counter + 1
                hash = bug.get('hash')
                procedure_id = bug.get('procedure')
                c.execute("SELECT * FROM FUNCTION WHERE RELEASE_ID = ? AND HASH = ? "
                          "AND PROJECT_ID = ?", (release_id_prior, hash, project_id))
                function_prior = c.fetchone()

                c.execute("SELECT * FROM FUNCTION WHERE RELEASE_ID = ? AND HASH = ? AND PROCEDURE_ID = ? "
                          "AND PROJECT_ID = ?", ((release_id_prior + 1), hash, procedure_id, project_id))
                function_after = c.fetchone()
                if function_after is None or function_prior is None:
                    continue
                # getting polynomial difference
                try:
                    polynomial_difference = int(function_after[5]) - int(function_prior[5])
                except ValueError:
                    polynomial_difference = "From " + function_prior[5] + " to " + function_after[5]

                if not function_prior[5] == function_after[5]:
                    c.execute("SELECT * FROM CHANGE WHERE RELEASE_PRIOR = ? AND HASH = ? AND PROCEDURE_ID = ? "
                              "AND PROJECT_ID = ?", (release_id_prior, hash, procedure_id, project_id))
                    change = c.fetchone()
                    if change is not None:
                        already_entered_counter += 1
                        continue
                    bug_trace = bug.get('bug_trace')
                    found_counter = found_counter + 1
                    found = False

                    loop = False
                    modeled_call = False
                    max_level = 0
                    modeled_call_description = ''
                    # we iterate through the change/bug trace
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
                        c.execute(
                            "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                            "increase,difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                             release_id_prior,
                                                                             'Loop/Modeled Call',
                                                                             max_level, True,
                                                                             polynomial_difference))
                        conn.commit()
                        add_counter = add_counter + 1
                    elif loop:
                        c.execute(
                            "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                            "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                              release_id_prior, "Loop",
                                                                              max_level, True,
                                                                              polynomial_difference))
                        conn.commit()
                        add_counter = add_counter + 1
                    elif modeled_call:
                        c.execute(
                            "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                            "increase,difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                             release_id_prior,
                                                                             modeled_call_description,
                                                                             max_level, True,
                                                                             polynomial_difference))
                        conn.commit()
                        add_counter = add_counter + 1

                    if not found:
                        not_found_counter += 1

print('TOTAL COUNTER:' + str(total_counter))
print('FOUND COUNTER:' + str(found_counter))
print("NOT FOUND" + str(not_found_counter))
print("ADDC" + str(add_counter))
print("Already entered" + str(already_entered_counter))



#### DECREASE SECTION
found_counter = 0
total_counter = 0
add_counter = 0
not_found_counter = 0
already_entered_counter = 0

for project in os.listdir(project_dir):
    for release in os.listdir(os.path.join(project_dir, project)):
        if not release.endswith('.json'):
            # look at Infer's differential mode decrease section
            try:
                with open(os.path.join(project_dir, project, release,
                                       "differential", "fixed.json"), 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                continue
            res = None
            # get release from database
            if len(release.split('___')) >= 2:
                c.execute("SELECT ID FROM RELEASE WHERE VERSION = ?", (release.split('___')[0],))
                res = c.fetchone()

            if res is None:
                continue
            release_id_prior = int(res[0])
            c.execute("SELECT ID FROM PROJECT WHERE NAME = ?", (project,))
            res = c.fetchone()
            project_id = int(res[0])
            # iterate through detected bugs/changes by Infer
            for bug in data:
                # exclude Top values
                if '`TOP`' in bug.get('qualifier') or 'Top' in bug.get('qualifier'):
                    continue
                total_counter = total_counter + 1
                hash = bug.get('hash')
                procedure_id = bug.get('procedure')
                c.execute("SELECT * FROM FUNCTION WHERE RELEASE_ID = ? AND HASH = ? "
                          "AND PROJECT_ID = ?", (release_id_prior, hash, project_id))
                function_prior = c.fetchone()

                c.execute("SELECT * FROM FUNCTION WHERE RELEASE_ID = ? AND HASH = ? AND PROCEDURE_ID = ? "
                          "AND PROJECT_ID = ?", ((release_id_prior + 1), hash, procedure_id, project_id))
                function_after = c.fetchone()
                if function_after is None or function_prior is None:
                    continue
                try:
                    polynomial_difference = int(function_prior[5]) - int(function_after[5])
                except ValueError:
                    polynomial_difference = "From " + function_prior[5] + " to " + function_after[5]

                if not function_prior[5] == function_after[5]:
                    c.execute("SELECT * FROM CHANGE WHERE RELEASE_PRIOR = ? AND HASH = ? AND PROCEDURE_ID = ? "
                              "AND PROJECT_ID = ?", (release_id_prior, hash, procedure_id, project_id))
                    change = c.fetchone()
                    if change is not None:
                        already_entered_counter += 1
                        continue
                    bug_trace = bug.get('bug_trace')
                    found_counter = found_counter + 1

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
                    # save change in change table
                    if loop and modeled_call:
                        c.execute(
                            "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                            "increase,difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                             release_id_prior,
                                                                             'Loop/Modeled Call',
                                                                             max_level, False,
                                                                             polynomial_difference))
                        conn.commit()
                        add_counter = add_counter + 1
                    elif loop:
                        c.execute(
                            "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                            "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                              release_id_prior, "Loop",
                                                                              max_level, False,
                                                                              polynomial_difference))
                        conn.commit()
                        add_counter = add_counter + 1
                    elif modeled_call:
                        c.execute(
                            "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                            "increase,difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                             release_id_prior,
                                                                             modeled_call_description,
                                                                             max_level, False,
                                                                             polynomial_difference))
                        conn.commit()
                        add_counter = add_counter + 1
                    else:
                      not_found_counter += 1

'''
print('TOTAL COUNTER:' + str(total_counter))
print('FOUND COUNTER:' + str(found_counter))
print("ALREADY ENTERED " + str(already_entered_counter))
print("NOT FOUND " + str(not_found_counter))
print("ADDC" + str(add_counter))
'''
