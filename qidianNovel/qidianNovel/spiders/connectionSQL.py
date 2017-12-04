import redis
from pymongo import MongoClient
def getredis():
    red = redis.Redis(host='127.0.0.1', port=6379)
    return red
def getMongodb(sqlName,collectionname):
    client = MongoClient('localhost', 27017)
    # 连接所需数据库,novel为数据库名
    db = client.get_database(sqlName)
    # 连接所用集合，也就是我们通常所说的表，rootName为表名
    bcollection = db.get_collection(collectionname)
    return bcollection