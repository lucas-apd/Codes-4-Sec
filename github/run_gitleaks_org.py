##Requirements:
# sudo apt install python3 python3-pip curl -y
# pip3 install PyGithub
# 
# !/bin/bash
# GITLEAKS_VERSION=$(curl -s https://api.github.com/repos/zricethezav/gitleaks/releases/latest |  grep -oP '"tag_name": "\K(.*)(?=")') && wget https://github.com/zricethezav/gitleaks/releases/download/$GITLEAKS_VERSION/gitleaks-linux-amd64 && \
# mv gitleaks-linux-amd64 gitleaks && \
# chmod +x gitleaks && \
# sudo mv gitleaks /usr/local/bin/
# export GIT_TOKEN='YourGitTokenHere'
# python3 run_gitleaks_org.py -o orgname 

from github import Github as gh
from github import GithubException
from os import getenv, popen, path, getcwd
from time import sleep
from argparse import ArgumentParser


class RunGitLeaksOrg(gh):
    
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument(
            '-o',
            '--orgname',
            help='Exemplo: script.py -o <orgname>',
            required=True
            )

        args = parser.parse_args()
               
        self.GIT_TOKEN = getenv('GIT_TOKEN')
        self.GH_ACCOUNT = gh(args.gittoken, per_page=1000)
        self.GH_ORG = self.GH_ACCOUNT.get_organization(args.orgname)
        self.GH_RATE_LIMIT = self.GH_ACCOUNT.get_rate_limit()
        
        try:
            self.run_gitleaks()
        except GithubException as error:
            print(error)
        
    def run_gitleaks(self):
        location = path.realpath(
            path.join(getcwd(), path.dirname(__file__)))

        for repo in self.GH_ORG.get_repos("visibility=all"): 
            if self.GH_RATE_LIMIT.search.remaining == 0:
                sleep(60) 
            stream = ''
            report = path.join(location,f'{repo.name}.leaks.json')
            stream = popen(f'gitleaks -r {repo.html_url} --access-token={self.GIT_TOKEN} -o {report}')
            
            if "No leaks found" in stream.read():
                popen(f'rm -f {report}')


if __name__ == '__main__':
   RunGitLeaksOrg()
