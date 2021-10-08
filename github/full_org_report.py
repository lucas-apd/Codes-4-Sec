# Requirements:
# pip3 install pygithub
from os import getenv, name
from github import Github as gh
from github import GithubException, RateLimitExceededException, UnknownObjectException
from time import sleep, gmtime
from datetime import datetime
from collections import Counter
from json import dumps
from calendar import timegm
from requests import post

class GithubOverview(gh):
    
    def __init__(self):
        self.ORG_NAME = getenv('GITHUB_ORG', default=None) # < Export Yout GitHub Org Name env variable! (export GITHUB_ORG='name')
        self.GH_TOKEN = getenv('GITHUB_TOKEN', default=None) # < Export Yout GitHub Token env variable! (export GITHUB_TOKEN='token')
        if not self.GH_TOKEN or not self.ORG_NAME:
            print('All variables are required: GITHUB_ORG e GITHUB_TOKEN')
            exit()

        self.GH_ACCOUNT = gh(self.GH_TOKEN, per_page=1000)
        self.GH_ORG = self.GH_ACCOUNT.get_organization(self.ORG_NAME)  
        self.GH_RATE_LIMIT = self.GH_ACCOUNT.get_rate_limit()      
        
        self.health_check()

        self.all_org_repos = self.safe_query_execute(self.GH_ORG.get_repos, type="all")
        self.all_langs= self.get_org_langs()
        self.org_report = {}
        self.org_report['Date'] = str(datetime.today().date())
        self.org_report['Org'] = self.get_org_infos()
        
        self.report_exporter(self.org_report)
        
    def health_check(self):
        if not self.GH_ORG.raw_data or self.GH_ORG.raw_data['login'] != self.ORG_NAME:
            print("Github Health Check Error")
            exit()

    def get_org_infos(self):
        org_infos = {}
        org_infos["Org_Name"] = self.ORG_NAME
        org_infos["Total_Repos"] = self.all_org_repos.totalCount
        org_infos["Public_Repos"] = [r.name for r in self.safe_query_execute(self.GH_ORG.get_repos, type="public") if not r.fork]
        org_infos["Used_Languages"] = list(dict.fromkeys(self.all_langs))
        org_infos["Common_Languages"] = [lang for lang, repo_count in Counter(self.all_langs).most_common(5)]
        org_infos["Total_Members"] = len(self.get_org_members())
        org_infos["Teams"] = self.get_org_teams()
        org_infos["Admins"] = self.get_org_admins()
        org_infos["Repos"] = self.get_repos_infos()            
        org_infos["Archived_Repos"] = self.archived_repos
        org_infos["Forked_Repos"] = self.forked_repos

        return org_infos

    def get_all_org_repos(self):
        try:
            return self.GH_ORG.get_repos("visibility=all")
        except GithubException as e:
            print(e)
            exit()

    def get_org_langs(self):
        self.archived_repos = 0
        self.forked_repos = 0
        all_repos_langs=[]
        excluded_langs=['Makefile', 'Dockerfile']

        for repo in self.all_org_repos:  
            if repo.archived:
                self.archived_repos += 1
                continue
            if repo.size == 0:
                continue
            if repo.fork:
                self.forked_repos += 1
                continue

            repo_langs = self.safe_query_execute(repo.get_languages)
            if not repo_langs:
                continue
            for lang in repo_langs:
                if lang not in excluded_langs:
                    all_repos_langs.append(lang)
        
        return all_repos_langs
    
    def get_org_teams(self):
        try:
            return [team.name for team in self.safe_query_execute(self.GH_ORG.get_teams)]
        except GithubException as e:
            print(e)
            return []

    def get_org_members(self):
        try:
            return [member.name for member in self.safe_query_execute(self.GH_ORG.get_members)]
        except GithubException as e:
            print(e)
            return []

    def get_org_admins(self):
        return [member.login for member in self.safe_query_execute(self.GH_ORG.get_members) if \
            member.get_organization_membership(self.ORG_NAME).role == 'admin']
    
    def get_repos_infos(self):
        org_repos_infos = []

        for repo in self.all_org_repos:
            if repo.archived or repo.size == 0 or repo.fork:
                continue
            
            repo_info = {}
            repo_info["Name"] = repo.name
            repo_info["Is_Private"] = repo.private
            repo_info["Readme_Exist"] = self.get_repo_readme_exist(repo)
            repo_info["Topics"] = [topic for topic in self.safe_query_execute(repo.get_topics)]
            repo_info["Endpoint"] = repo.homepage
            repo_info["Last_Update"] = self.get_repo_last_update(repo)
            repo_info["Master_Protect"] = self.get_repo_master_protection(repo)
            repo_info["Teams"] = [repo.name for repo in self.safe_query_execute(repo.get_teams)]
            repo_info["Alerts_On"] = self.safe_query_execute(repo.get_vulnerability_alert)
            repo_info["Vulnerabilities"] = "False"
            if repo_info["Alerts_On"]:
                repo_info["Vulnerabilities"] = self.get_repo_has_vuln(repo)
            
            org_repos_infos.append(repo_info)
       
        return org_repos_infos

    def get_repo_readme_exist(self,repo):
        repo_readme = self.safe_query_execute(repo.get_readme)
        if not repo_readme or repo_readme.decoded_content.decode() == repo.name or repo_readme.size == 0:
            return False
        
        return True

    def get_repo_master_protection(self, repo):    
        branch_master = self.safe_query_execute(repo.get_branch, branch="master")
        if not branch_master:
            return
        if branch_master.protected:
            master_protect = branch_master.get_protection().raw_data
            if 'required_pull_request_reviews' in str(master_protect):
                return master_protect['required_pull_request_reviews']['required_approving_review_count']
        
        return branch_master.protected

    def get_repo_last_update(self,repo):
        current_date = datetime.today()
        commits = self.safe_query_execute(repo.get_commits)
        last_update = repo.updated_at
        
        if commits.totalCount:
            last_commit_date=commits[0].commit.committer.date
            if last_commit_date > last_update:
                last_update = last_commit_date

        return (current_date - last_update).days

    def get_repo_has_vuln(self, repo):    
        url = 'https://api.github.com/graphql'
        query =  '{repository(name: "%s", owner: "%s") {vulnerabilityAlerts(first: 100) \
        {nodes {createdAt dismissedAt securityVulnerability {package {name}advisory {description}}}}}}' % (repo.name, self.ORG_NAME)
        data = { 'query' : query }
        headers = {'Authorization': 'token %s' % self.GH_TOKEN}

        try:
            return len([vuln['securityVulnerability'] for vuln in post(url=url, json=data, headers=headers).json()['data']['repository']['vulnerabilityAlerts']['nodes']])
        except Exception as e:
            print(e)
            
        return None

    def safe_query_execute(self, action, **kargs):
        try:
            return action(**kargs)
        except Exception as e:
            if type(e) == UnknownObjectException:
                return False
            elif type(e) == RateLimitExceededException:
                if self.GH_RATE_LIMIT.search.remaining == 0:
                    search_rate_limit = self.GH_RATE_LIMIT.search
                    reset_timestamp = timegm(search_rate_limit.reset.timetuple())
                    sleep_time = reset_timestamp - timegm(gmtime()) + 10
                    if sleep_time < 0:
                        sleep_time = 60

                    sleep(sleep_time)
                    return action(**kargs)
            else:
                return False

    def report_exporter(self,report):
        with open(f'github_full_report_{self.ORG_NAME}.json', 'w') as full_report:
            full_report.write(dumps(report,ensure_ascii=False, indent=4, sort_keys=False))
        full_report.close()

if __name__ == '__main__':
    full_report = GithubOverview()
