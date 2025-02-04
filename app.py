from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user
from flask_cors import CORS
from datetime import datetime, timezone, date, timedelta
from sqlalchemy import JSON 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_session import Session
import redis


app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secretkey'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Optional: Explicitly setting the table name
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
    country = db.Column(db.String(100))
    province = db.Column(db.String(100))
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
    closingDate = db.Column(db.Date)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postalCode = db.Column(db.String(100))
    bidAmount = db.Column(db.JSON)  
    totalAmount = db.Column(db.Float)
    division = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)


@app.before_request
def create_tables():
    db.create_all()

bcrypt = Bcrypt(app)
cors = CORS(app)
Session(app)

active_users = set()

@login_manager.user_loader
def load_user(user_id):
    print(user_id, "llllllllllllllllllllll")
    return User.query.get(int(user_id))

@app.before_request
def track_active_users():
    print("ooooooo", session)
    if '_user_id' in session:
        print("kkkkkkkkkkkkkkkkkkk")
        active_users.add(session['_user_id'])

@app.route('/active_users')
def get_active_users():
    return {'active_users': len(active_users)}


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def About():
    return render_template('About.html')

@app.route('/terms_of_use')
def terms_of_use():
    return render_template('terms.html')

@app.route('/subscription_agreement')
def subscription_agreement():
    return render_template('subscription_agreement.html')

@app.route('/Privacy_Policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/networking')
def networking():
    return render_template('Networking_Contacts.html')

@app.route('/blog')
def blog():
    return render_template('blog_page.html')

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
                                        BusinessWebsite=BusinessWebsite,country=country, province=province)
                new_user = User(division=division, country=country, province=province,
                                firstName=firstName, lastName=lastName, mobileNumber=mobileNumber,
                                username=username, password=hash_password, domain=domain, state=True, role="Admin")

                db.session.add(new_company)
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify({'message': 'Register Successfully'})
        else:
            return jsonify({'message': "Username already exists."}), 401

@app.route('/register/company', methods=['GET'])
def registerCompany():
    queries = request.args.get('query', '').lower()
    print("query:", queries)
    
    if queries:
        # Modified query to find companies where BusinessName contains the search query
        companies = Company.query.filter(Company.BusinessName.ilike(f'%{queries}%')).all()
        
        # Prepare the response data
        company_list = []
        for company in companies:
            company_data = {
                'id': company.id,
                'BusinessName': company.BusinessName,
                'BusinessPhone': company.BusinessPhone,
                'BusinessAddress': company.BusinessAddress,
                'BusinessWebsite': company.BusinessWebsite,
                'country': company.country,
                'province':company.province
            }
            company_list.append(company_data)

        # Return the JSON response
        return jsonify(company_list)
    
    # If no query, return an empty list
    return jsonify([])

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

@app.route('/subscription_details', methods=['GET'])
@login_required
def subscription():
    return render_template('subscription_details.html')



# -------------- Start Dashboard Page ----------------

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    
    return render_template('Dashboard.html', valid_role=valid_user.role)

@app.route('/dashboard/chart', methods=['GET'])
@login_required
def dashboard_chart():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    domain = user.domain
    company = Company.query.filter_by(domain=domain).first()
    company_id = company.id
    current_year = datetime.now().year
    projects_count = [0] * 12
    bid_projects_count = [0] * 12
    projects = Projects.query.filter(Projects.created_at >= f'{current_year}-01-01').all()
    # bids = Bids.query.filter(Bids.created_at >= f'{current_year}-01-01', company_id=company_id).all()
    bids = Bids.query.filter(
        Bids.created_at >= f'{current_year}-01-01',
        Bids.company_id == company_id  # Use the attribute from the model here
    ).all()
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

# -------------- End Dashboard Page ------------------

# -------------- Start Report Page -------------------
def format_currency(value):
    if value is None:
        return "0.00"
    
    # Format the number
    return f"{value:,.2f}"

