from pymongo import MongoClient
from pprint import pprint

client = MongoClient('192.168.19.48', 8080)
db = client['news']
mongo_base = client.instausers
collection = mongo_base['instagram']

users = collection.find({"$and": [{"username": 'tecom_group'},
                                  {"target_type": 'followed_by'}]})
pprint(list(users))

users = collection.find({"$and": [{"username": 'nntu.alekseeva'},
                                  {"target_type": 'follow'}]})
pprint(list(users))
