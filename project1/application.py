import os

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html", wrong_credentials= False)

@app.route("/landing", methods=["POST","GET"])
def landing():
    if session.get("user") is None:
        session["user"]= ""
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        credentials_check = db.execute("SELECT * FROM users WHERE username = :username",
            {"username": name}).fetchone()
        if credentials_check is None or credentials_check[2] != password:
            return render_template("index.html", wrong_credentials= True)
        session["user"] = name
    return render_template("landing.html", name= session["user"],results= None)

@app.route("/register")
def register():
    return render_template("register.html", bad_pass=False, taken_username=False)

@app.route("/registry", methods=["POST"])
def registry():

    new_name = request.form.get("new_name")
    new_pass = request.form.get("new_password")
    if len(new_pass) < 2:
        return render_template("register.html", bad_pass=True, taken_username=False)
    #Check if username exists
    if not db.execute("SELECT * FROM users WHERE username = \'"+new_name+"\'").rowcount == 0:
        return render_template("register.html",bad_pass=False, taken_username=True)
    db.execute("INSERT INTO users (username, password) VALUES (\'"+new_name+"\', \'"+new_pass+"\')")
    db.commit()
    return render_template("success.html")
@app.route("/booksearch", methods=["POST", "GET"])
def booksearch():
    search_value= str(request.form.get("search_value"))
    if search_value.isspace() or search_value == "":
        return render_template("landing.html", name=session["user"], no_result=True, results=None)
    if search_value.isnumeric():
        search_results= db.execute("SELECT id, isbn, title, author, year FROM books WHERE year= "+search_value).fetchall()
    else:
        search_value= search_value.capitalize()
        execute_string= "SELECT id, isbn, title, author, year FROM books WHERE isbn LIKE \'%"+search_value+"%\'  OR title LIKE \'%"+search_value+"\' OR author LIKE \'%"+search_value+"%\'"
        search_results= db.execute(execute_string).fetchall()
    if len(search_results) == 0:
        return render_template("landing.html", name= session["user"], no_result= True, results= search_results)
    keys = ['id',' isbn', 'title', 'author', 'year']
    result_dict = []
    for values in search_results:
        temp_dict= {}
        for i in range(len(values)):

            temp_dict[keys[i]] = values[i]

        result_dict.append(temp_dict)
    #print(result_dict)
    return render_template("landing.html", name= session["user"], results= result_dict)
@app.route("/books/<int:book_id>", methods=["POST","GET"])
def books(book_id):
    book= db.execute("SELECT * FROM books WHERE id= \'"+str(book_id)+"\'").fetchone()
    if book is None:
        return render_template("error.html", message="something is wrong, couldnt find that book id in database")
    keys = ['id','isbn', 'title', 'author', 'year']
    dict = {keys[i]:book[i] for i, _ in enumerate(keys)}
    book = dict
    key = "nTn90wDOHmwT53AyuhZNg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": book['isbn']})

    book['work_ratings_count']  = res.json()['books'][0]['work_ratings_count']
    star = res.json()['books'][0]['average_rating']
    book['average_rating'] = star
    if session.get("rating") is None:
        session["rating"] = 0
    if session.get("notes") is None:
        session["notes"]= ""
    if request.method == "POST":

        rating = request.form.get("user_rating")
        print(rating)
        session["rating"]= rating
        note = request.form.get("note")
        print(note)
        session["notes"]= note
    return render_template("book.html", book=book, rating= session["rating"], note= session["notes"])