@app.route('/detailed_reports')
@login_required
def detailed_reports():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    division = user.division
    domain = user.domain
    company = Company.query.filter_by(domain=domain).first()
    company_id = company.id
    
    # Get current year and previous year
    current_year = datetime.now().year
    previous_year = current_year - 1

    # Query bids for current year
    current_year_bids = Bids.query.filter(
        Bids.company_id == company_id,
        Bids.created_at >= datetime(current_year, 1, 1),
        Bids.created_at < datetime(current_year + 1, 1, 1)  # Exclude next year
    ).all()

    # Query bids for previous year
    previous_year_bids = Bids.query.filter(
        Bids.company_id == company_id,
        Bids.created_at >= datetime(previous_year, 1, 1),
        Bids.created_at < datetime(current_year, 1, 1)  # Exclude current year
    ).all()

    # Calculate total value and counts
    current_year_total_value = sum(bid.totalAmount for bid in current_year_bids)
    formatted_value = format_currency(current_year_total_value)
    current_year_number_bids = len(current_year_bids)

    previous_year_total_value = sum(bid.totalAmount for bid in previous_year_bids)
    previous_year_number_bids = len(previous_year_bids)

    # Calculate percentages safely
    if previous_year_total_value > 0:
        percent_from_previous_value = (current_year_total_value / previous_year_total_value) * 100
    else:
        percent_from_previous_value = 0  # or None, or some other default value

    if previous_year_number_bids > 0:
        percent_from_previous_number = (current_year_number_bids / previous_year_number_bids) * 100
    else:
        percent_from_previous_number = 0  # or None, or some other default value

    print(percent_from_previous_number, percent_from_previous_value)

    return render_template('detailed_reports.html', 
                           division=division,
                           current_year_total_value=formatted_value,
                           current_year_number_bids=current_year_number_bids,
                           percent_from_previous_number=percent_from_previous_number,
                           percent_from_previous_value=percent_from_previous_value)


@app.route('/detailed_reports/chart/project', methods=['POST'])
@login_required
def reports_chart_project():
    year = request.json.get('currentYear')
    year = int(year)
    projects_count = [0] * 12
    bid_projects_count = [0] * 12

    # Get the current user's information
    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    domain = valid_user.domain
    
    # Find the company associated with the current user's domain
    company = Company.query.filter_by(domain=domain).first()


    company_id = company.id

    # Query projects created in the current year
    projects = Projects.query.filter(Projects.created_at >= f'{year}-01-01',Projects.created_at < f'{year + 1}-01-01').all()

    # Count projects by month
    for project in projects:
        month_index = project.created_at.month - 1  # Months are 1-12
        projects_count[month_index] += 1

    # Query bids for the current year belonging to the current user company
    bids = Bids.query.filter(
        Bids.created_at >= f'{year}-01-01',
        Bids.created_at < f'{year + 1}-01-01',
        Bids.company_id == company_id  # Assuming Bids table has a company_id field
    ).all()

    # Count bids associated with the company by month
    for bid in bids:
        month_index = bid.created_at.month - 1
        bid_projects_count[month_index] += 1

    return jsonify({
        'totalprojects': projects_count,
        'userbids': bid_projects_count
    })

@app.route('/detailed_reports/chart/months', methods=['POST'])
@login_required
def reports_chart_months():
    month = request.json.get('selectedMonth')
    year = request.json.get('selectedYears')

    (month, year, "month, years")
    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    domain = valid_user.domain
    bid_user_id = valid_user.id
    user_division = valid_user.division
    company = Company.query.filter_by(domain=domain).first()
    
    if not company:
        return jsonify({"error": "Company not found for the user."}), 404

    company_id = company.id

    # Fetch bids by the company's user for the specified year and month
    bids = Bids.query.filter(
        Bids.user_id == bid_user_id,
        db.extract('year', Bids.created_at) == year,
        db.extract('month', Bids.created_at) == month
    ).all()

    # Retrieve project_ids from bids made by the user
    project_ids_with_bids = set(bid.project_id for bid in bids)

    # Get all projects that have bids
    projects = Projects.query.filter(Projects.id.in_(project_ids_with_bids)).all()

    # Create a mapping from project id to all bids for that project to find the lowest
    project_bids = {project.id: [] for project in projects}

    # Populate project_bids with all relevant bids
    all_bids = Bids.query.filter(Bids.project_id.in_(project_ids_with_bids),
                                 Bids.division == user_division).all()
    for bid in all_bids:
        if bid.project_id in project_bids:
            project_bids[bid.project_id].append(bid.totalAmount)

    project_ids = []
    contractor_prices = []
    lowest_prices = []
    max_prices = []
    project_name = []
    city = []
    province = []

    # Now gather data for each project
    for project in projects:
        project_ids.append(f"CH-{str(project.id).zfill(2)}")
        project_name.append(project.projectName)
        city.append(project.city)
        province.append(project.province)
        
        # Get the user's bid for the project, if any
        user_bid = next((bid.totalAmount for bid in bids if bid.project_id == project.id), 0)

        # Aggregate prices and find the lowest price
        amounts = project_bids[project.id]
        contractor_prices.append(user_bid)  # User's bid for the project
        lowest_prices.append(min(amounts) if amounts else 0)  # Lowest bid among all bids
        max_prices.append(max(amounts) if amounts else 0)  # Lowest bid among all bids

    return jsonify({
        "projectIds": project_ids,
        "contractorPrices": contractor_prices,
        "lowestPrices": lowest_prices,
        "maxPrices": max_prices,
        "project_name": project_name,
        "city": city,
        "province": province
    })

