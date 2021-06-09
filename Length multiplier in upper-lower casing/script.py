import unicodedata
import sys
from tabulate import tabulate

CASING = "Lower" # Upper Lower

# MULTIPLIER TABLE
f = open(f'multiplierFactorTable{CASING}.txt', 'a')
data = []
for i in range (sys.maxunicode + 1):
  uni = chr(i)
  char8 = uni.encode('utf8', 'ignore').decode('utf8', 'ignore')
  if CASING == "Upper":
    char8casing = char8.upper()
  else:
    char8casing = char8.lower()
  length = len(char8casing) - len(char8)
  if length != 0:
    data.append(length)
for i in range (25):
  f.write(f"Multiplier x{i+1}: " + str(data.count(i)) + "\n")
f.close()



# MULTIPLIER FOR EACH CHARACTER
headers=["Unicode Point", "Character in UTF-8 + length", "Character normalized + legth"]
data = []
f = open(f'multiplier{CASING}.txt', 'a', encoding='utf8')
for i in range (sys.maxunicode + 1):
  uni = chr(i)
  char8 = uni.encode('utf8', 'ignore').decode('utf8', 'ignore')
  if CASING == "Upper":
    char8casing = char8.upper()
  else:
    char8casing = char8.lower()  
  if len(char8) != len(char8casing):
    if i < 65535:
      str1 = "U+" + str(hex(i))[2:].rjust(4,'0')
    else:
      str1 = "U+" + str(hex(i))[2:].rjust(8,'0')
    str2 = "\u200e" + char8 + "\u200e ---> " + str(len(char8))
    str3 = "\u200e" + char8casing + "\u200e ---> " + str(len(char8casing))
    data.append([str1, str2, str3])
f.write(tabulate(data, headers=["Unicode Point", "Character in UTF-8 + length", "Character normalized + legth"]))
f.close()
