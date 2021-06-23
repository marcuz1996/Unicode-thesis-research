from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime
import yaml
import unicodedata
import os

app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/')
def index():
  return render_template('/index.html')

#true valid, false dangerous
def sqlChecker(string):
  for i in range (len(string)-1):
    if string[i] == '\'' or string[i] == '#' or string[i] == '"' or (string[i] == '-' and string[i+1] == '-') or string[i] == ';':
      return False
  return True


#################### SQL INJECTION ##############################
#f＇ or 1=1；﹣﹣ 
@app.route('/testInjection', methods=['GET', 'POST'])
def testInjection():
  if request.method == 'POST':
    userDetails = request.form
    if not(sqlChecker(userDetails['name'])):
      return 'invalid input: your input cannot contain " or \' or -- or ;'
    else:
      name = unicodedata.normalize('NFKC', userDetails['name']).encode('utf-8', 'ignore').decode('utf8')
      cur = mysql.connection.cursor()
      resultValue = cur.execute('SELECT * FROM users WHERE name = \'' + name + '\';')
      cur.close()
      if resultValue > 0:
        return render_template('/privatePage.html')
      else:
        return 'Your name does not appear in the database!'
  else:
    return render_template('/testInjection.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    # Fetch form data
    userDetails = request.form
    name = userDetails['name']
    email = userDetails['email']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO users(name, email) VALUES(\'' + name + '\',\'' + email + '\');')
    #cur.execute('INSERT INTO users(name, email) VALUES(\'' + name + '\', SELECT task FROM tasks WHERE id = 5);')
    #asd ' , 'a@a') UNION SELECT content FROM tasks WHERE id = 5;--
    #asd ' , 'SELECT * FROM tasks');--
    mysql.connection.commit()
    cur.close()
    return redirect('/users')
  return render_template('/register.html')

@app.route('/users')
def users():
  cur = mysql.connection.cursor()
  resultValue = cur.execute("SELECT * FROM users")
  if resultValue > 0:
    userDetails = cur.fetchall()
    cur.close()
    return render_template('users.html',userDetails=userDetails)
  cur.close()

@app.route('/deleteuser/<int:id>')
def deleteUser(id):
  try:
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM users WHERE id = \'' + str(id) + '\';')
    mysql.connection.commit()
    cur.close()
    return redirect('/users')
  except Exception as e:
    print (e)
    return 'There was a problem deleting that task'

  
#################### XSS ############################
#＜script＞ alert(1) ＜/script＞
@app.route('/tasks', methods = ['POST', 'GET'])
def tasks():
  if request.method == 'POST':
    if (validationRequest(request.form['content'])):
      task_normalized = unicodedata.normalize('NFKC', request.form['content']).encode('utf-8', 'ignore').decode('utf8')
    else:
      return "Your task contain dangerous content!"
    try:
      cur = mysql.connection.cursor()
      cur.execute('INSERT INTO tasks(content, date) VALUES( \'' + task_normalized + '\',\'' + str(datetime.now()) + '\');')
      mysql.connection.commit()
      cur.close()
      return redirect('/tasks')
    except Exception as e:
      print (e)
      return "There was an issue adding your task"
  else:
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM tasks")
    if resultValue > 0:
      tasks = cur.fetchall()
      cur.close()
      return render_template("tasks.html", tasks=tasks)
    else:
      cur.close()
      return render_template("tasks.html", tasks=[])

@app.route('/deletetask/<int:id>')
def deleteTask(id):
  try:
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM tasks WHERE id = \'' + str(id) + '\';')
    mysql.connection.commit()
    cur.close()
    return redirect('/tasks')
  except Exception as e:
    print (e)
    return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    new_content = request.form['content']
    try:
      cur.execute('UPDATE tasks SET content = \'' + new_content + '\' WHERE id = \'' + str(id) + '\';')
      mysql.connection.commit()
      cur.close()
      return redirect('/tasks')
    except:
      return 'There was an issue updating your task'
  else:
    cur.execute('SELECT * FROM tasks WHERE id = \'' + str(id) + '\';')
    task = cur.fetchone()
    cur.close()
    return render_template('update.html', task=task)

