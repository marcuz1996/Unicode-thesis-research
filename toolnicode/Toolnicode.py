import requests
import secrets
import string
import re
import time
from colorama import Fore, Style, init

URL = 'http://localhost:5000/'
TOKEN_LENGTH = 8
S_POINTED = "\u1e69"
FILEGATURE = "\ufb01"
A_UPPER = "\u0041"
A_LOWER = "\u0061"
GREEK_NUMERAL_SIGN = '\u0374'
MODIFIER_LETTER_PRIME = '\u02b9' #char obtained from GREEK_NUMERAL_SIGN normalization of each type
#Escaping
escaping_dict = {
    "EXCLAMATION_MARK" : '\u0021',
    "QUOTATION_MARK" : '\u0022',
    "NUMBER_SIGN" : '\u0023',
    "DOLLAR_SIGN" : '\u0024',
    "PERCENT_SIGN" : '\u0025',
    "AMPERSAND" : '\u0026',
    "APOSTROPHE" : '\u0027',
    "SOLIDUS" : '\u002f',
    "REVERSE_SOLIDUS" : '\u005c',
    "LESSTHAN_SIGN" : '\u003c',
    "GREATERTHAN_SIGN" : '\u003e',
    "QUESTION_MARK" : '\u003f',
    "AMP+NUMBER" : '\u0026'+'\u0023',
}

def greenPrint(text):
  current_time = time.strftime("%H:%M:%S", time.localtime())
  print(f"[{current_time}]  {Fore.GREEN}{text}{Style.RESET_ALL}")
def whitePrint(text):
  current_time = time.strftime("%H:%M:%S", time.localtime())
  print(f"[{current_time}]  {Fore.WHITE}{text}{Style.RESET_ALL}")
def yellowPrint(text):
  current_time = time.strftime("%H:%M:%S", time.localtime())
  print(f"[{current_time}]  {Fore.YELLOW}{text}{Style.RESET_ALL}")
def redPrint(text):
  current_time = time.strftime("%H:%M:%S", time.localtime())
  print(f"[{current_time}]  {Fore.RED}{text}{Style.RESET_ALL}")

def createPayload (char):
  alphabet = string.ascii_letters
  token = ''.join(secrets.choice(alphabet) for i in range(TOKEN_LENGTH))
  payload = token + char + token
  parameters = {
    'content' : payload
  }
  return token, parameters

def injection(char):
  token, parameters = createPayload(char)
  x = requests.post(URL, data = parameters)
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE)
  if char:
    char = char.group()[TOKEN_LENGTH:-TOKEN_LENGTH]
    return char
  else:
    return ''

def compatibilityParser(payload):
  payload = payload.replace("<", "\uff1c")
  payload = payload.replace(">", "\uff1e")
  payload = payload.replace("!", "\uff01")
  payload = payload.replace("\"", "\uff02")
  payload = payload.replace("#", "\uff03")
  payload = payload.replace("$", "\uff04")
  payload = payload.replace("%", "\uff05")
  payload = payload.replace("&", "\uff06")
  payload = payload.replace("'", "\uff07")
  payload = payload.replace("/", "\uff0f")
  payload = payload.replace("\\", "\uff3c")
  payload = payload.replace("?", "\uff1f")
  return payload

def normalizationCheck ():
#Normalization
  char = injection(GREEK_NUMERAL_SIGN)
  if char == MODIFIER_LETTER_PRIME:
    pass
  elif char == GREEK_NUMERAL_SIGN: 
    greenPrint("There is NO normalization")
    return
  else:
    yellowPrint("something goes wrong")
    return
  #Form
  char = injection(S_POINTED)
  if(len(char) == 3):
    form = 1    #decomposed
  else:
    form = 2    #composed
  #Equivalence
  char = injection(FILEGATURE)
  if(len(char) == 2):
    if form == 1:
      redPrint("There is NFKD normlization")
    else:
      redPrint("There is NFKC normlization") 
  else:
    if form == 1:
      redPrint("There is NFD normlization")
    else:
      redPrint("There is NFC normlization")

def casingCheck ():
  #Upper to Lower
  char = injection(A_UPPER)
  if char == A_LOWER:
    redPrint("There is a lower transformation")
  elif char == A_UPPER:
    greenPrint("There is NO lower transformation")
  else:
    yellowPrint("something goes wrong")
    return
  #Lower to Upper
  char = injection(A_LOWER)
  if char == A_UPPER:
    redPrint("There is a upper transformation")
  elif char == A_LOWER:
    greenPrint("There is NO upper transformation")
  else:
    yellowPrint("something goes wrong")
    return

def escapingCheck():
  for key in escaping_dict:
    char = injection(escaping_dict[key])
    if len(char) == 0:
      redPrint("Escaping!!! " + key + " (" + escaping_dict[key] + ")" + " has been escaped.")
    else:
      greenPrint(key + " (" + escaping_dict[key] + ")" + " has not been escaped.")

def injectNormalizationPayload(dimension):
  if dimension == "1":
    file = "xss_payload_10.txt"
  elif dimension == "2":
    file = "xss_payload_500.txt"
  elif dimension == "3":
    file = "xss_payload_6606.txt"
  with open(f"static/payload/{file}", "r") as f:
    lines = f.read().splitlines() 
    for line in lines:
      payload_normalized = compatibilityParser(line)
      whitePrint("injecting -> " + payload_normalized)
      char = injection(payload_normalized)
      if char == line:
        redPrint("Payload injection work correctly, payload was not escaped")
      else:
        yellowPrint("Payload injection fail")

  
def main():
  #for colored terminal
  init(convert=True)
  while(True):
    print("Choose which analisys perform:\n[1] Normalization\n[2] Casing\n[3] Escaping\n[0] Quit\n")
    choose = input()
    if choose == "0":
      return
    elif choose == "1":
      print("You want perform an analysis or an injection?\n[1] Scan for unicode normalization\n[2] Try xss injection\n")
      sub_choose = input()
      if sub_choose == "1":
        normalizationCheck()
      elif sub_choose == "2":
        print("Choose payloads:\n[1] load 10 payloads\n[2] load 500 payloads\n[3] load 6000+ payloads\n")
        sub_choose = input()
        if sub_choose == "1" or sub_choose == "2" or sub_choose == "3":
          injectNormalizationPayload(sub_choose)
      else:
        print("invalid input")
    elif choose == "2":
      casingCheck()
    elif choose == "3":
      escapingCheck()
    elif choose == "4":
      injectNormalizationPayload()
    else:
      print("invalid input")
  

if __name__ == "__main__":
    main()