@app.route('/detailed_report/project/table', methods=['POST'])
@login_required
def detailed_report_project():
    project_id = request.json.get('projectId')
    projectId = project_id.split('-')[1]  # This will get '01'
    projectId = int(projectId)  # Convert '01' to an integer, resulting in 1
    project = Projects.query.filter_by(id=projectId).first()
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_division = user.division
    user_ID = user.id
    bids = Bids.query.filter_by(project_id=projectId, division = user_division).all()

    current_user_id = current_user.id  # Get the logged user's ID
    totalAmount = []
    bid_list = []
    for bid in bids:
        totalAmount.append(bid.totalAmount)
        # user = User.query.filter_by(id=bid.user_id).first()
        company = Company.query.filter_by(id=bid.company_id).first()
        bidder_name = company.BusinessName
        bid_details = {
            'user_id': bid.user_id,
            'bid_price': bid.totalAmount,  # Assuming totalAmount is the bid price
            'bidder_name': bidder_name,   # Replace with the actual attribute for the bidder name
        }
        bid_list.append(bid_details)


    max_value = max(totalAmount)
    min_value = min(totalAmount)
    number_bid = len(bids)


    def calculate_average(data):
        if not data:
            return 0  # Return 0 or any other default value you prefer
        return sum(data) / len(data)

    # Assuming 'bids' is your list of Bid objects
    bid_prices = [bid.totalAmount for bid in bids]
    average_bid_price = calculate_average(bid_prices)

    formatted_average_bid_price = f"${average_bid_price:,.2f}"

    data = {
        'user_id':user_ID,
        'projectname':project.projectName,
        'closingDate':project.closingDate,
        'address':project.address,
        'city':project.city,
        'province':project.province,
        'postalCode':project.postalCode,
        'bids': bid_list,  # Add the list of bids
        'maxBidPrice': max_value,
        'minBidPrice': min_value,
        'medianBidPrice': formatted_average_bid_price,
        'number_bid': number_bid
    }

    return jsonify(data)

@app.route('/detailed_report/project/table_915', methods=['POST'])
@login_required
def detailed_report_project_915():
    project_id = request.json.get('projectId')
    selectedDivision = request.json.get('selectedDivision')
    projectId = project_id.split('-')[1]  # This will get '01'
    projectId = int(projectId)  # Convert '01' to an integer, resulting in 1
    project = Projects.query.filter_by(id=projectId).first()
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_division = user.division
    user_ID = user.id
    bids = Bids.query.filter_by(project_id=projectId, division = user_division).all()

    current_user_id = current_user.id  # Get the logged user's ID
    totalAmount = []
    bid_list = []
    for bid in bids:
        bid_amount = bid.bidAmount[selectedDivision]

        if bid_amount:  # This checks if the string is not empty
            totalAmount.append(float(bid_amount))
        else:
            # Handle the case where bid_amount is empty, e.g.:
            print(f"No bid amount for division {selectedDivision}")
        # user = User.query.filter_by(id=bid.user_id).first()
        company = Company.query.filter_by(id=bid.company_id).first()
        bidder_name = company.BusinessName
        bid_details = {
            'user_id': bid.user_id,
            'bid_price': bid.bidAmount[selectedDivision],  # Assuming totalAmount is the bid price
            'bidder_name': bidder_name   # Replace with the actual attribute for the bidder name
        }
        bid_list.append(bid_details)

    max_value = max(totalAmount)
    min_value = min(totalAmount)
    number_bid = len(bids)

    average_bid_price = sum(totalAmount) / number_bid

    formatted_average_bid_price = f"${average_bid_price:,.2f}"

    data = {
        'user_id':user_ID,
        'projectname':project.projectName,
        'closingDate':project.closingDate,
        'address':project.address,
        'city':project.city,
        'province':project.province,
        'postalCode':project.postalCode,
        'bids': bid_list,  # Add the list of bids
        'maxBidPrice': max_value,
        'minBidPrice': min_value,
        'medianBidPrice': formatted_average_bid_price,
        'number_bid': number_bid
    }

    return jsonify(data)

