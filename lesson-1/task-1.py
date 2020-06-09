import requests
import json

rsp = requests.get('https://api.github.com/users/alexbabkin/repos')
for repo in rsp.json():
    print(repo['name'], repo['html_url'])

with open('task-1-repositories.json', 'w') as f:
    json.dump(rsp.json(), f, indent=4)
