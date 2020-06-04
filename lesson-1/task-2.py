import requests
import json

# Authorization with API KEY
API_KEY = 'Q2YNlkX4gpY8drtYO6mDinKEfkdP1KOaQqf4VJ8D'
rsp = requests.get(
    url='https://api.nasa.gov/planetary/apod',
    params={'api_key': f'{API_KEY}'}
)
with open('task-2-Astronomy-Picture-of-the-Day.json', 'w') as f:
    json.dump(rsp.json(), f, indent=4)
