
from github import Github as gh
from os import getenv
from github import GithubException
from datetime import datetime
from itertools import cycle
from threading import Thread
from time import sleep
from sys import stdout


class GetInactiveRepos(gh):
    
    def __init__(self):
      
        self.DEADLINE_IN_DAYS= 365
        
        self.progress = False
        load = Thread(target=self.animate)
        load.start()

        self.GH_TOKEN = getenv('GITHUB_TOKEN')
        self.GH_ACCOUNT = gh(self.GH_TOKEN, per_page=1000)
        self.GH_ORG = self.GH_ACCOUNT.get_organization('gbprojectbr')  
        self.GH_RATE_LIMIT = self.GH_ACCOUNT.get_rate_limit()

        try:
            worker = Thread(target=self.get_inactive_repos)
            self.progress = self.get_inactive_repos()
            worker.start()
        except GithubException as error:
            print(error)
            exit()

        print(self.progress)


    def animate(self):
        for c in cycle(['|', '/', '-', '|', '-', '\\']):
            if self.progress:
                break
            stdout.write('\r Vasculhando velharia no Github. Aguarde...   ' + c +'\t')
            stdout.flush()
            sleep(0.1)
        stdout.write('\rDone!')


    def get_inactive_repos(self):
        inactive_repos=[]

        for repo in self.all_github_repos(): 
            if self.GH_RATE_LIMIT.search.remaining == 0:
                sleep(60) 
            if repo.archived or repo.size == 0:
                continue

            repo_info= self.get_last_commit(repo)
            if repo_info: 
                inactive_repos.append(repo_info)

        return inactive_repos


    def all_github_repos(self):
        try:
            return self.GH_ORG.get_repos("visibility=all")
        except GithubException as e:
            print(e)
            exit()


    def get_last_commit(self,repo):
        current_date = datetime.today()
        
        try:
            commits = repo.get_commits()
        except GithubException as e:
            print(repo.name, e)
            return False

        last_update = repo.updated_at
        
        if commits.totalCount:
            repo_info={}
            last_commit_date=commits[0].commit.committer.date
            if last_commit_date > last_update:
                last_update = last_commit_date

        last_actvt_days = (current_date - last_update).days

        if int(last_actvt_days) > self.DEADLINE_IN_DAYS:
            repo_info['name']=repo.name
            repo_info['inactivity']=last_actvt_days
            return repo_info

        return False

GetInactiveRepos()
