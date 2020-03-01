# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 20:14:16 2019

@author: 小懒虫
"""
import pandas as pd
import random
from models import Count,Result,Roots,User,Task
from flask_mongoengine import MongoEngine
import json
from flask import Flask, session, redirect, url_for, escape, request, render_template, make_response, jsonify
import logging
import sys
import os
from datetime import *
app = Flask(__name__,static_url_path='')
app.config['MONGODB_SETTINGS'] = {
    'db'    : 'wordroot',
    'host'  : 'localhost',
    'port'  : 27017
 
}


app.config['SECRET_KEY'] = '123456'
logger = logging.getLogger(__name__)
db = MongoEngine()
db.init_app(app)

@app.route("/recharge",methods=['GET', 'POST'])
def recharge():
    username=session['username']
    user=User.objects(user=username).first()
    return (render_template("recharge.html",
                             username=user.user,
                             times=user.times   ))
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route("/introduction")
def introduction():
    username=session['username']
    user=User.objects(user=username).first()
    return (render_template("introduction.html",
                             username=user.user,
                             times=user.times   ))

@app.route("/bonus",methods=['POST'])
def bonus():
    username=session['username']
    index=request.form['index']
    today=date.today()
    user=User.objects(user=username).first()
    tasks=Task.objects(index=index,user=username,create_at=today).all()
    oncetasks=Task.objects(index=index,user=username).all()
    words=Count.objects(user=user.user,create_at=today).all()
    
    wordlist=[]
    countwords=Count.objects(user=user.user).all()
    for word in countwords:
        if word.word not in wordlist:
            wordlist.append(word.word)
    length = len(wordlist)
   
    
    
    if index=='0':
        if len(tasks)==0:
            user.update(times=user.times+5)
            Task(user=username,index=index).save()
            return jsonify({'status': '1'})
    elif index=='1':
        
        if len(words) >=10 and len(tasks)==0:
            user.update(times=user.times+5)
            Task(user=username,index=index).save()
            return jsonify({'status': '1'})
    elif index=='2':
       
        if len(words) >=20 and len(tasks)==0:
            user.update(times=user.times+15)
            Task(user=username,index=index).save()
            return jsonify({'status': '1'})
        
    elif index=='3':
        if len(words) >=50 and len(tasks)==0:
            user.update(times=user.times+30)
            Task(user=username,index=index).save()
            return jsonify({'status': '1'})
        
    elif index=='4' and len(oncetasks)==0:
        if length >= 100:
            Task(user=username,index=index).save()
            user.update(times=user.times+100)
            return jsonify({'status': '1'})
    elif index=='5'and len(oncetasks)==0:
        if length >= 500:
            Task(user=username,index=index).save()
            user.update(times=user.times+100)
            return jsonify({'status': '1'})
    
    return jsonify({'status': '0'})
    
@app.route("/daily")
def daily():
    username=session['username']
    user=User.objects(user=username).first()
    today=date.today()
    wordlearned=Count.objects(user=user.user,create_at=today).all()
    wordlist=[]
    countwords=Count.objects(user=user.user).all()
    for word in countwords:
        if word.word not in wordlist:
            wordlist.append(word.word)
    length = len(wordlist)
    quests={'0':"(daily)Sign in evertday--5 points",
            '1':"(daily)Learn 10 more words--5 points",
            '2':"(daily)Learn 20 more words--15 points",
            '3':"(daily)Learn 50 more words--30 poitns",
            "4":"(only once)Acomplish collections of 100 words -- 100 points",
            "5":"(only once)Acomplish collections of 500 words -- 500 points"
            }
    return (render_template("daily.html",
                            quests=quests,
                             username=user.user,
                             times=user.times,
                             wordlearned=len(wordlearned),
                             wordcollect=length))
@app.route("/mywordlist",methods=['GET', 'POST'])
def mywordlist():
    if 'username' in session:
        username=session['username']
        user=User.objects(user=username).first()
        wordlist=[]
        words=Count.objects(user=user.user).all()
        for word in words:
            if word.word not in wordlist:
                wordlist.append(word.word)
        wordlist.sort()
        return (render_template("mywordlist.html",
                                words=wordlist,
                                length=len(wordlist),
                                username=user.user,
                                times=user.times
                                ))


@app.route("/",methods=['GET', 'POST'])
def index():
    
    if 'username' in session:
        wordindex=request.args.get('wordindex')
        username=session['username']
        user=User.objects(user=username).first()
        if user.times < 0:
            return (render_template("recharge.html",
                                username=user.user,
                                times=user.times))
        else:
            user.update(times=user.times-1)
            questlists=pd.read_json(Result.objects().to_json())  
            wordroot= pd.read_json(Roots.objects().to_json())['root']
            rlength=len(wordroot)
            length=len(questlists['word'])
            
            if wordindex == None:
                num1=random.randint(0,length-1)
            else:
                num1=questlists[(questlists.word==wordindex)].index.tolist()[0]
            question=questlists.take([num1])
            word=question['word'][num1]
            hints=question['hint'][num1]
            #roots
            roots=question['root'][num1].strip('[').strip(']')
            roots=roots.split(',')
            root2=[]
            for root in roots:
                root=root.strip(" ")
                root2.append(root.strip().strip("'").strip('"'))
            answers="".join(root2)
            while len(root2)<=5:
                num2=random.randint(0,rlength-1)
                temword=wordroot[num2]
                if temword not in root2:
                    root2.append(temword)
            root2.sort()
            Count(word=word,user=user.user).save()
            #wordcounts
            wordcounts=len(Count.objects(word=word).all())
        
            #hints
            th=hints.split('］')
            
            com=(th[0]).split('；')
            
            t1= com[0].split('［')
            t2= com[-1].split('→')
            wordg=''
            for i in range(len(word)):
                wordg+='_ '
            component=[wordg,t1[1]]
            for c in com[1:-1]:
                component.append(c)
            for t in t2:
                component.append(t)
            
            
            hint=th[1].split('。')
            today=date.today()
            wordlearned=len(Count.objects(user=user.user,create_at=today).all())
    
            return (render_template("index.html",
                                    word=word,
                                    roots=root2,
                                    component=component,
                                    hints=hint,
                                    itemid=num1,
                                    answer=question['origin'][num1],
                                    wordcounts=wordcounts,
                                    answers = answers,
                                    username=user.user,
                                    times=user.times,
                                    wordlearned=wordlearned
                                    ))
        
    else:
        return render_template('login.html')
    
    
    
    

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logger.debug("login post method")
        username = request.form['username']
        password = request.form['password']
        users=User.objects(user=username).all()
        for user in users:
            
            if password== user.password:
                session['username']=request.form['username']
                session['password']=request.form['password']
                # return resp
                return jsonify({'status': '0', 'errmsg': '登录成功！'})
            else:
                    # return redirect(url_for('error'))
                return jsonify({'status': '-1', 'errmsg': '用户名或密码错误！'})
        return jsonify({'status': '-1', 'errmsg': '用户名或密码错误！'})
    logger.debug("login get method")
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        logger.debug("login post method")
        username = request.form['username']
        password = request.form['password']
        users=User.objects(user=username).all()
        
        if len(users) == 0:
            
            User(user=username,password=password,times=10).save()
            # return resp
            session['username']=request.form['username']
            session['password']=request.form['password']
                
            return jsonify({'status': '0', 'errmsg': '注册成功！'})
        else:
                    # return redirect(url_for('error'))
            return jsonify({'status': '-1', 'errmsg': '用户名或密码错误！'})
        return jsonify({'status': '-1', 'errmsg': '用户名或密码错误！'})
    logger.debug("login get method")
    return render_template('register.html')    


@app.route("/verify",methods=['GET']) 
def verification():    
    answer=request.args.get('answerid')
    if answer == word:
        #+1
        pass
    return None

        
    

    
    
    
    
    


if __name__ == '__main__':
    
    app.run(
      host='0.0.0.0',
      port= 80,
      debug=False
    )
