from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user
from flask_cors import CORS
import os

# app = Flask(__name__, template_folder='/public_html/templates')
app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), 'public_html', 'templates'),
            static_folder=os.path.join(os.getcwd(), 'public_html', 'static'))


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'construct_hub'

# def execute_schema():
#     with mysql.connection.cursor() as cursor:
#         # Read the SQL file
#         sql_file_path = os.path.join(os.path.dirname(__file__), 'schema.sql')  # Adjust path if needed
#         with open(sql_file_path, 'r') as file:
#             sql_script = file.read()
        
#         # Execute multiple SQL statements
#         for statement in sql_script.split(';'):
#             statement = statement.strip()
#             if statement:  # Make sure it's not an empty statement
#                 try:
#                     cursor.execute(statement)
#                 except Exception as e:
#                     print(f"An error occurred: {e}")
        
#         mysql.connection.commit()  # Commit changes

# @app.before_request
# def initialize_database():
#     execute_schema()

app.secret_key = 'secretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
cors = CORS(app, origins=['http://localhost:5000'], allow_headers=['Content-Type', 'Authorization'], allow_credentials=True, supports_credentials=True)

# User Loader
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user[2])  # Here, we're using `username` as the user_id
    return None

# Home Route (Welcome Page)
@app.route('/')
def home():
    return render_template('index.html')

# Links you to the About Us page.
@app.route('/about')
def About():
    return render_template('about.html')  # Make sure the path is correct

# Links you to the Contact page.
@app.route('/contact.html')
def contact():
    return render_template('contact.html') # Make sure the path is correct



# Links you to the user registration page.
@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')  # Make sure the path is correct
    
    if request.method == 'POST':
        division = request.json.get('division')
        BusinessName = request.json.get('BusinessName')
        BusinessPhone = request.json.get('BusinessPhone')
        BusinessAddress = request.json.get('BusinessAddress')
        country = request.json.get('country')
        province = request.json.get('province')
        BusinessWebsite = request.json.get('BusinessWebsite')
        firstName = request.json.get('firstName')
        lastName = request.json.get('lastName')
        mobileNumber = request.json.get('mobileNumber')
        username = request.json.get('username')
        password = request.json.get('password')
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        domain = BusinessWebsite.split('@')[1]

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM company WHERE domain = %s", (domain, ))
        old_domain = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username, ))
        old_user = cursor.fetchone()

        if not old_user:

            if old_domain:
                print("<<<<<<<<<<")

                cursor.execute(''' INSERT INTO users (division, country, province, firstName, lastName,
                    mobileNumber, username, password, domain) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (division, country, province, firstName, lastName,
                    mobileNumber, username, hash_password, domain))
                return jsonify({'message': 'Register Successfully'})
            else:
                print(">>>>>>>")
                cursor.execute(''' INSERT INTO company (domain, BusinessName, BusinessPhone, BusinessAddress, BusinessWebsite) 
                    VALUES(%s, %s, %s, %s, %s)''',
                    (domain, BusinessName, BusinessPhone, BusinessAddress, BusinessWebsite))
                
                cursor.execute(''' INSERT INTO users (division, country, province, firstName, lastName,
                    mobileNumber, username, password, domain, state) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (division, country, province, firstName, lastName,
                    mobileNumber, username, hash_password, domain, True))
                
                mysql.connection.commit()
                cursor.close()

                
                return jsonify({'message': 'Register Successfully'})
        else:
            print("lllllddfdfdf")
            return jsonify({'message': "Username is already exist."}), 401
        

#  Links you to the user login page.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        valid_user = cursor.fetchone()
        cursor.close()

        if valid_user:
            stored_password = valid_user[8]
            valid_state = valid_user[11]
            valid_password = bcrypt.check_password_hash(stored_password, password)
            print("state", valid_state)

            if valid_password:
                if valid_state:
                    user = User(username)
                    login_user(user)  # Log in the user
                    return jsonify({'message': 'Login Success'}), 200
                else:
                    print("oooooo")

                    return jsonify({'message': "Requires administrator approval."}), 401
            else:
                return jsonify({'message': "The username or password is incorrect."}), 401
        else:
            print("ppppppp")
            return jsonify({'message': "The username or password is incorrect."}), 401

@app.route('/dashboard', methods=['GET'])
@login_required  # This will automatically handle the token validation
def dashboard():
    return render_template('dashboard.html')
    

# Add Project Route (GET and POST)
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        project_address = request.form['project_address']
        city = request.form['city']
        province = request.form['province']
        postal_code = request.form['postal_code']
        country = request.form['country']

        # Insert the new project into the database
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO projects (name, address, city, province, postal_code, country)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_name, project_address, city, province, postal_code, country))
        conn.commit()
        conn.close()

        # Redirect to the search projects page
        return redirect(url_for('search_projects'))

    return render_template('add_project.html')

# Search Projects Route
@app.route('/search-projects', methods=['GET', 'POST'])
def search_projects():
    # Connect to the SQLite database
    # conn = sqlite3.connect('projects.db')
    # c = conn.cursor()

    # # Retrieve all projects from the database
    # c.execute('SELECT * FROM projects')
    # projects_data = c.fetchall()

    # # Close the database connection
    # conn.close()

    # Pass the projects data to the search results page
    # return render_template('search_results.html', results=projects_data)
    return render_template('search_results.html')

# Profile Route
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Logout Route (Just a placeholder for now)
@app.route('/logout')
@login_required  # Ensure that only logged-in users can access this route
def logout():
    logout_user()  # Clear the session and log out the user
    return redirect(url_for('home'))  # Redirect to home page after logout

# Run Flask App
if __name__ == '__main__':
    app.run(host="0.0.0.0")

#This is to setup to setup user database-------------------------------------
