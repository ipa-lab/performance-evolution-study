import os
import subprocess
from packaging import version


def execute_diff(folder_path):
    # get all files from folder (=name should be equal to GitHub project name), take only the files
    # that start with a digit ( x.xx.x-costs-report.json) and have a file size bigger than 5 bytes
    # (this is done to avoid including releases where infer could not create an analysis)
    files = [file for file in os.listdir(folder_path) if file.endswith('.json') and
             os.path.getsize(folder_path + "/" + file) > 5]


    for report in files:
        try:
            version.parse(report.split("__costs-report.json")[0])
        except version.InvalidVersion:
            files.remove(report)

    files.sort(key=lambda x: (
        version.parse(x.split("__costs-report.json")[0])))
    for i in range(len(files) - 1):
        previous_version = os.path.join(folder_path, files[i])
        newer_version = os.path.join(folder_path, files[i + 1])
        # infer diff mode
        subprocess.run(["infer", "reportdiff", "--costs-current", newer_version, "--costs-previous", previous_version])
        # move infer-out folder and rename it
        subprocess.run(["mkdir", files[i].split("__costs-report")[0] + "___" +
                        files[i + 1].split("__costs-report")[0]])
        subprocess.run(["mv", "./infer-out/differential", folder_path + "/differential/" + files[i].split("__costs-report")[0] + "___" +
                        files[i + 1].split("__costs-report")[0]])
        print(files[i].split("__costs-report")[0])


# iterate through results folder
for folder in os.listdir("./results"):
        execute_diff("./results/" + folder)

