import datetime
import bcrypt
import jwt
import os
import uuid 

def update_headers(resp):
  resp.headers['Access-Control-Allow-Origin'] = "*"
  resp.headers['Strict-Transport-Security'] = "max-age=31536000"
  resp.headers['X-Frame-Options'] = "DENY"
  resp.headers['Content-Security-Policy'] = "default-src 'none'"
  resp.headers['X-Content-Type-Options'] = "nosniff"
  #resp.headers['Content-Type'] = "application/json"
  return resp

def get_headers():
  headers = {}
  headers['Access-Control-Allow-Origin'] = "*"
  headers['Strict-Transport-Security'] = "max-age=31536000"
  headers['X-Frame-Options'] = "DENY"
  headers['Content-Security-Policy'] = "default-src 'none'"
  headers['X-Content-Type-Options'] = "nosniff"
  #resp.headers['Content-Type'] = "application/json"
  return headers

def get_date_time():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
  
def hash_password_func(password):
  salt = bcrypt.gensalt()
  hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
  return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
  provided_hash = bcrypt.hashpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
  if provided_hash.decode("utf-8") == hashed_password:
    return True
  else:
    return False
  
def generateJWTToken(payload_employee_id):
  secret_value_jwt = os.getenv("SECRET_KEY")
  expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
  payload = {
            "sub": "employee_id",
            "iss": "employee_id token generation",
            "employeeid": payload_employee_id,
            "exp": expiry_time
        }
  jwt_token = jwt.encode(payload, secret_value_jwt, algorithm="HS256")
  return jwt_token

def verifyJWTToken(jwt_token):
    try:
        secret_value_jwt = os.getenv("SECRET_KEY")
        payload = jwt.decode(jwt_token, secret_value_jwt, algorithms=["HS256"])
        employee_id = payload.get('employeeid')
        return employee_id, None
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None, "Invalid token"

def generate_id():
  return str(uuid.uuid4()).replace('-', '')

def generate_timenow_function():
  return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

