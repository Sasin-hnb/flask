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
    role = db.Column(db.String(100))

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
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('Register.html')
    
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
        domain = '.'.join(BusinessWebsite.split('.')[-2:])
        
        old_domain = Company.query.filter_by(domain=domain).first()
        old_user = User.query.filter_by(username=username).first()

        if not old_user:
            if old_domain:
                new_user = User(division=division, country=country, province=province,
                                firstName=firstName, lastName=lastName, mobileNumber=mobileNumber,
                                username=username, password=hash_password, domain=domain, role="Viewer")
                db.session.add(new_user)
                db.session.commit()
                return jsonify({'message': 'Register Successfully'})
            else:
                new_company = Company(domain=domain, BusinessName=BusinessName,
                                        BusinessPhone=BusinessPhone, BusinessAddress=BusinessAddress,
                                        BusinessWebsite=BusinessWebsite)
                new_user = User(division=division, country=country, province=province,
                                firstName=firstName, lastName=lastName, mobileNumber=mobileNumber,
                                username=username, password=hash_password, domain=domain, state=True, role="Admin")

                db.session.add(new_company)
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify({'message': 'Register Successfully'})
        else:
            return jsonify({'message': "Username already exists."}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('Login.html')

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
    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    print(valid_user.role, "ddddddd")
    return render_template('Dashboard.html', valid_role=valid_user.role)

@app.route('/user_management')
@login_required
def user_management():
    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    valid_domain = valid_user.domain
    users_with_same_domain = User.query.filter_by(domain=valid_domain).all()
    return render_template('User_Management.html', users=users_with_same_domain)

@app.route('/user_management/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found."}), 404
    
    user_data = {
        "id": user.id,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "username": user.username,
        "role": user.role
    }

    return jsonify(user_data), 200

@app.route('/user_management/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        username = data.get('username')
        role = data.get('role')

        print("Updating data: username =", username, ", role =", role)

        # Use db.session to retrieve the user
        user = db.session.get(User, user_id)  # Use Session.get() instead

        if user is None:
            return jsonify({"error": "User not found"}), 404

        # Update user attributes
        user.firstName = firstName
        user.lastName = lastName
        user.username = username
        user.role = role
        
        db.session.commit()  # Commit the changes to the database
        return jsonify({"message": "User updated successfully"}), 200  # Success response

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message if something goes wrong

@app.route('/user_management/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        # Retrieve the user to be deleted
        user = db.session.get(User, user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        
        current_username = current_user.username

        # Check if the current user is trying to delete themselves
        if current_username == user.username:
            # Find other users in the same domain
            other_users = User.query.filter_by(domain=user.domain).filter(User.username != user.username).all()
            
            if other_users:
                # Check if any other users exist with a non-Admin role
                for other_user in other_users:
                    if other_user.role != 'Admin':
                        # Change the first user's role to 'Admin'
                        other_user.role = 'Admin'
                        other_user.state = True
                        db.session.add(other_user)  # Ensure the change is tracked

            # Optionally, you can implement a message indicating the action taken
            # since the primary user (current_user) may be affected.
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        project_address = request.form['project_address']
        city = request.form['city']
        province = request.form['province']
        postal_code = request.form['postal_code']
        country = request.form['country']

        return redirect(url_for('search_projects'))

    return render_template('add_project.html')


@app.route('/search-projects', methods=['GET', 'POST'])
def search_projects():
    # Retrieve projects from the database and pass it to the search results page
    # You would define a Project model for this
    return render_template('search_results.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')
        email = request.json.get('email')
        phone = request.json.get('phone')
        division = request.json.get('division')
        company_name = request.json.get('company_name')

        return redirect(url_for('dashboard'))
    return render_template('profile.html')

@app.route('/detailed_reports')
@login_required
def detailed_reports():
    return render_template('detailed_report.html')

@app.route('/project_lookup')
@login_required
def project_lookup():
    return render_template('project_lookup.html')



@app.route('/project_entry')
@login_required
def project_entry():
    return render_template('project_entry.html')

@app.route('/bidding_history')
@login_required
def bidding_history():
    return render_template('bidding_history.html')

@app.route('/networking')
@login_required
def networking():
    return render_template('Networking_Contacts.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0")