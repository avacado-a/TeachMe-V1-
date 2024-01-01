from random import choice
from replit import db
keys = db["keys"]
def save_keys():
  db["keys"] = keys
  file = open("save.txt","w")
  file.write(str(keys))
  file.close()
def chat(response):
  if response in keys:
    rand_choice = choice(keys[response])
    return {"response":rand_choice}
  else:
    return {"error":"noresponse"}
def rate(rate,key,response):
  try:
    if not key in list(keys):
      keys[key] = [response]
    if int(rate)>1 or int(rate)<-1: 
      raise Exception("Range")
    elif int(rate) == -1:
      return {"error":"badrating"}
    elif int(rate) == 1:
      keys[key].append(response)
      save_keys()
      return {"response":["taken",key,response,rate]}
    elif int(rate) == 0:
      return {"response":"taken"}
    elif int(rate)%1 != 0:
      raise Exception("Decimal")
  except (Exception) as e:
    return {"error":e}
def badrate(new,response,key):
  keys[key].remove(response)
  keys[key].append(new)
  save_keys()
  return [new,response,key]
def noresponse(key,response):    
  keys[key] = [response.lower()]
  save_keys()
def getEmpty():
  back = []
  for i in list(keys):
    if keys[i] == []:
      back.append(i)
  return back
def addEmpty(key,response_api):
  keys[key] = [response_api]
  save_keys()
def giveSave():
  return keys