@app.route('/detailed_reports/chart/division', methods=['POST'])
@login_required
def reports_chart_division():
    month = request.json.get('selectedMonths')
    year = request.json.get('selectedYears')
    selectedDivision = request.json.get('selectedDivision')  # Get division from the request, convert to int
    division = int(request.json.get('division__'))

    
    # Validate inputs
    if month is None or year is None or selectedDivision is None:
        return jsonify({"error": "Missing required parameters."}), 400

    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    domain = valid_user.domain
    company = Company.query.filter_by(domain=domain).first()
    
    if not company:
        return jsonify({"error": "Company not found for the user."}), 404

    company_id = company.id

    # Fetch bids by the company's user for the specified year and month
    bids = Bids.query.filter(
        Bids.company_id == company_id,
        db.extract('year', Bids.created_at) == year,
        db.extract('month', Bids.created_at) == month
    ).all()

    # Retrieve project_ids from bids made by the user
    project_ids_with_bids = {bid.project_id for bid in bids}
    # Get all projects that have bids
    projects = Projects.query.filter(Projects.id.in_(project_ids_with_bids)).all()

    # Create a mapping from project id to all bids for that project
    project_bids = {project.id: [] for project in projects}
    all_bids = Bids.query.filter(
        Bids.project_id.in_(project_ids_with_bids), 
        Bids.division == division  # Use equality instead of 'in_' method
    ).all()
    for bid in all_bids:
        if bid.project_id in project_bids:
            if isinstance(bid.bidAmount, (list, dict)):
                project_bids[bid.project_id].append(bid.bidAmount)
            else:
                project_bids[bid.project_id].append([bid.bidAmount])  # Convert to a list

    # Initialize the response lists
    project_ids = []
    contractor_prices = []
    lowest_prices = []
    max_prices = []
    project_names = []
    city = []
    province = []

    # Now gather data for each project
    for project in projects:
        project_ids.append(f"CH-{str(project.id).zfill(2)}")
        project_names.append(project.projectName)
        city.append(project.city)
        province.append(project.province)

        # Get the user's bid for the project, if any
        user_bid_data = next((b.bidAmount[selectedDivision] for b in bids if b.project_id == project.id), 0)
        contractor_prices.append(user_bid_data)

        # Aggregate prices and find the lowest price
        amounts = []
        for bid in project_bids[project.id]:
            amounts.append(bid[selectedDivision])

        lowest_prices.append(min(amounts) if amounts else 0)  # Lowest bid among all bids
        max_prices.append(max(amounts) if amounts else 0)  # Max bid among all bids

    return jsonify({
        "projectIds": project_ids,
        "contractorPrices": contractor_prices,
        "lowestPrices": lowest_prices,
        "maxPrices": max_prices,
        "project_name": project_names,
        "city": city,
        "province": province
    })

# -------------- End Report Page -------------------

# -------------- Start User Management Page -------------------

@app.route('/user_management')
@login_required
def user_management():
    username = current_user.username
    valid_user = User.query.filter_by(username=username).first()
    valid_domain = valid_user.domain
    users_with_same_domain = User.query.filter_by(domain=valid_domain).all()
    return render_template('User_Management.html', users=users_with_same_domain)

