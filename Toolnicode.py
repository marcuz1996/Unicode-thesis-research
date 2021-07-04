import requests
import secrets

URL = 'http://localhost:5000/tasks'
KELVIN = "\u212a"
KNORMALIZED = "\u004b"
SPOINTED = "\u1e69"
FILEGATURE = "\ufb01"

def createPayload (char):
  token = secrets.token_hex(8)
  payload = token + char
  parameters = {
    'content' : payload
  }
  return token, parameters

def check (string1, string2):
  if string1 == string2:
    return True
  else:
    return False


def main():
  #Normalization
  token, parameters = createPayload(KELVIN)
  x = requests.post(URL, data = parameters)
  txt = x.text.split(token)[1].split("<")[0]
  if check(txt, KNORMALIZED):
    print("There is normalization, let's analyze the normalization in detail...")
  elif check(txt, KELVIN):
    print("There is NO normalization")
    return
  else:
    print("something goes wrong")
    return
  
  #Form
  token, parameters = createPayload(SPOINTED)
  x = requests.post(URL, data = parameters)
  txt = x.text.split(token)[1].split("<")[0]
  if(len(txt) == 3):
    print("The form is DECOMPOSED...")
    form = 1
  else:
    print("The form is COMPOSED...")
    form = 2

  #Equivalence
  token, parameters = createPayload(FILEGATURE)
  x = requests.post(URL, data = parameters)
  txt = x.text.split(token)[1].split("<")[0]
  if(len(txt) == 2):
    print("We have COMPATIBILITY equivalence...")
    if form == 1:
      print("NFKD")
    else:
      print("NFKC") 
  else:
    print("We have CANONICAL equivalence...")
    if form == 1:
      print("NFD")
    else:
      print("NFC")



if __name__ == "__main__":
    main()
