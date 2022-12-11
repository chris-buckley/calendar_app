import calendar
from datetime import datetime
import pymssql
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import Sequence

from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

# Connect to the SQL server
conn = pymssql.connect(server='host.docker.internal', user='sa', password='Pringles!234', database='master')

# Set the autocommit property to True
conn.autocommit(True)

# Create a cursor
cursor = conn.cursor()

# Check if the database exists
database_exists_stmt = "SELECT COUNT(*) FROM sys.databases WHERE name = 'my_app';"
cursor.execute(database_exists_stmt)
result = cursor.fetchone()
if result[0] == 0:
    # The database does not exist, so create it
    create_database_stmt = "CREATE DATABASE my_app;"
    cursor.execute(create_database_stmt)

# Set the autocommit property back to False
conn.autocommit(False)

# Check if the user_account table exists
table_exists_stmt = "SELECT COUNT(*) FROM sys.tables WHERE name = 'user_account';"
cursor.execute(table_exists_stmt)
result = cursor.fetchone()
if result[0] == 0:
    # The table does not exist, so create it
    create_table_stmt = """
    CREATE TABLE user_account (
        id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    );
    """

    # Execute the CREATE TABLE statement using the cursor
    cursor.execute(create_table_stmt)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://sa:Pringles!234@host.docker.internal/my_app'

# Create a SQLAlchemy object
db = SQLAlchemy(app)

# Define a model for the user_account table
class User_account(db.Model):
    id = db.Column(db.Integer, Sequence('user_account_id_seq'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

# Create a new User_account object
user = User_account(id=1, name='John Doe', email='johndoe@example.com')

# Insert the object into the user_account table
with app.app_context():
    db.session.add(user)
    db.session.commit()

# Retrieve all records from the user_account table
    users = db.session.query(User_account).all()

# Print the name and email of each user
for user in users:
    print(f"{user.name}: {user.email}")


@app.route('/')
@app.route('/calender')
def calendar_view():
    year = request.args.get('year', default=None)
    month = request.args.get('month', default=None)

    # If no year and month are provided, use the current year and month
    if year is None or month is None:
        year = datetime.now().year
        month = datetime.now().month

    # Convert year and month to integers, if they are not None
    if year is not None:
        year = int(year)
    if month is not None:
        month = int(month)

    # Get the calendar for the given year and month
    cal = calendar.monthcalendar(year, month)

    return render_template('calendar.html', cal=cal, year=year, month=month)
