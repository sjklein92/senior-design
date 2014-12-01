import git
import os

def getGitFiles(filePath):
	repo=git.Repo(filePath)
	fileString= repo.git.ls_files()
	filesList=fileString.split('\n')
	filesList.extend(repo.untracked_files)
	return filesList

def statuses(filePath):
	repo=git.Repo(filePath)
	statusString=repo.git.status('-s')
	statuslist=statusString.split('\n')
	for string in statuslist:
		tempSplit=string.split()
		statusDict[tempSplit[1]]=tempSplit[0]
	return statusDict

def commit(message):
	subprocess.call(["git", "commit", "-a" ,"-m",message])
	subprocess.call(["git", "push"])
