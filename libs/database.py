import datetime
import argparse
import pymysql
import redis
import json


mysqlconnection = None
redisConnection = None


def initConnections(configs):
    initMySQLConnection(configs)
    initRedisConnection(configs)
    

def initMySQLConnection(configs):
    global mysqlconnection
    
    mysqlconnection = pymysql.connect(  host = configs._db_host, 
                                   port = configs._db_port, 
                                   user = configs._db_user, 
                                   passwd = configs._db_passwd, 
                                   db = configs._db_name, 
                                   charset = configs._db_charset,
                                   autocommit = True)
    return mysqlconnection


def _checkMySQLConnectionInitialized(func):
    global mysqlconnection
    
    def wrapper(*args, **kwargs):   
        if mysqlconnection == None:
            raise Exception("Use `initMySQLConnection` or `initConnections` to init the database connection first.")
        else:
            return func(*args)
         
    return wrapper
        


def _toDict(keys, vals):
    if not isinstance(keys, (list, tuple)) or \
        not isinstance(vals, (list, tuple)):
        raise Exception("toDict expect two list as parameter")
    if len(keys) > len(vals):
        raise Exception("unequal number of keys and values")
    
    d = {}
    for i in range(len(keys)):
        if isinstance(vals[i], datetime.datetime):
            d[keys[i]] = vals[i].strftime('%Y-%m-%d %H:%M:%S')
        else:
            d[keys[i]] = vals[i]
    
    return d


def _toRespondent(args): # args is a tuple
    keys = ["id", "age", "gender", "education", "country_of_birth", "country_of_residence", 
            "ethnicity", "is_native", "language_spoken", "start_time", "end_time", "email"]
    
    return _toDict(keys, args)

def _toQuestion(args): # args is a tuple
    keys = ["id", "word"]
    
    return _toDict(keys, args)


def _toAnswer(args): # args is a tuple
    keys = ["id", "association1", "association2", "association3", "time_spend", "question_id", "respondent_id"]
    
    return _toDict(keys, args)


@_checkMySQLConnectionInitialized
def getRespondents():
    global mysqlconnection
    
    cursor = mysqlconnection.cursor()
    _ = cursor.execute("select * from `respondent`;")
    rows = cursor.fetchall()
    data = {v["id"]:v for v in map(_toRespondent, rows)}
    cursor.close()
    return data


@_checkMySQLConnectionInitialized
def getAnswers():
    global mysqlconnection
    
    cursor = mysqlconnection.cursor()
    _ = cursor.execute("select * from `answer`;")
    rows = cursor.fetchall()
    data = {v["id"]:v for v in map(_toAnswer, rows)}
    cursor.close()
    return data


@_checkMySQLConnectionInitialized
def getQuestions():
    global mysqlconnection
    
    cursor = mysqlconnection.cursor()
    _ = cursor.execute("select * from `question`;")
    rows = cursor.fetchall()
    data = {v["id"]:v for v in map(_toQuestion, rows)}
    cursor.close()    
    return data


@_checkMySQLConnectionInitialized
def refreshMySQLQuestions(questions):
    global mysqlconnection
    
    cursor = mysqlconnection.cursor()
    
    insertValues = ", ".join(["(\"{}\")".format(q) for q in questions])
    
    _ = cursor.execute("UPDATE `question` SET `enable`=0;")
    _ = cursor.execute(f"INSERT INTO `question` (`word`) VALUES {insertValues} ON DUPLICATE KEY UPDATE `enable`=1;")
    
    mysqlconnection.commit()
    
    cursor.close()

    

##################################################################
#
# Then the redis part
#
##################################################################


def initRedisConnection(configs):
    global redisConnection
    
    redisConnection = redis.Redis(host = configs._redis_host,
                                  port = configs._redis_port)
    return redisConnection



def _checkRedisConnectionInitialized(func):
    global redisConnection
    
    def wrapper(*args, **kwargs):   
        if redisConnection == None:
            raise Exception("Use `initRedisConnection` or `initConnections` to init the redis connection first.")
        else:
            return func()
            
    return wrapper
        
    

@_checkRedisConnectionInitialized
@_checkMySQLConnectionInitialized
def refreshRedis():
    cursor = mysqlconnection.cursor()
    
    _ = cursor.execute("select * from `question` where `enable`=1;")
    
    rows = cursor.fetchall()
    questions = list(map(_toQuestion, rows))
    
    cursor.close()
    
    redisConnection.delete('questionList')
    redisConnection.set('questionIndex', 0)

    with redisConnection.pipeline(transaction=False) as p:
        for q in [json.dumps(e) for e in questions]:
            p.lpush('questionList', q)
        p.execute()
    
    
