import git
import os



def getGitFiles(self,filePath):
	repo=Repo(filePath)
	fileString= repo.git.ls_files()
	fileList=fileString.split('\n')
	filesList.extend(repo.untracked_files)
	return filesList

def login(self):
	pass
	
