import json
import sqlite3
import os

import packaging.version
from packaging import version

# connect to database
conn = sqlite3.connect('database/infer_results.db')

c = conn.cursor()

# read results
project_dir = './results'

# iterate through projects
for directory in os.listdir(project_dir):
    # check if the project is already in the database
    c.execute("SELECT * FROM Project WHERE name = ?", (directory,))
    project = c.fetchone()
    if project:
        print("Project " + directory[1] + "already exists")
    else:
        c.execute("INSERT INTO Project (name) VALUES (?)", (directory,))
        c.execute("SELECT * FROM Project WHERE name = ?", (directory,))
        project = c.fetchone()

    # start adding cost-report files from project into database
    cost_report_list = [cost_report for cost_report in os.listdir(project_dir + "/" + directory) if
                        cost_report.endswith('.json') and len(cost_report.split("-costs-report")) > 1
                        and os.path.getsize(os.path.join(project_dir, directory, cost_report)) > 5000]

    # remove reports whose version cannot be parsed from list
    for report in cost_report_list:
        try:
            version.parse(report.split("__costs-report.json")[0])
        except packaging.version.InvalidVersion:
            cost_report_list.remove(report)

    try:
        # sort by version
        cost_report_list.sort(key=lambda x: (
            version.parse(x.split("__costs-report.json")[0])))

        for index, cost_report in enumerate(cost_report_list):
            # fetch release Version
            release_version = cost_report.split("-costs-report")[0]
            print(release_version)
            # check if release is already in database
            c.execute("SELECT * FROM Release WHERE version = ? and project_id = ?", (release_version, project[0]))
            release = c.fetchone()
            if release:
                print("Release " + release_version + " already exists")
            else:
                c.execute("INSERT INTO Release (id, project_id, version) VALUES (?,?,?)",
                          (index, project[0], release_version))
                c.execute("SELECT * FROM Release WHERE version = ? and project_id = ?", (release_version, project[0]))
                release = c.fetchone()

            # open the cost report
            with open(os.path.join(project_dir + "/" + directory, cost_report), 'r') as f:
                data = json.load(f)

            for function in data:
                hash_field = function.get('hash')
                procedure_id = function.get('procedure_id')
                c.execute("SELECT * FROM Function WHERE hash = ? and procedure_id = ? and release_id = ?", (hash_field,
                                                                                                            procedure_id,
                                                                                                            release[0]))
                f = c.fetchone()
                if not f:
                    procedure_name = function.get('procedure_name')
                    polynomial = function.get('exec_cost', {}).get('hum', {}).get('hum_degree')
                    big_o = function.get('exec_cost', {}).get('hum', {}).get('big_o')
                    trace = json.dumps(function.get('exec_cost', {}).get('trace'))
                    c.execute("INSERT INTO FUNCTION(hash, release_id, project_id, procedure_name, procedure_id, "
                              "polynomial, bigo, trace) VALUES (?,?,?,?,?,?,?,?)", (hash_field, release[0], project[0],
                                                                                    procedure_name, procedure_id,
                                                                                    polynomial, big_o, trace))
        conn.commit()
    except packaging.version.InvalidVersion:
        print("Unable to sort for project: " + directory)
