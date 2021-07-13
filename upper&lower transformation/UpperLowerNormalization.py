import sys

def lowerToUpper(char):
  low = char.lower()
  upp = low.upper()
  if upp == char or low ==char:
    return
  else:
    f.write(char + "  --> " + hex(ord(char)))
    f.write("\n|\n|\t\tLOWER\n|\n")
    f.write(low + "  --> ")
    for x in low:
      f.write("  " + str(hex(ord(x))))
    f.write("\n|\n|\t\tUPPER\n|\n")
    f.write(upp + "  --> ")
    for x in upp:
      f.write("  " + str(hex(ord(x))))
    f.write("\n\n\n")



def upperToLower(char):
  upp = char.upper()
  low = upp.lower()
  if low == char or upp == char:
    return
  else:
    f.write(char + "  --> " + hex(ord(char)))
    f.write("\n|\n|\t\tUPPER\n|\n")
    f.write(upp + "  --> ")
    for x in upp:
      f.write("  " + str(hex(ord(x))))
    f.write("\n|\n|\t\tLOWER\n|\n")
    f.write(low + "  --> ")
    for x in low:
      f.write("  " + str(hex(ord(x))))
    f.write("\n\n\n")


for i in range (sys.maxunicode + 1):
  f = open('upper&lower.txt' , 'a', newline='', encoding='utf8')
  char = chr(i)
  lowerToUpper(char)
  upperToLower(char)
f.close()
