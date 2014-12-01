import git
import os
import subprocess

def commit(filePath, message):
    old_pwd = os.path.abspath(os.curdir)
    os.chdir(filePath)
    if subprocess.call(["git", "commit", "-a" ,"-m", message]) != 0:
        os.chdir(old_pwd)
        return False
    success = (subprocess.call(["git", "push"]) == 0)
    os.chdir(old_pwd)
    return success

def getGitFiles( filePath):
    repo = git.Repo(filePath)
    fileString = repo.git.ls_files()
    filesList = fileString.split('\n')
    filesList.extend(repo.untracked_files)
    return filesList


def statuses( filePath):
    repo = git.Repo(filePath)
    statusString = repo.git.status('--porcelain')
    statuslist = statusString.split('\n')
    statusDict = {}
    for string in statuslist:
        statusDict['/'+string[3:]]=string[0:2]
    return statusDict
