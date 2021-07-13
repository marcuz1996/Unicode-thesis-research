from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import yaml
import unicodedata

#&#3cscript&#3e alert(1) &#3c&#2fscript&#3e
app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']


mysql = MySQL(app)

#＜script＞ alert(1) ＜/script＞
@app.route('/', methods = ['POST', 'GET'])
def index():
  if request.method == 'POST':
    if (validationRequest(request.form['content'])):
      task_normalized = unicodedata.normalize('NFKC', request.form['content']).encode('utf-8', 'ignore').decode('utf8')
    else:
      return "Your input contain dangerous content!"
    try:
      cur = mysql.connection.cursor()
      cur.execute(f'INSERT INTO test(content) VALUES(\'{task_normalized}\');')
      mysql.connection.commit()
      cur.close()
      return redirect('/')
    except Exception as e:
      print (e)
      return "There was an issue adding your task"
  else:
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM test")
    if resultValue > 0:
      content = cur.fetchall()
      cur.close()
      return render_template("index.html", content=content)
    else:
      cur.close()
      return render_template("index.html", content=[])


@app.route('/delete/<int:id>')
def deleteTask(id):
  try:
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM test WHERE id = \'' + str(id) + '\';')
    mysql.connection.commit()
    cur.close()
    return redirect('/')
  except Exception as e:
    print (e)
    return 'There was a problem deleting that task'


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


if __name__ == '__main__':
  app.run(debug=True)

#create table test(id INT NOT NULL AUTO_INCREMENT,content VARCHAR(200) NOT NULL,PRIMARY KEY (ID));