def isAtoZ(char):
  if ((char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z')):
    return True
  else:
    return False

def validationRequest(task):
  for i in range (len(task)-2):
    if task[i] == '<':
      if isAtoZ(task[i+1]) or task[i+1] == '!' or task[i+1] == '/' or task[i+1] == '?':
        return False
    if task[i] == '&' and task[i+1] == '#':
      return False
  return True

################# Directory Traversal ###################
#﹒﹒／﹒﹒／etc／passwd.txt
@app.route('/privatetask', methods=['GET', 'POST'])
def privateTask():
  if request.method == 'POST':
    userDetails = request.form
    if urlChecker(userDetails['task']):
      privateTask = unicodedata.normalize('NFKC', userDetails['task']).encode('utf-8', 'ignore').decode('utf8')
      path = './static/tasks/' + privateTask
      f = open(path, mode='r')
      task = f.readlines()[0]
      f.close()
      return render_template('/privateTasks.html', task = task)
    else:
      return 'invalid input: your input cannot contain .. or /'
  else:
    return render_template('/privateTasks.html')

#true valid, false dangerous
def urlChecker(path):
  for i in range (len(path)-1):
    if path[i] == '/' or (path[i] == '.' and path[i+1] == '.'): 
      return False
  return True

################ Length Comparison #####################
#check on python
#insert string that ecoded in utf-8 are longer than 5 but that decoded are shorter than 5 (桜の)
@app.route('/registerModerator', methods=['GET', 'POST'])
def registerModerator():
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    moderatorName = request.form['name']
    if len(moderatorName.encode('utf-8', 'ignore')) > len('admin'): 
      try:
        cur.execute('INSERT INTO adminUsers(name) VALUES (\'' + moderatorName + '\');')
        mysql.connection.commit()
        cur.close()
        return redirect('/registerModerator')
      except Exception as e:
        print(e)
        return 'There was an issue updating moderators'
    else:
      return 'you must insert a name longer than \'admin\''
  else:
    resultValue = cur.execute('SELECT * FROM adminUsers')
    if resultValue > 0:
      moderators = cur.fetchall()
      return render_template('/registerModerator.html', moderators = moderators)
    return render_template('/registerModerator.html', moderators = [])


#check on mysql
#insert string shorter than 5 that after storing into database results in a string longer than 5 (桜の)
@app.route('/registerModeratorMysql', methods=['GET', 'POST'])
def registerModeratorMysql():
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    moderatorName = request.form['name']
    if len(moderatorName) < len('admin'): 
      try:
        cur.execute('INSERT INTO adminUsers2(name) VALUES (\'' + moderatorName + '\');')
        mysql.connection.commit()
        cur.close()
        return redirect('/registerModeratorMysql')
      except Exception as e:
        print(e)
        return 'There was an issue updating moderators'
    else:
      return 'you must insert a name shorter than \'admin\''
  else:
    moderators = []
    admins = []
    resultValue = cur.execute('select * from adminUsers2 where LENGTH(name) < 5')
    if resultValue > 0:
      moderators = cur.fetchall()
    resultValue = cur.execute('select * from adminUsers2 where LENGTH(name) >= 5')
    if resultValue > 0:
      admins = cur.fetchall()
  return render_template('/registerModeratorMysql.html', moderators = moderators, admins=admins)

################ Length Comparison + Lower() tranformation #####################
#check on python
#to bypass use: admİn
@app.route('/registerModeratorLower', methods=['GET', 'POST'])
def registerModeratorLower():
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    moderatorName = request.form['name']
    if len(moderatorName) < len('admin'): 
      try:
        cur.execute('INSERT INTO adminusers3(name) VALUES (\'' + moderatorName.lower() + '\');')
        mysql.connection.commit()
        cur.close()
        return redirect('/registerModeratorLower')
      except Exception as e:
        print(e)
        return 'There was an issue updating moderators'
    else:
      return 'you must insert a name shorter than \'admin\''
  else:
    resultValue = cur.execute('SELECT * FROM adminusers3')
    if resultValue > 0:
      moderators = cur.fetchall()
      return render_template('/registerModeratorLower.html', moderators = moderators)
    return render_template('/registerModeratorLower.html', moderators = [])

# check on mysql
# the lower function on python works different from the one of MySQL
# when you use lower in MySQL our string become == admin unlike python transformation
# to bypass use: admİn
@app.route('/registerModeratorLowerMysql', methods=['GET', 'POST'])
def registerModeratorLowerMysql():
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    moderatorName = request.form['name']
    if moderatorName.lower() != 'admin': 
      try:
        cur.execute('INSERT INTO adminusers4(name) VALUES (\'' + moderatorName + '\');')
        mysql.connection.commit()
        cur.close()
        return redirect('/registerModeratorLowerMysql')
      except Exception as e:
        print(e)
        return 'There was an issue updating moderators'
    else:
      return 'you must insert a name shorter than \'admin\''
  else:
    moderators = []
    admins = []
    resultValue = cur.execute('SELECT id, LOWER(name) FROM adminusers4')
    if resultValue > 0:
      all = cur.fetchall()
      for mod in all:
        if mod[1] == 'admin':
          admins.append(mod)
        else:
          moderators.append(mod)
    return render_template('/registerModeratorLowerMysql.html', moderators = moderators, admins=admins)

################ Length Comparison + NFC Normalization #####################
@app.route('/registerModeratorNormalization', methods=['GET', 'POST'])
def registerModeratorNormalization():
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    moderatorName = request.form['name']
    if len(moderatorName) < len('admin'): 
      try:
        cur.execute('INSERT INTO adminusers5(name) VALUES (\'' + unicodedata.normalize('NFC', moderatorName) + '\');')
        mysql.connection.commit()
        cur.close()
        return redirect('/registerModeratorNormalization')
      except Exception as e:
        print(e)
        return 'There was an issue updating moderators'
    else:
      return 'you must insert a name shorter than \'admin\''
  else:
    resultValue = cur.execute('SELECT * FROM adminusers5')
    if resultValue > 0:
      moderators = cur.fetchall()
      return render_template('/registerModeratorNormalization.html', moderators = moderators)
    return render_template('/registerModeratorNormalization.html', moderators = [])

############### TRANSCODING ####################
#logging in as AऄDMIN you bypass the check
@app.route('/transcoding', methods=['GET', 'POST'])
def transcoding():
  if request.method == 'POST':
    #Firewall check in UTF-8
    name = request.form['name'].lower()
    if name == 'admin':
      return 'You can\'t log as Administrator!!!'
    #server check in ASCII
    name = name.encode('ascii', 'ignore').decode('ascii', 'ignore')
    if name != 'admin':
      return 'Hello ' + name + '!\n Welcome back!'
    else:
      return render_template('/privatePage.html')
  else:
    return render_template('/transcoding.html')


############### RTL OVERRIDE ####################
@app.route('/rtloverride', methods=['GET', 'POST'])
def rtloverride():
  if request.method == 'POST':
    file = request.files['file']
    print(file.filename.encode('utf-8').decode('utf-8'))
    if(file.filename[-3:] == 'exe'):
      print("ok")
    if (file.filename[-3:] == 'txt'):
      print("ko")
    print(file.filename[-3:])
    f = open(f'zalgo.txt', 'a', encoding='utf8')
    f.write(file.filename)
    f.close
    file.save(os.path.join('static/uploads', file.filename))
    return render_template('/rtloverride.html')
  else:
    return render_template('/rtloverride.html')


############### TEST PAGE ####################
@app.route('/testingPage', methods=['GET', 'POST'])
def testingPage():
  cur = mysql.connection.cursor()
  if request.method == 'POST':
    hexVal = request.form['name']
    link = request.form['link']
    try:
      cur.execute(("INSERT INTO bytestest(varbin, varblob) VALUES (X'"+ hexVal +"', X'"+ hexVal +"');"))
      mysql.connection.commit()
      cur.close()
      return redirect('/testingPage')
    except Exception as e:
      print(e)
      return 'There was an issue updating moderators'
  else:
    bytez = []
    #link = "\" onerror=\"alert(1)\""
    #link = "./static/image/cat.jpg"
    link = "\xc2"
    #resultValue = cur.execute('select * from bytestest')
    resultValue = cur.execute("SELECT CONVERT(varbin USING utf8), CONVERT(varblob USING utf8) FROM bytestest;")
    if resultValue > 0:
      bytez = cur.fetchall()
  return render_template('/testingPage.html', bytez = bytez, link = link)

if __name__ == '__main__':
  app.run(debug=True)


''' admin DB creation

create table adminusers(
    -> id INT NOT NULL AUTO_INCREMENT,
    -> name VARCHAR(200) NOT NULL,
    -> PRIMARY KEY (ID));

'''