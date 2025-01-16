from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user
from flask_cors import CORS
from datetime import datetime, timezone, date

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
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)


class Company(db.Model):
    __tablename__ = 'company'  # Optional: Explicitly setting the table name
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), unique=True)
    BusinessName = db.Column(db.String(100))
    BusinessPhone = db.Column(db.String(15))
    BusinessAddress = db.Column(db.String(255))
    BusinessWebsite = db.Column(db.String(255))
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)

class Projects(db.Model):
    __tablename__ = 'projects'  # Optional: Explicitly setting the table name
    id = db.Column(db.Integer, primary_key=True)
    projectName = db.Column(db.String(100))
    closingDate = db.Column(db.Date)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postalCode = db.Column(db.String(100))
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)
    bids = db.relationship('Bids', backref='project', lazy=True)



class Bids(db.Model):
    __tablename__ = 'bids'  # Optional: Explicitly setting the table name
    id = db.Column(db.Integer, primary_key=True)
    projectName = db.Column(db.String(100))
    closingDate = db.Column(db.DateTime)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postalCode = db.Column(db.String(100))
    bidAmount = db.Column(db.Float)  
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)


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
    
    return render_template('Dashboard.html', valid_role=valid_user.role)

@app.route('/dashboard/chart', methods=['GET'])
@login_required
def dashboard_chart():
    current_year = datetime.now().year
    projects_count = [0] * 12
    bid_projects_count = [0] * 12
    projects = Projects.query.filter(Projects.created_at >= f'{current_year}-01-01').all()
    bids = Bids.query.filter(Bids.created_at >= f'{current_year}-01-01').all()

    for project in projects:
        month_index = project.created_at.month - 1  # Months are 1-12
        projects_count[month_index] += 1

    for bid in bids:
        month_index = bid.created_at.month - 1
        bid_projects_count[month_index] += 1

    return jsonify({
        'projects': projects_count,
        'bids': bid_projects_count
    })

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
    print("pppppp", user.state)
    if user is None:
        return jsonify({"error": "User not found."}), 404
    
    user_data = {
        "id": user.id,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "username": user.username,
        "role": user.role,
        "state": user.state
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
        state = data.get('state')

        print("Updating data: username =", username, ", state =", state)
        if state == "true":
            states = 1
        else:
            states = 0
        # Use db.session to retrieve the user
        user = db.session.get(User, user_id)  # Use Session.get() instead

        if user is None:
            return jsonify({"error": "User not found"}), 404

        # Update user attributes
        user.firstName = firstName
        user.lastName = lastName
        user.username = username
        user.role = role
        user.state = states
        
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
        closingDate = request.json.get('closingDate')
        projectName = request.json.get('projectName')
        address = request.json.get('address')
        city = request.json.get('city')
        province = request.json.get('province')
        postalCode = request.json.get('postalCode')

        try:
            closingDates = datetime.strptime(closingDate, '%Y-%m-%d')
        except ValueError as e:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        new_project = Projects(
            projectName=projectName,
            closingDate=closingDates,
            address=address,
            city=city,
            province=province,
            postalCode=postalCode
        )   

    # Add the new project to the session and commit
        db.session.add(new_project)
        db.session.commit()
        return jsonify({'message': 'Add project successfully!'})



    return render_template('Add_Project.html')


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

@app.route('/Project_Search')
@login_required
def Project_Search():
    return render_template('Project_Search.html')

@app.route('/project_search/search', methods=['GET'])
def search_projects():
    # Extract query parameters
    project_name = request.args.get('projectName', '').strip()
    address = request.args.get('address', '').strip()
    city = request.args.get('city', '').strip()
    province = request.args.get('province', '').strip()
    postalCode = request.args.get('postalCode', '').strip()
    
    # Query the Projects table for matching records
    query = Projects.query

    # Apply filters if parameters are provided
    if project_name:
        query = query.filter(Projects.projectName.ilike(f'%{project_name}%'))
    if address:
        query = query.filter(Projects.address.ilike(f'%{address}%'))
    if city:
        query = query.filter(Projects.city.ilike(f'%{city}%'))
    if province:
        query = query.filter(Projects.province.ilike(f'%{province}%'))
    if postalCode:
        query = query.filter(Projects.postalCode.ilike(f'%{postalCode}%'))

    results = query.all()  # Fetch all matching records

    # Prepare response data
    projects_list = [{
        'id': project.id,
        'projectName': project.projectName,
        'closingDate': project.closingDate.strftime('%Y-%m-%d') if project.closingDate else None,
        'address': project.address,
        'city': project.city,
        'province': project.province,
        'postalCode':project.postalCode
    } for project in results]

    return jsonify(projects_list)

@app.route('/Bid_Entry/<int:projectId>', methods=['GET', 'POST'])
@login_required
def project_entry(projectId):
    if request.method == 'GET':
        user_name = current_user.username
        user = User.query.filter_by(username=user_name).first()
        user_division = user.division
        return render_template('Bid_Entry.html', division=user_division, projectId=projectId)
    
    if request.method == 'POST':
        user_name = current_user.username
        user = User.query.filter_by(username=user_name).first()
        user_division = user.division
        user_domain = user.domain
        company = Company.query.filter_by(domain=user_domain ).first()
        companyId = company.id
        closingDate = request.json.get('closingDate')
        projectName = request.json.get('projectName')
        address = request.json.get('address')
        city = request.json.get('city')
        province = request.json.get('province')
        totalValue = request.json.get('totalValue')

        try:
            closingDates = datetime.strptime(closingDate, '%Y-%m-%d')
        except ValueError as e:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        new_bid = Bids(
            projectName=projectName,
            closingDate=closingDates,
            address=address,
            city=city,
            province=province,
            bidAmount=totalValue,
            project_id=projectId,
            company_id=companyId
        )   
        db.session.add(new_bid)
        db.session.commit()
        return jsonify({'message': 'Bid to the project successfully!'})

@app.route('/detailed_reports')
@login_required
def detailed_reports():
    return render_template('detailed_reports.html')

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