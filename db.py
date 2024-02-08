from pymongo import MongoClient

DATABASE_URL = 'mongodb://localhost:27017'
client = MongoClient(DATABASE_URL)

conn_for_users = MongoClient('mongodb://localhost:27017/')
db = client['local']
users_collection = db['users']