import requests
import secrets
import re

URL = 'http://localhost:5000/tasks'
TOKEN_LENGTH_INDEX = 4
S_POINTED = "\u1e69"
FILEGATURE = "\ufb01"
A_UPPER = "\u0041"
A_LOWER = "\u0061"
GREEK_NUMERAL_SIGN = '\u0374'
MODIFIER_LETTER_PRIME = '\u02b9' #char obtained from GREEK_NUMERAL_SIGN normalization of each type


def createPayload (char):
  token = secrets.token_hex(TOKEN_LENGTH_INDEX)
  payload = token + char + token
  parameters = {
    'content' : payload
  }
  return token, parameters


def normalizationCheck ():
#Normalization
  token, parameters = createPayload(GREEK_NUMERAL_SIGN)
  x = requests.post(URL, data = parameters)
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE).group()[TOKEN_LENGTH_INDEX*2:-TOKEN_LENGTH_INDEX*2]
  if char == MODIFIER_LETTER_PRIME:
    print("There is normalization, let's analyze the normalization in detail...")
  elif char == GREEK_NUMERAL_SIGN: 
    print("There is NO normalization")
    return
  else:
    print("something goes wrong")
    return
  #Form
  token, parameters = createPayload(S_POINTED)
  x = requests.post(URL, data = parameters)
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE).group()[TOKEN_LENGTH_INDEX*2:-TOKEN_LENGTH_INDEX*2]
  if(len(char) == 3):
    print("The form is DECOMPOSED...")
    form = 1
  else:
    print("The form is COMPOSED...")
    form = 2
  #Equivalence
  token, parameters = createPayload(FILEGATURE)
  x = requests.post(URL, data = parameters)
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE).group()[TOKEN_LENGTH_INDEX*2:-TOKEN_LENGTH_INDEX*2]
  print(char)
  if(len(char) == 2):
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

def casingCheck ():
  #Upper to Lower
  token, parameters = createPayload(A_UPPER)
  x = requests.post(URL, data = parameters)
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE).group()[TOKEN_LENGTH_INDEX*2:-TOKEN_LENGTH_INDEX*2]
  if char == A_LOWER:
    print("There is a lower transformation")
  elif char == A_UPPER:
    print("There is NO lower transformation")
  else:
    print("something goes wrong")
    return
  #Lower to Upper
  token, parameters = createPayload(A_LOWER)
  x = requests.post(URL, data = parameters)
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE).group()[TOKEN_LENGTH_INDEX*2:-TOKEN_LENGTH_INDEX*2]
  if char == A_UPPER:
    print("There is a upper transformation")
  elif char == A_LOWER:
    print("There is NO upper transformation")
  else:
    print("something goes wrong")
    return
  
def main():
  normalizationCheck()
  casingCheck()
  

if __name__ == "__main__":
    main()
