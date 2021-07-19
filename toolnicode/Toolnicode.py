import requests
import argparse
import secrets
import string
import re
import time
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = 'http://localhost:5000/'
NAME = 'content'
PATH_CHROME = "Browser_Selenium/chromedriver.exe"
TOKEN_LENGTH = 8

MULTIPLICATION_SIGN = '\u00d7'
REPLACEMENT_CHARACTER= '\ufffd'
S_POINTED = "\u1e69"
FILEGATURE = "\ufb01"
A_UPPER = "\u0041"
A_LOWER = "\u0061"
GREEK_QUESTION_MARK = "\u037e"
SEMICOLON = "\u003b"
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
    "SEMICOLON" : '\u003b',
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
    f'{NAME}' : payload
  }
  return token, parameters

def injection(char):
  token, parameters = createPayload(char)
  try:
    x = requests.post(URL, data = parameters)
  except Exception as e:
    print(e)
    exit()
  char = re.search(token + ".*" + token, x.text, re.IGNORECASE)
  if char:
    char = char.group()[TOKEN_LENGTH:-TOKEN_LENGTH]
    #print(hex(ord(char)))
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

def normalizationCheck (ascii):
#Normalization
  if ascii == 1:
    char = injection(GREEK_NUMERAL_SIGN)
    if char == MODIFIER_LETTER_PRIME:
      pass
    elif char == GREEK_NUMERAL_SIGN: 
      greenPrint("There is NO normalization")
      return
    else:
      normalizationCheck(2)
      #yellowPrint("something goes wrong")
      return
  if ascii == 2:
    char = injection(GREEK_QUESTION_MARK)
    if char == SEMICOLON:
      pass
    elif char == GREEK_QUESTION_MARK: 
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

def charsetTranscodingCheck():
  char = injection(GREEK_NUMERAL_SIGN)
  if char == GREEK_NUMERAL_SIGN: 
    greenPrint("UTF-8 encoding supported")
    return
  elif char == '' or '?' in char or REPLACEMENT_CHARACTER in char:
    redPrint("UTF-8 encoding NOT supported")
  else:
    yellowPrint("Something goes wrong!")
    return
  char = injection(MULTIPLICATION_SIGN)
  if char == MULTIPLICATION_SIGN: 
    greenPrint("Latin-1 encoding supported")
  else:
    redPrint("Latin-1 encoding NOT supported")
    greenPrint("ASCII encoding supported")
    return
  
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
    print("Do you want to check if payload injection actually open a popup screen in the page (avoid false positive) Y/n?")
    choose = input()
    if choose.lower() == "y":
      options = webdriver.ChromeOptions()
      options.add_argument('log-level=3')
      options.add_argument('--headless')
      driver = webdriver.Chrome(PATH_CHROME, chrome_options=options)
      driver.implicitly_wait(10)
      driver.get(URL)
      try:
        driver.switch_to.alert
        redPrint("a popup in the website is found")
      except:
        greenPrint("No popup opened")
      driver.quit()
    else:
      return

  
def main():
  #for colored terminal
  init(convert=True)
  '''
  parser = argparse.ArgumentParser()
  required = parser.add_argument_group('required arguments')
  required.add_argument("-u", "--url", help = "url to scan", required=True)
  required.add_argument("-n", "--name", help = "name html attribute of input field to test", required=True)
  args = parser.parse_args()
  if args.url:
    global URL
    URL = args.url
  if args.name:
    global NAME
    NAME = args.name
    '''
  while(True):
    print("Choose which analisys perform:\n[1] Normalization\n[2] Casing\n[3] Escaping\n[4] Charset transcoding (valid only if there are no normalization)\n[0] Quit\n")
    choose = input()
    if choose == "1":
      print("You want perform an analysis or an injection?\n[1] Scan for unicode normalization\n[2] Try xss injection\n")
      sub_choose = input()
      if sub_choose == "1":
        normalizationCheck(1)
      elif sub_choose == "2":
        print("Choose payloads:\n[1] load 10 payloads\n[2] load 500 payloads\n[3] load 6000+ payloads\n")
        sub_choose = input()
        if sub_choose == "1" or sub_choose == "2" or sub_choose == "3":
          injectNormalizationPayload(sub_choose)
        else:
          print("invalid input")
      else:
        print("invalid input") 
    elif choose == "2":
      casingCheck()
    elif choose == "3":
      escapingCheck()
    elif choose == "4":
      charsetTranscodingCheck()
    elif choose == "5":
      pass
    elif choose == "0":
      return
    else:
      print("invalid input")
  

if __name__ == "__main__":
    main()
