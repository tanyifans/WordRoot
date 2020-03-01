# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 20:06:57 2018

@author: 小懒虫
"""


from datetime import *
from flask_mongoengine import MongoEngine
db = MongoEngine()
class Count(db.Document):
    meta = {
        'collection': 'usercount',
        
    }

    user = db.StringField()
    word = db.StringField()
    create_at = db.DateTimeField(default=date.today())
    
class Result(db.Document):
    meta = {
        'collection': 'result',
        
    }

    
    hint = db.StringField()
    origin = db.StringField()
    root = db.StringField()
    word = db.StringField()
   
class Roots(db.Document):
    meta = {
        'collection': 'roots',
        
    }
    
    root = db.StringField()

class User(db.Document):
    meta = {
        'collection': 'user',
        
    }
    
    user = db.StringField()
    password = db.StringField()
    times=db.IntField()
    
class Task(db.Document):
    meta = {
        'collection': 'task',
        
    }
    
    user = db.StringField()
    index = db.StringField()
    create_at = db.DateTimeField(default=date.today())
    