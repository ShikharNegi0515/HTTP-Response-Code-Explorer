from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

BASE_IMAGE_URL = "https://http.dog/"


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    response_codes = db.Column(db.Text, nullable=False)  # Comma-separated codes


def get_image_url(response_code):
    return f"https://http.dog/{response_code}.jpg"



@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('search'))
        else:
            return "Invalid credentials"
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        filter_query = request.form['filter']
        matching_codes = filter_response_codes(filter_query)
        results = [
            {
                "code": code,
                "image_url": get_image_url(code)
            }
            for code in matching_codes
        ]
        return render_template('search.html', response_codes=results)

    # On GET request, render the page without results
    return render_template('search.html', response_codes=[])


VALID_RESPONSE_CODES = [
    "100", "101", "102", "103", "200", "201", "202", "203", "204", "205", "206", "207",
    "208", "218", "226", "300", "301", "302", "303", "304", "305", "306", "307", "308",
    "400", "401", "402", "403", "404", "405", "406", "407", "408", "409", "410", "411",
    "412", "413", "414", "415", "416", "417", "418", "419", "420", "421", "422", "423",
    "424", "425", "426", "428", "429", "430", "431", "440", "444", "449", "450", "451",
    "460", "463", "464", "494", "495", "496", "497", "498", "499", "500", "501", "502",
    "503", "504", "505", "506", "507", "508", "509", "510", "511", "520", "521", "522",
    "523", "524", "525", "526", "527", "529", "530", "561", "598", "599", "999"
]

def filter_response_codes(query):
    if query.endswith('xx'):
        prefix = query[:-2]
        return [code for code in VALID_RESPONSE_CODES if code.startswith(prefix)]
    elif query.endswith('x'):
        prefix = query[:-1]
        return [code for code in VALID_RESPONSE_CODES if code.startswith(prefix)]
    else:  # Exact match
        return [query] if query in VALID_RESPONSE_CODES else []



@app.route('/save_list', methods=['POST'])
def save_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    response_codes = request.form.getlist('response_codes')
    response_codes_str = ','.join(response_codes)
    new_list = List(name=name, response_codes=response_codes_str)
    db.session.add(new_list)
    db.session.commit()
    return redirect(url_for('lists'))


@app.route('/lists')
def lists():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    saved_lists = List.query.all()
    return render_template('lists.html', saved_lists=saved_lists)


@app.route('/delete_list/<int:list_id>')
def delete_list(list_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    list_to_delete = List.query.get_or_404(list_id)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('lists'))


@app.route('/edit_list/<int:list_id>', methods=['GET', 'POST'])
def edit_list(list_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    list_item = List.query.get_or_404(list_id)
    if request.method == 'POST':
        list_item.name = request.form['name']
        list_item.response_codes = ','.join(request.form.getlist('response_codes'))
        db.session.commit()
        return redirect(url_for('lists'))
    response_codes = list_item.response_codes.split(',')
    return render_template('edit_list.html', list_item=list_item, response_codes=response_codes)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
