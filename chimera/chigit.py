import git
import os

def getGitFiles(self, filePath):
    repo = git.Repo(filePath)
    fileString = repo.git.ls_files()
    filesList = fileString.split('\n')
    filesList.extend(repo.untracked_files)
    return filesList

def cloneRepo(self, url, filePath):
    git.Repo(url,filePath)

def statuses(self, filePath):
    repo = git.Repo(filePath)
    statusString = repo.git.status('--porcelain')
    statuslist = statusString.split('\n')
    statusDict = {}
    for string in statuslist:
        statusDict['/'+string[3:]]=string[0:2]
    return statusDict