@app.route('/user_management/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
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
@login_required
def update_user(user_id):
    try:
        data = request.get_json()
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        username = data.get('username')
        role = data.get('role')
        state = data.get('state')

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

# -------------- End User Management Page -------------------

# -------------- Start Add Project Page -------------------

@app.route('/add_project', methods=['GET', 'POST'])
@login_required
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

# -------------- End Add Project Page -------------------

# -------------- Start Profile Page -------------------

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

# -------------- End Add Project Page -------------------

# -------------- Start Project Search Page -------------------

@app.route('/Project_Search')
@login_required
def Project_Search():
    return render_template('Project_Search.html')

@app.route('/project_search/search', methods=['GET'])
@login_required
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

@app.route('/project_search/bid/<int:projectId>')
@login_required
def project_search_bid(projectId):
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_id = user.id
  
    bid = Bids.query.filter_by(project_id=projectId, user_id=user_id).first() 
    
    if not bid:
        return jsonify({"message": "Do you wish to submit a bid for this project?", "state": 4})
    
    project = bid.project  # Assuming you have a 'project' relationship in Bids
    
    if project.closingDate < datetime.now().date():
        return jsonify({"message": "No revisions allowed; project is closed!", "state": 2})

    created_at = bid.created_at
    time_diff = datetime.now().date() - timedelta(hours=24)

    if created_at >= time_diff:
        return jsonify({"message": "You can edit your bid after 24 hours!", "state": 1})
    else:
        return jsonify({"message": "Do you wish to edit your bid for this project?", "state": 3})

# -------------- End Project Search Page -------------------

# -------------- Start Bid Entry Page -------------------

@app.route('/Bid_Entry/<int:projectId>', methods=['GET', 'POST'])
@login_required
def project_entry(projectId):
    if request.method == 'GET':
        user_name = current_user.username
        user = User.query.filter_by(username=user_name).first()
        user_division = user.division
        project = Projects.query.filter_by(id=projectId).first()
        project_closingDate = project.closingDate
        project_projectName = project.projectName
        project_address = project.address
        project_city = project.city
        project_province = project.province
        project_postalCode = project.postalCode

        return render_template('Bid_Entry.html', division=user_division, projectId=projectId, 
                                project_closingDate=project_closingDate, project_projectName=project_projectName, 
                                project_address=project_address, project_city=project_city,
                                project_province=project_province, project_postalCode=project_postalCode)
    
    if request.method == 'POST':
        user_name = current_user.username
        user = User.query.filter_by(username=user_name).first()
        user_division = user.division
        user_domain = user.domain
        user_id = user.id
        company = Company.query.filter_by(domain=user_domain ).first()
        companyId = company.id
        closingDate = request.json.get('closingDate')
        projectName = request.json.get('projectName')
        address = request.json.get('address')
        city = request.json.get('city')
        province = request.json.get('province')
        bidamount = request.json.get('amounts')
        postalCode = request.json.get('postalCode')
        totalAmount = request.json.get('totalAmount')

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
            bidAmount=bidamount,
            project_id=projectId,
            company_id=companyId,
            user_id=user_id,
            postalCode=postalCode,
            totalAmount=totalAmount,
            division=user_division
        )   
        db.session.add(new_bid)
        db.session.commit()
        return jsonify({'message': 'Bid to the project successfully!'})

@app.route('/editbid/<int:projectId>', methods=['PUT'])
@login_required
def editbid(projectId):
    updateClosingDate = request.get_json().get('date')
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    bid = Bids.query.filter_by(user_id=user_id, project_id=projectId).first()
    bid_id = bid.id
    bids = db.session.get(Bids, bid_id)
    parsed_date = datetime.strptime(updateClosingDate, '%Y-%m-%d').date()
    bids.closingDate = parsed_date

    db.session.commit()
    return jsonify({"message": "update succesfully!"}), 200

# -------------- End Bid Entry Page -------------------

# -------------- Start Bidding History Page -------------------

@app.route('/bidding_history')
@login_required
def bidding_history():
    return render_template('Bidding_History.html')

@app.route('/bidding_history/table')
@login_required
def bidding_history_table():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_domain = user.domain
    company = Company.query.filter_by(domain=user_domain).first()
    company_id = company.id
    bids = Bids.query.filter_by(company_id=company_id).all()

    serialized_bids = []
    for bid in bids:
        project = bid.project 
        formatted_project_id = f"CH-{bid.project_id:02d}"  
        serialized_bids.append({
            'project_id': bid.project_id,
            'formatted_project_id': formatted_project_id,
            'projectName': project.projectName if project else 'Unknown',  # Safeguard against None
            'totalAmount': bid.totalAmount,
            'closingDate': bid.closingDate
        })

    return jsonify(serialized_bids)

