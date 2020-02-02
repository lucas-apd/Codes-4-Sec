# by github.com/Lucas-L-Alcantara
#pre req: jq cli

from os import popen


def get_public_repos(org):

    try:
        report = []
        repos = popen('curl "https://api.github.com/users/{}/repos?per_page=200" | jq -r ".[] | .name"'.format(org)).read()
        for repo in repos.splitlines():
            report.append(repo)
    except:
        return None

    return report

if __name__ == '__main__':
    org=""
    print('\n'.join(get_public_repos(org)))