import git
import os

def getGitFiles(self,filePath):
	repo=git.Repo(filePath)
	fileString= repo.git.ls_files()
	filesList=fileString.split('\n')
	filesList.extend(repo.untracked_files)
	return filesList

def login(self):
	pass
	
