from flask import Flask, render_template, request, redirect, url_for, abort
import flask as werkzeug
from replit import db
from os import environ
import chat
import random
import time
import requests


def remove_items(test_list, item):
  res = [i for i in test_list if i != item]
  return res




app = Flask(__name__)
def get(question,api_key,user_id):
  try:
    body = {"action": {"type": "text", "payload": question}}
    response = requests.post(
        f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact",
        json=body,
        headers={"Authorization": api_key},
      )
    api_response = response.json()[1]["payload"]["message"]
    api_response = api_response.replace("\nWhat would you like to ask TeachMe?","")
    print(api_response,"set")
    return api_response
  except:
    return get(question,api_key,user_id)
@app.route("/post/<key>/response")
def post(key,response):
  chat.noresponse(key,response)
  return "TAKEN"
@app.route('/test')
def test():
  return render_template("test.html")
@app.before_request
def before_request():
  print(db["login"])
  
  print(request.headers.get('X-Replit-User-Name'), request.path,request.endpoint)
  if request.headers.get('X-Replit-User-Name') in [None,''] and request.endpoint not in ['static','login']:
    return redirect(url_for('login'))
  elif request.endpoint in ['login']:
    pass
  elif request.endpoint in ['static']:
    pass
  else:
    if request.headers.get('X-Replit-User-Name') in list(db):
      print(request.path,db[request.headers.get('X-Replit-User-Name')])
      if request.path == db[request.headers.get('X-Replit-User-Name')][0] and request.path != "/":
        redirect(url_for("home"))#pass#abort(500)
      if request.endpoint not in ['static']:
        a = time.gmtime()
        db[request.headers.get('X-Replit-User-Name')] = [request.path,str(a[1])+"/"+str(a[2])+"/"+str(a[0])+"   "+str(a[3])+":"+str(a[4])+":"+str(a[5])]
    else:
      if request.endpoint not in ['static']:
        a = time.gmtime()
        db[request.headers.get('X-Replit-User-Name')] = [request.path,str(a[1])+"/"+str(a[2])+"/"+str(a[0])+"   "+str(a[3])+":"+str(a[4])+":"+str(a[5])]
@app.route('/login')
def login():
  sign = request.args.get("sign")
  if sign == "True":
    db["login"] += 1
  print(request.headers.get('X-Replit-User-Name'))
  if request.headers.get('X-Replit-User-Name'):
    if int(db["login"]%2)==1:
      return render_template('login.html',login = str(db["login"]))
    db[str(request.headers.get('X-Replit-User-Name'))+"questionandanswer"] = {"answered":[],"questions":{}}
    return redirect(url_for('home'))
  #return redirect(url_for('home'))
  return render_template('login.html',login = str(db["login"]))
@app.route('/')
def home():
  return render_template('intro.html',username = request.headers.get('X-Replit-User-Name'))


@app.route('/bot')
def bot():
  return render_template('home.html',username=request.headers.get('X-Replit-User-Name'))

@app.route('/question')
def result():
  result = request.args.get("question")
  print(result,type(result))
  print(type(result))
  result = result.lower()
  a = chat.chat(result)
  print(result,a)
  if (list(a)[0] == "error"):# or (result == ''):
    return render_template('gotten.html',answer=get(result,environ["api_key"],str(request.headers.get('X-Replit-User-Name'))),username=request.headers.get('X-Replit-User-Name'),question=result)
    #return render_template('noresponse.html',username =request.headers.get('X-Replit-User-Name'),question=result)
  return render_template('gotten.html',answer=a["response"],username=request.headers.get('X-Replit-User-Name'),question=result)

@app.route('/rated')
def rated():
  question = request.args.get("question")
  answer = request.args.get("answer")
  rating = request.args.get("rating")
  response = chat.rate(rating,question,answer)
  db[str(request.headers.get('X-Replit-User-Name'))+"questionandanswer"]["questions"][question]=[answer,rating]
  if list(response)[0] == "response":
    return render_template('intro.html',username = request.headers.get('X-Replit-User-Name'))
  elif response["error"] == "badrating":
    return render_template('badrating.html',answer=answer,question=question,rating=rating,username = request.headers.get('X-Replit-User-Name'))
  return "You gave a rating of "+str(rating) +" and this error came: "+str(response)+". Please go back to the home page."
  #rate(rate,key,response):
  
@app.route("/badrating")
def badrating():
  question = request.args.get("question")
  answer = request.args.get("answer")
  newr = request.args.get("new")
  print(newr,question,answer)
  print(chat.badrate(newr,answer,question))
  db[str(request.headers.get('X-Replit-User-Name'))+"questionandanswer"]["questions"][question].append(newr)
  return render_template('intro.html', username=request.headers.get('X-Replit-User-Name'))
  
@app.route("/noresponse")
def noresponse():
  question = request.args.get("question")
  api_key = environ["api_key"]
  user_id = str(request.headers.get('X-Replit-User-Name'))
  api_response = get(question,api_key,user_id)
  print(api_response,"set")
  chat.addEmpty(question,api_response)
  db[str(request.headers.get('X-Replit-User-Name'))+"questionandanswer"]["questions"][question]=["ai"]
  return render_template('intro.html',username=request.headers.get('X-Replit-User-Name'))

@app.route("/another")
def another():
  question = request.args.get("question")
  answer = request.args.get("new")
  db[str(request.headers.get('X-Replit-User-Name'))+"questionandanswer"]["answered"].append([question,answer])
  chat.noresponse(question,answer)
  return render_template('intro.html',username=request.headers.get('X-Replit-User-Name'))

@app.route("/answer")
def answer():
  questions = chat.getEmpty()
  print(questions,len(questions))
  if len(questions) == 0:
    return redirect(url_for('alt'))
  questions = random.choice(questions)
  return render_template('answer.html',username=request.headers.get('X-Replit-User-Name'),question=questions)
  
@app.route("/alt")
def alt():
  return render_template("alt.html")

"""
@app.route('/highscore')
def get_highscore():
  return {'score': db['highscore']}


@app.route('/highscore/set', methods=['POST'])
def set_highscore():
  score = request.args.get('score', type=int)
  if score > int(db['highscore']):
    db['highscore'] = score
    return {'success': True}
  
  return {'error': 'score not greater than record score'}
"""


app.run(host='0.0.0.0', port=8080)
