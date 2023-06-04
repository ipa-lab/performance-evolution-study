import json
import sqlite3
import os

# connect to database
conn = sqlite3.connect('database/infer_results2.db')

c = conn.cursor()

project_dir = './results'

# iterate through projects
found_counter = 0
total_counter = 0
for project in os.listdir(project_dir):
    # iterate through files projects
    for release in os.listdir(os.path.join(project_dir, project)):
        # only look at differential folders
        if not release.endswith('.json'):
            try:
                with open(os.path.join(project_dir, project, release,
                                       "differential", "introduced.json"), 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                continue
            c.execute("SELECT ID FROM RELEASE WHERE VERSION = ?", (release.split('_')[0],))
            release_id_prior = int(c.fetchone()[0])
            c.execute("SELECT ID FROM PROJECT WHERE NAME = ?", (project,))
            project_id = int(c.fetchone()[0])
            # iterate through bugs reported by infer
            for bug in data:
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
                try:
                    polynomial_difference = int(function_after[5]) - int(function_prior[5])
                except ValueError:
                    polynomial_difference = "From " + function_prior[5] + " to " + function_after[5]
                if not function_prior[5] == function_after[5]:
                    c.execute("SELECT * FROM CHANGE WHERE RELEASE_PRIOR = ? AND HASH = ? AND PROCEDURE_ID = ? "
                              "AND PROJECT_ID = ?", (release_id_prior, hash, procedure_id, project_id))
                    change = c.fetchone()
                    # check if change is already tracked
                    if change is not None:
                        continue
                    bug_trace = bug.get('bug_trace')
                    found_counter = found_counter + 1
                    # check if bug is type loop or modeled call
                    for o in bug_trace:
                        if "Loop" in o.get('description'):
                            found = True
                            c.execute(
                                "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                                "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                    release_id_prior, "Loop", o.get('level'),
                                                                    True, polynomial_difference))
                            conn.commit()
                            break
                        if 'Modeled call to' in o.get('description'):
                            found = True
                            c.execute(
                                "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                                "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                    release_id_prior, o.get('description'),
                                                                    o.get('level'), True, polynomial_difference))
                            conn.commit()
                            break

print('TOTAL COUNTER:' + str(total_counter))
print('FOUND COUNTER:' + str(found_counter))


#### DECREASE SECTION


found_counter = 0
total_counter = 0
for project in os.listdir(project_dir):
    # iterate through files projects
    for release in os.listdir(os.path.join(project_dir, project)):
        # only look at differential folders
        if not release.endswith('.json'):
            try:
                with open(os.path.join(project_dir, project, release,
                                       "differential", "fixed.json"), 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                continue
            c.execute("SELECT ID FROM RELEASE WHERE VERSION = ?", (release.split('_')[0],))
            release_id_prior = int(c.fetchone()[0])
            c.execute("SELECT ID FROM PROJECT WHERE NAME = ?", (project,))
            project_id = int(c.fetchone()[0])
            # iterate through bugs reported by infer
            for bug in data:
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
                    # check if change is already tracked
                    if change is not None:
                        continue
                    bug_trace = bug.get('bug_trace')
                    found_counter = found_counter + 1
                    # check if bug is type loop or modeled call
                    for o in bug_trace:
                        if "Loop" in o.get('description'):
                            found = True
                            c.execute(
                                "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                                "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                    release_id_prior, "Loop", o.get('level'),
                                                                    False, polynomial_difference))
                            conn.commit()
                            break
                        if 'Modeled call to' in o.get('description'):
                            found = True
                            c.execute(
                                "INSERT INTO CHANGE(PROJECT_ID, hash, procedure_id, release_prior, reason, change_level, "
                                "increase, difference) VALUES(?,?,?,?,?,?,?,?)", (project_id, hash, procedure_id,
                                                                    release_id_prior, o.get('description'),
                                                                    o.get('level'), False, polynomial_difference))
                            conn.commit()
                            break

print('TOTAL COUNTER:' + str(total_counter))
print('FOUND COUNTER:' + str(found_counter))