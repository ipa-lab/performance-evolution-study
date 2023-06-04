import os
import subprocess


# checks out the releases
def get_releases():
    releases = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True).stdout.split("\n")
    return releases


def clone_project(git_repo_url):
    subprocess.run(["git", "clone", git_repo_url])


if __name__ == '__main__':
    # list of projects (for pilot study, list was manually adapted)
    projects = ["bundletool", "elasticsearch-java", "mybatis-plus", "zuul"]
    wd = os.getcwd()
    for project in projects:
        os.chdir(wd + "/" + project)
        releases = get_releases()
        for release in releases[::-1]:
            if release != "":
                print("Starting to build")
                subprocess.run(["git", "checkout", release])
                try:
                    # try to execute Infer (using gradlew)
                    # For maven, this command needs to be change to mvn build -DskipTests = True
                    subprocess.run(["infer", "--cost-only", "--", "./gradlew", "build", "-x", "test"])
                except FileNotFoundError:
                    continue
                # move cost report to result folder
                subprocess.run(["mv", "infer-out/costs-report.json",
                                "./../../results/" + project + "/" + release + "-costs-report.json"])
                # delete infer-out folder
                subprocess.run(["rm", "-f", "./infer-out", "-r"])
                try:
                    # clean
                    subprocess.run(["./gradlew", "clean"])
                except FileNotFoundError:
                    continue