@app.route('/bidding_history/modal/getData/<int:projectId>')
@login_required
def bidding_history_modal(projectId):
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_division = user.division
    company__ = Company.query.filter_by(domain=user.domain).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    project = Projects.query.filter_by(id=projectId).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Get all bids for the project
    all_bids = Bids.query.filter_by(project_id=projectId, division=user_division).all()

    # Helper function to serialize Bids objects
    def serialize_bid(bid):
        company = Company.query.get(bid.company_id)  # Fetch the user based on user_id in the bid
        return {
            "id": bid.id,
            "amount": bid.bidAmount,
            "totalAmount": bid.totalAmount,
            "project_id": bid.project_id,
            "company_id": bid.company_id,
            "company": company.BusinessName if company else None  # Retrieve username if user exists
        }

    all_bids_serialized = [serialize_bid(bid) for bid in all_bids]

    data = {
        "project_address": project.address,
        "division": user.division,
        "projectName": project.projectName,
        "closingDate": project.closingDate,
        "formatted_project_id": f"CH-{projectId:02d}",
        "company_Id": company__.id,
        "all_bids": all_bids_serialized  # Changed from other_bid to all_bids
    }

    return jsonify(data)

# -------------- End Bidding History Page -------------------

# -------------- Start Company Page -------------------

@app.route('/manage_company')
@login_required
def company_detail():
    return render_template('Company_Details.html')

@app.route('/manage_company/detail')
@login_required
def manage_company_detail():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    domain = user.domain
    company = Company.query.filter_by(domain=domain).first()
    data = {
        "userId": user.id,
        "mobileNumber": user.mobileNumber,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": username,
        "companyName": company.BusinessName,
        "phoneNumber": company.BusinessPhone,
        "address": company.BusinessAddress,
        "website": company.BusinessWebsite,
        "division": user.division
    }
    return jsonify(data)

@app.route('/manage_company/<int:userId>', methods=['PUT'])
@login_required
def manage_company_detail_edit(userId):
    try:
        data = request.get_json()
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        username = data.get('email')
        mobileNumber = data.get('mobileNumber')
        companyName = data.get('companyName')
        phoneNumber = data.get('phoneNumber')
        address = data.get('address')
        website = data.get('website')
        division = data.get('division')


        users = User.query.filter_by(id=userId).first()
        user = db.session.get(User, userId)
        if not user:
            return jsonify({"error": "User not found"}), 404
    
        # Use db.session to retrieve the company
        companies = Company.query.filter_by(domain=users.domain).first()
        company_id = companies.id
        company = db.session.get(Company, company_id)
        
        company.BusinessName = companyName
        company.BusinessPhone = phoneNumber
        company.BusinessAddress = address
        company.BusinessWebsite = website
        user.firstName = firstName
        user.lastName = lastName
        user.username = username
        user.division = division
        user.mobileNumber = mobileNumber
        
        db.session.commit()  # Commit the changes to the database
        return jsonify({"message": "User and company updated successfully"}), 200  # Success response
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message if something goes wrong

# -------------- End Company Page -------------------

# -------------- Start Feedback Page -------------------
@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'GET':
        username = current_user.username
        user = User.query.filter_by(username=username).first()
        
        firstName = user.firstName
        lastName = user.lastName
        fullName = firstName + ' ' + lastName  # Corrected this line
        email = username
        
        return render_template('Feedback.html', fullName=fullName, email=email)
    
    if request.method == 'POST':
        data = request.json
        sender_email = data.get("email")
        message_body = data.get("message")

        receiver_email = "AvyaanDavid@outlook.com"
        subject = "New Feedback from ConstructHub"

        # Set up email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message_body, "plain"))

        try:
            # Configure SMTP server (Replace with your email credentials)
            smtp_server = "smtp.office365.com"
            smtp_port = 587
            smtp_user = "AvyaanDavid@outlook.com"
            smtp_password = "your-email-password"

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()

            return jsonify({"message": "Message sent successfully!"})

        except Exception as e:
            return jsonify({"message": f"Error sending message: {str(e)}"}), 500

        




# -------------- Start Feedback Page -------------------


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0")
