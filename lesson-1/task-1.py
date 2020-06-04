import requests
import json

rsp = requests.get('https://api.github.com/users/alexbabkin/repos')

with open('task-1-repositories.json', 'w') as f:
    json.dump(rsp.json(), f, indent=4)
