# by github.com/Lucas-L-Alcantara
#pre req:
# jq cli = sudo apt install jq
#python + argparse

from os import popen
from argparse import ArgumentParser

def get_public_repos(org):

    try:
        report = []
        repos = popen('curl "https://api.github.com/users/{}/repos?per_page=1000" | jq -r ".[] | .name"'.format(org)).read()
        for repo in repos.splitlines():
            report.append(repo)
    except:
        return None

    return report

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-o',
        '--org',
        help='Example: script.py -o <"organization_name">',
        required=True
    )
    
    args = parser.parse_args()
    print('\n'.join(get_public_repos(args.org)))

