from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# =====================
# APP CONFIG
# =====================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# =====================
# LOGIN MANAGER
# =====================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# =====================
# MODELS
# =====================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    faculties = db.Column(db.String(500))
    application_start = db.Column(db.String(50))
    tuition_fee = db.Column(db.String(100))
    documents = db.Column(db.String(500))
    website = db.Column(db.String(300))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text)
    date_submitted = db.Column(db.DateTime, default=db.func.now())

    university = db.relationship('University', backref=db.backref('applications', lazy=True))


# =====================
# USER LOADER
# =====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================
# IMPORT INITIAL UNIVERSITIES
# =====================
def import_universities():
    if University.query.first():
        return  # Already imported

    universities = [
        {"name": "University of Oxford", "country": "United Kingdom", "city": "Oxford",
         "faculties": "Humanities; Engineering; Medicine; Law; Business", "application_start": "October",
         "tuition_fee": "£25,000–£45,000", "documents": "Passport; Diploma; Transcript; IELTS; Motivation Letter; CV",
         "website": "https://www.ox.ac.uk"},

        {"name": "University of Cambridge", "country": "United Kingdom", "city": "Cambridge",
         "faculties": "Science; Engineering; Arts; Medicine; Economics", "application_start": "October",
         "tuition_fee": "£24,000–£42,000", "documents": "Passport; Diploma; Transcript; IELTS; Recommendation Letters",
         "website": "https://www.cam.ac.uk"},

        {"name": "Imperial College London", "country": "United Kingdom", "city": "London",
         "faculties": "Engineering; Medicine; Natural Sciences; Business", "application_start": "October",
         "tuition_fee": "£28,000–£47,000", "documents": "Passport; Diploma; Transcript; IELTS; Motivation Letter",
         "website": "https://www.imperial.ac.uk"},

        {"name": "ETH Zurich", "country": "Switzerland", "city": "Zurich",
         "faculties": "Engineering; Architecture; Natural Sciences", "application_start": "December",
         "tuition_fee": "CHF 1,500 per semester", "documents": "Passport; Diploma; Transcript; Language Certificate",
         "website": "https://ethz.ch/en.html"},

        {"name": "EPFL", "country": "Switzerland", "city": "Lausanne",
         "faculties": "Engineering; Computer Science; Physics", "application_start": "December",
         "tuition_fee": "CHF 1,300 per semester", "documents": "Passport; Diploma; Transcript; Language Certificate",
         "website": "https://www.epfl.ch/en/"},

        {"name": "University of Amsterdam", "country": "Netherlands", "city": "Amsterdam",
         "faculties": "Social Sciences; Economics; Law; Humanities", "application_start": "January",
         "tuition_fee": "€8,000–€15,000", "documents": "Passport; Diploma; Transcript; IELTS; Motivation Letter",
         "website": "https://www.uva.nl/en"},

        {"name": "Delft University of Technology", "country": "Netherlands", "city": "Delft",
         "faculties": "Engineering; Architecture; Technology", "application_start": "January",
         "tuition_fee": "€15,000–€18,000", "documents": "Passport; Diploma; Transcript; IELTS",
         "website": "https://www.tudelft.nl/en"},

        {"name": "Leiden University", "country": "Netherlands", "city": "Leiden",
         "faculties": "Law; Political Science; Humanities", "application_start": "January",
         "tuition_fee": "€10,000–€15,000", "documents": "Passport; Diploma; Transcript; Motivation Letter",
         "website": "https://www.universiteitleiden.nl/en"},

        {"name": "Technical University of Munich", "country": "Germany", "city": "Munich",
         "faculties": "Engineering; Computer Science; Medicine", "application_start": "May",
         "tuition_fee": "No tuition fee", "documents": "Passport; Diploma; Transcript; Language Certificate",
         "website": "https://www.tum.de/en/"},

        {"name": "Ludwig Maximilian University of Munich", "country": "Germany", "city": "Munich",
         "faculties": "Humanities; Medicine; Law; Economics", "application_start": "May",
         "tuition_fee": "No tuition fee", "documents": "Passport; Diploma; Transcript; Language Certificate",
         "website": "https://www.en.uni-muenchen.de/"},

        {"name": "Heidelberg University", "country": "Germany", "city": "Heidelberg",
         "faculties": "Medicine; Law; Natural Sciences", "application_start": "May",
         "tuition_fee": "No tuition fee", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.uni-heidelberg.de/en"},

        {"name": "Sorbonne University", "country": "France", "city": "Paris",
         "faculties": "Arts; Humanities; Science; Medicine", "application_start": "January",
         "tuition_fee": "€3,000–€4,000", "documents": "Passport; Diploma; Transcript; Language Certificate",
         "website": "https://www.sorbonne-universite.fr/en"},

        {"name": "Université Paris-Saclay", "country": "France", "city": "Paris",
         "faculties": "Science; Engineering; Mathematics", "application_start": "January",
         "tuition_fee": "€3,500", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.universite-paris-saclay.fr/en"},

        {"name": "Sciences Po", "country": "France", "city": "Paris",
         "faculties": "Political Science; International Relations; Law", "application_start": "February",
         "tuition_fee": "€7,000–€14,000", "documents": "Passport; Diploma; Transcript; Motivation Letter",
         "website": "https://www.sciencespo.fr/en/"},

        {"name": "KU Leuven", "country": "Belgium", "city": "Leuven",
         "faculties": "Engineering; Science; Economics; Law", "application_start": "February",
         "tuition_fee": "€1,000–€4,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.kuleuven.be/kuleuven/"},

        {"name": "Ghent University", "country": "Belgium", "city": "Ghent",
         "faculties": "Engineering; Bioscience; Medicine", "application_start": "February",
         "tuition_fee": "€1,000–€4,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.ugent.be/en"},

        {"name": "University of Vienna", "country": "Austria", "city": "Vienna",
         "faculties": "Humanities; Law; Social Sciences", "application_start": "March",
         "tuition_fee": "€1,500 per year", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.univie.ac.at/en/"},

        {"name": "Vienna University of Technology", "country": "Austria", "city": "Vienna",
         "faculties": "Engineering; Computer Science", "application_start": "March",
         "tuition_fee": "€1,500 per year", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.tuwien.at/en/"},

        {"name": "Charles University", "country": "Czech Republic", "city": "Prague",
         "faculties": "Medicine; Law; Humanities", "application_start": "February",
         "tuition_fee": "€4,000–€10,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://cuni.cz/UKEN-1.html"},

        {"name": "University of Warsaw", "country": "Poland", "city": "Warsaw",
         "faculties": "Law; Economics; Social Sciences", "application_start": "March",
         "tuition_fee": "€3,000–€6,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://en.uw.edu.pl/"},

        {"name": "Jagiellonian University", "country": "Poland", "city": "Krakow",
         "faculties": "Medicine; Law; Humanities", "application_start": "March",
         "tuition_fee": "€3,000–€6,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://en.uj.edu.pl/en_GB/start"},

        {"name": "Sapienza University of Rome", "country": "Italy", "city": "Rome",
         "faculties": "Engineering; Medicine; Law; Humanities", "application_start": "April",
         "tuition_fee": "€2,000–€4,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.uniroma1.it/en"},

        {"name": "University of Bologna", "country": "Italy", "city": "Bologna",
         "faculties": "Law; Economics; Engineering", "application_start": "April",
         "tuition_fee": "€2,000–€3,500", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.unibo.it/en"},

        {"name": "Politecnico di Milano", "country": "Italy", "city": "Milan",
         "faculties": "Engineering; Architecture; Design", "application_start": "April",
         "tuition_fee": "€3,000–€4,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.polimi.it/en/"},

        {"name": "University of Barcelona", "country": "Spain", "city": "Barcelona",
         "faculties": "Humanities; Medicine; Economics", "application_start": "March",
         "tuition_fee": "€3,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.ub.edu/web/ub/en/"},

        {"name": "Autonomous University of Madrid", "country": "Spain", "city": "Madrid",
         "faculties": "Science; Law; Economics", "application_start": "March",
         "tuition_fee": "€3,000", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.uam.es/"},

        {"name": "University of Copenhagen", "country": "Denmark", "city": "Copenhagen",
         "faculties": "Science; Health; Social Sciences", "application_start": "January",
         "tuition_fee": "Free for EU students", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.ku.dk/english/"},

        {"name": "Aarhus University", "country": "Denmark", "city": "Aarhus",
         "faculties": "Business; Engineering; Arts", "application_start": "January",
         "tuition_fee": "Free for EU students", "documents": "Passport; Diploma; Transcript",
         "website": "https://international.au.dk/"},

        {"name": "Stockholm University", "country": "Sweden", "city": "Stockholm",
         "faculties": "Science; Law; Humanities", "application_start": "January",
         "tuition_fee": "Free for EU students", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.su.se/english/"},

        {"name": "Uppsala University", "country": "Sweden", "city": "Uppsala",
         "faculties": "Engineering; Medicine; Humanities", "application_start": "January",
         "tuition_fee": "Free for EU students", "documents": "Passport; Diploma; Transcript",
         "website": "https://www.uu.se/en/"}
    ]

    for uni in universities:
        u = University(
            name=uni["name"],
            country=uni["country"],
            city=uni["city"],
            faculties=uni["faculties"],
            application_start=uni["application_start"],
            tuition_fee=uni["tuition_fee"],
            documents=uni["documents"],
            website=uni.get("website", "")
        )
        db.session.add(u)
    db.session.commit()
    print("✅ Universities imported successfully")

# =====================
# ROUTES
# =====================

# Home page
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
def home():
    country = request.args.get('country')
    faculty = request.args.get('faculty')

    # Base query
    query = University.query

    if country:
        query = query.filter_by(country=country)
    if faculty:
        query = query.filter(University.faculties.like(f"%{faculty}%"))

    universities1 = query.all()

    # Unique countries & faculties for dropdowns
    countries = [c[0] for c in db.session.query(University.country).distinct().all()]

    # Faculties: split all, flatten and unique
    all_faculties = []
    for u in University.query.all():
        all_faculties.extend([f.strip() for f in u.faculties.split(";")])
    faculties = sorted(list(set(all_faculties)))

    return render_template(
        'home.html',
        universities=universities1,
        countries=countries,
        faculties=faculties,
        selected_country=country,
        selected_faculty=faculty
    )

# Universities list
@app.route('/universities')
def universities():
    universities1 = University.query.all()
    return render_template(
        "universities.html",
        universities=universities1,
        search_country="",
        search_faculty=""
    )

# University detail (empty for now)
@app.route('/university_detail/<int:uni_id>')
def university_detail(uni_id):
    university = University.query.get_or_404(uni_id)
    return render_template('university_detail.html', university=university)


# Add university (login required)
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_university():
    if request.method == 'POST':
        uni = University(
            name=request.form['name'],
            country=request.form['country'],
            city=request.form['city'],
            faculties=request.form['faculties'],
            application_start=request.form['application_start'],
            tuition_fee=request.form['tuition_fee'],
            documents=request.form['documents']
        )
        db.session.add(uni)
        db.session.commit()
        flash("University added successfully!", "success")
        return redirect(url_for('universities'))

    return render_template('add_university.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(
            request.form['password'],
            method='pbkdf2:sha256'
        )

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
        return redirect(url_for('login'))
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

# =====================
# APPLY NOW FORM HANDLING
# =====================
@app.route('/apply/<int:uni_id>', methods=['POST'])
def apply(uni_id):
    university = University.query.get_or_404(uni_id)

    # Form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Save to database
    application = Application(
        university_id=uni_id,
        name=name,
        email=email,
        message=message
    )
    db.session.add(application)
    db.session.commit()

    flash(f'Thank you, {name}! Your application to {university.name} has been submitted.', 'success')

    return redirect(url_for('university_detail', uni_id=uni_id))

# RUN APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        import_universities()
    app.run(host = "0.0.0.0")

