from flask import Flask
import pymongo
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = '2f22ce414d5bebe72de663adb9e46098'
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
client = pymongo.MongoClient('localhost', 27017)
db = client.Users


from login_system import routes