# Unicode Encodings Vulnerabilities

## Description

This respository contains all my work done about Unicode encodings vulnerabilities. In particular I work on python3 and mysql integration.<br/>
vulnerable-flask-sql folder conatins the vulnerable web app to reproduce my tests. in order to reproduce them correctly you must follw the setup procedure and you must satisfy the requirements.

## Requirements

1. python3

- Flask
- flask_mysqldb
- datetime
- yaml
- unicodedata
- os

2. mysql 8.0.23

## Setup

1. Create a yaml configuration file in vulnerable-flask-sql folder in this way:<br/>

```
mysql_host: "localhost"
mysql_user: "username"
mysql_password: "password"
mysql_db: "flaskapp"
```

2. import Database into mysql:<br/>
   type in your terminal this command:
   `mysql -u username -p flaskapp < flaskapp.sql`
   the flaskapp.sql file is located into vulnerable-flask-sql folder.
