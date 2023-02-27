''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
from fastapi import FastAPI, Request                            # The main FastAPI import and Request object
from fastapi.responses import HTMLResponse, JSONResponse        # Used for returning HTML responses (JSON is default)
from fastapi.templating import Jinja2Templates                  # Used for generating HTML from templatized files
from fastapi.staticfiles import StaticFiles                     # Used for making static resources available to server
import uvicorn                                                  # Used for running the app directly through Python
import mysql.connector as mysql                                 # Used for interacting with the MySQL database
import os                                                       # Used for interacting with the system environment
from dotenv import load_dotenv                                  # Used to read the credentials

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration
load_dotenv('../credentials.env')                 # Read in the environment variables for MySQL
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']

app = FastAPI()                                   # Specify the "app" that will run the routing
views = Jinja2Templates(directory='views')        # Specify where the HTML files are located
static_files = StaticFiles(directory='public')    # Specify where the static files are located
app.mount('/public', static_files, name='public') # Mount the static files directory to /public

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define helper functions for CRUD operations

# CREATE SQL query
def db_create_user(first_name:str, last_name:str) -> int:
  '''
  1. Open a connection to the database
  2. INSERT a new user into the table
  3. Close the connection to the database
  4. Return the new user's ID (this is stored in the cursor's 'lastrowid' attribute after execution)
  '''
  
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()

  cursor.execute(f"INSERT INTO users (first_name, last_name) VALUES (\"{first_name}\", \"{last_name}\");")
  db.commit()
  db.close()

  id = cursor.lastrowid
  return id

# SELECT SQL query
def db_select_users(user_id:int=None) -> list:
  '''
  1. Open a connection to the database
  2. If the user_id is specified as an argument, perform a SELECT for just that user record
  3. If there is no user_id specified, then perform a SELECT for all users
  4. Close the connection to the database
  5. Return the retrieved record(s)
  '''

  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()

  if user_id == None: 
    cursor.execute("SELECT user_id, first_name, last_name FROM users;") # it is better to be specific than use * bc then you know what you are grabbing
    response = cursor.fetchall()
  else: 
    cursor.execute(f"SELECT user_id, first_name, last_name FROM users WHERE user_id={user_id};")
    response = cursor.fetchone()

  db.close() 

  return response

# UPDATE SQL query
def db_update_user(user_id:int, first_name:str, last_name:str) -> bool:
  '''
  1. Open a connection to the database
  2. UPDATE the user in the database
  3. Close the connection to the database
  4. Return True if a row in the database was successfully updated and False otherwise (you can
     check how many records were affected by looking at the cursor's 'rowcount' attribute)
  '''

  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.connect()
  
  values = (f'first_name="{first_name}", last_name="{last_name}"')
  cursor.execute(f'UPDATE users SET {values} WHERE user_id="{user_id}"')
  rowcount = cursor.rowcount

  db.commit()
  cursor.close()

  return rowcount > 0

# DELETE SQL query
def db_delete_user(user_id:int) -> bool:
  '''
  1. Open a connection to the database
  2. DELETE the user in the database
  3. Close the connection to the database
  4. Return True if a row in the database was successfully deleted and False otherwise (you can
     check how many records were affected by looking at the cursor's 'rowcount' attribute)
  '''
  try: 
    db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
    cursor = db.cursor()

    query = "DELETE FROM user WHERE user_id={uesr_id};".format(user_id=user_id)
    cursor.execute(query)
    db.commit()
    db.close()

    rowcount = cursor.rowcount
    return rowcount > 0

  except RuntimeError as err: 
    print("runtime error: {0}".format(err))
    return False
  

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Home route to load the main page in a templatized fashion

# GET /
@app.get('/', response_class=HTMLResponse)
def get_home(request:Request) -> HTMLResponse:
  return views.TemplateResponse('index.html', {'request':request, 'users':db_select_users()})

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# RESTful User Routes

# GET /users
# Used to query a collection of all users
@app.get('/users')
def get_users() -> dict:
  '''
  1. Query the database for all users
  2. Format the results as a list of dictionaries (JSON objects!) where the dictionary keys are:
    'id', 'first_name', and 'last_name'
  3. Return this collection as a JSON object, where the key is 'users' and the value is the list
  '''

  data = db_select_users()

  return {'users': data}

# GET /users/{user_id}
# Used to query a single user
@app.get('/users/{user_id}')
def get_user(user_id:int) -> dict:
  '''
  1. Query the database for the user with a database ID of 'user_id'
  2. If the user does not exist, return an empty object
  3. Otherwise, format the result as JSON where the keys are: 'id', 'first_name', and 'last_name'
  4. Return this object
  '''
  data = db_select_users(user_id)

  if data != None:
    return JSONResponse(data)

  return {}

# POST /users
# Used to create a new user
@app.post("/users")
async def post_user(request:Request) -> dict:
  '''
  1. Retrieve the data asynchronously from the 'request' object
  2. Extract the first and last name from the POST body
  3. Create a new user in the database
  4. Return the user record back to the client as JSON
  '''

  data = await request.json()
  # print(data)

  first_name = data.get("first_name", "")
  last_name = data.get("last_name", "")

  # print(first_name)
  # print(type(first_name))
  # print(last_name)

  user_id = db_create_user(first_name,last_name)

  if user_id != None: 
    user_data = db_select_users(user_id)
    print(user_data)
    return user_data

  return {}

# PUT /users/{user_id}
@app.put('/users/{user_id}')
async def put_user(user_id:int, request:Request) -> dict:
  '''
  1. Retrieve the data asynchronously from the 'request' object
  2. Attempt to update the user first and last name in the database
  3. Return the update status under the 'success' key
  '''
  response = db_update_user(user_id,request)
  return {response: False}

# DELETE /users/{user_id}
@app.delete('/users/{user_id}')
def delete_user(user_id:int) -> dict:
  '''
  1. Attempt to delete the user from the database
  2. Return the delete status under the 'success' key
  '''
  response = db_delete_user(user_id)
  return {response: False}

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# If running the server directly from Python as a module
if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=6543, reload=True)