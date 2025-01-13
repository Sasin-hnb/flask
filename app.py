from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user
from flask_cors import CORS

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    division = db.Column(db.String(100))
    country = db.Column(db.String(100))
    province = db.Column(db.String(100))
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    mobileNumber = db.Column(db.String(15))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    domain = db.Column(db.String(100))
    state = db.Column(db.Boolean, default=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), unique=True)
    BusinessName = db.Column(db.String(100))
    BusinessPhone = db.Column(db.String(15))
    BusinessAddress = db.Column(db.String(255))
    BusinessWebsite = db.Column(db.String(255))

@app.before_request
def create_tables():
    db.create_all()

bcrypt = Bcrypt(app)
cors = CORS(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def About():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        data = request.json
        division = data.get('division')
        BusinessName = data.get('BusinessName')
        BusinessPhone = data.get('BusinessPhone')
        BusinessAddress = data.get('BusinessAddress')
        country = data.get('country')
        province = data.get('province')
        BusinessWebsite = data.get('BusinessWebsite')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        mobileNumber = data.get('mobileNumber')
        username = data.get('username')
        password = data.get('password')
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        domain = BusinessWebsite.split('@')[1]
        
        old_domain = Company.query.filter_by(domain=domain).first()
        old_user = User.query.filter_by(username=username).first()

        if not old_user:
            if old_domain:
                new_user = User(division=division, country=country, province=province,
                                firstName=firstName, lastName=lastName, mobileNumber=mobileNumber,
                                username=username, password=hash_password, domain=domain)
                db.session.add(new_user)
                db.session.commit()
                return jsonify({'message': 'Register Successfully'})
            else:
                new_company = Company(domain=domain, BusinessName=BusinessName,
                                      BusinessPhone=BusinessPhone, BusinessAddress=BusinessAddress,
                                      BusinessWebsite=BusinessWebsite)
                new_user = User(division=division, country=country, province=province,
                                firstName=firstName, lastName=lastName, mobileNumber=mobileNumber,
                                username=username, password=hash_password, domain=domain, state=True)

                db.session.add(new_company)
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify({'message': 'Register Successfully'})
        else:
            return jsonify({'message': "Username already exists."}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')

        valid_user = User.query.filter_by(username=username).first()

        if valid_user:
            valid_password = bcrypt.check_password_hash(valid_user.password, password)

            if valid_password:
                if valid_user.state:  # Added check for user state
                    login_user(valid_user)
                    return jsonify({'message': 'Login Success'}), 200
                else:
                    return jsonify({'message': "Requires administrator approval."}), 401
            else:
                return jsonify({'message': "The username or password is incorrect."}), 401
        else:
            return jsonify({'message': "The username or password is incorrect."}), 401

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        project_address = request.form['project_address']
        city = request.form['city']
        province = request.form['province']
        postal_code = request.form['postal_code']
        country = request.form['country']

        # Use SQLAlchemy to insert the new project into your project model
        # You would define a Project model for this
        # conn = sqlite3.connect('projects.db')
        # c = conn.cursor()
        # c.execute('''
        #     INSERT INTO projects (name, address, city, province, postal_code, country)
        #     VALUES (?, ?, ?, ?, ?, ?)
        # ''', (project_name, project_address, city, province, postal_code, country))
        # conn.commit()
        # conn.close()

        # Redirect to the search projects page
        return redirect(url_for('search_projects'))

    return render_template('add_project.html')


@app.route('/search-projects', methods=['GET', 'POST'])
def search_projects():
    # Retrieve projects from the database and pass it to the search results page
    # You would define a Project model for this
    return render_template('search_results.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0")