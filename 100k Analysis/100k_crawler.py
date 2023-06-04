import json
import sqlite3
import os
import subprocess


# clone project
def clone_project(git_repo_url):
    subprocess.run(["gh", "repo", "clone", git_repo_url])
    return True


# get releases
def get_releases():
    releases = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True).stdout.split("\n")
    return releases


# get latest versions
def get_latest_version():
    latest_version = subprocess.run(["git", "describe", "--abbrev=0", "--tags"], capture_output=True,
                                    text=True).stdout.split("\n")
    return latest_version


# execute infer
def execute_infer_on_releases(project, is_gradle):
    # create folder for results
    subprocess.run(["mkdir", "./../../results/" + project])
    releases = get_releases()

    # list of cost-reports that were already generated (in case of program crash)
    already_generated_files = [file for file in os.listdir("./../../results/" + project) if file.endswith('.json')]
    for release in releases[::-1]:
        if release != "":
            print("Starting to build")
            if release + "__costs-report.json" in already_generated_files:
                print(release + " was already generated, skipping")
                continue
            subprocess.run(["git", "checkout", release])
            if is_gradle:
                run_infer_gradle()
            else:
                run_infer_maven()

            # move costs report to results folder
            subprocess.run(["mv", "infer-out/costs-report.json",
                            "./../../results/" + project + "/" + release + "__costs-report.json"])
            # delete folder
            subprocess.run(["rm", "-f", "./infer-out", "-r"])
            # in case of gradle clean project
            if is_gradle:
                try:
                    subprocess.run(["./gradlew", "clean"])
                except FileNotFoundError:
                    print("Error when building with gradle")
                except PermissionError:
                    print("Permission Error")


# execute infer on gradle projects
def run_infer_gradle():
    try:
        subprocess.run(["infer", "--cost-only", "--", "./gradlew", "build", "-x", "test"])
    except FileNotFoundError:
        print("Error when building with gradle")
    except PermissionError:
        print("Permission Error, skipping")


# execute infer on maven projects
def run_infer_maven():
    subprocess.run(["infer", "--cost-only", "--", "mvn", "clean", "install", "-DskipTests"])


# delete repository to save disc space
def delete_project(project_name):
    subprocess.run(["rm", project_name, "-r", "-f"])


# connect to database
conn = sqlite3.connect('../database/infer_results.db')

c = conn.cursor()
wd = os.getcwd()

# open JAigantic dataset
with open('projects.json') as f:
    project_list = json.load(f)

# iterate through dataset
for author in project_list:

    # check if project has more than 100 github stars
    if int(project_list[author]['github']['stars']) < 100:
        continue

    # get repository data
    repository = project_list[author]['github']['repository']
    stars = project_list[author]['github']['stars']

    c.execute("SELECT * FROM Project WHERE NAME =  ?", (repository,))
    result = c.fetchone()
    conn.commit()
    if result:
        print(f"{repository} already exists")
        continue

    # clone the project
    successful_clone = clone_project(project_list[author]['github']['github_link'])
    if not successful_clone:
        continue

    # check if project is gradle or maven
    is_gradle = project_list[author]['systems']['build_types']['gradle']
    is_maven = project_list[author]['systems']['build_types']['maven']

    # get the latest version
    try:
        os.chdir(wd + "/" + repository)
    except FileNotFoundError:
        print("Unable to clone " + repository)
        continue

    # check if there are releases
    if len(get_releases()) < 1:
        os.chdir(wd)
        delete_project(repository)
        print("No releases")
        continue
    latest = get_latest_version()[0]
    subprocess.run(["git", "checkout", latest])

    # execute infer
    if is_maven:
        run_infer_maven()
    elif is_gradle:
        run_infer_gradle()
    else:
        os.chdir(wd)
        delete_project(repository)
        print("not java or maven")
        continue

    c.execute("INSERT INTO Project (name, url, stars) VALUES (?, ?, ?)", (repository,
                                                                          project_list[author]['github'][
                                                                              'github_link'],
                                                                          stars))
    conn.commit()
    # check if infer works (if not, project is deleted, and we go back to home dir)
    try:
        if not os.path.getsize("infer-out/costs-report.json") > 5:
            os.chdir(wd)
            delete_project(repository)
            continue
    except FileNotFoundError:
        os.chdir(wd)
        delete_project(repository)
        continue

    # we know that infer works, and we execute it on all releases
    print("Executing on all releases: " + repository)
    execute_infer_on_releases(repository, is_gradle)
    os.chdir(wd)
    delete_project(repository)
