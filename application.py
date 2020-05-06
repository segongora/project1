import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

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

def loged_in():

	loged_in = False

	if session.get('user') is None:
		loged_in = False
	else:
		loged_in = True

	return loged_in

@app.route("/")
def index():
	books = db.execute("SELECT * FROM books LIMIT 100")

	return render_template("index.html", loged_in=loged_in(), books=books)


@app.route("/book/<string:isbn>")
def book(isbn):

	book = db.execute("SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).fetchone()

	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()

	authors = []
	Reviewed=False
	for review in reviews:
		authors.append(db.execute("SELECT * FROM users WHERE id = :author_id", {"author_id": review.user_id}).fetchone())
		if session.get('user').id == review.user_id:
			Reviewed = True

	ratings = requests.get("https://www.goodreads.com/book/review_counts.json",
	params={"key": "ThoUB9JBXDw1owggqq88A", "isbns": book.isbn}).json()

	if ratings is None:
		ratings['books'][0]['work_ratings_count'] = "No review count available."
		ratings['books'][0]['average_rating'] = "No average rating available."

	return render_template("book.html", loged_in=loged_in(), book=book,
	ratings=ratings, reviews=reviews, authors=authors, Reviewed=Reviewed, user=session.get('user'))

@app.route("/search", methods=["POST"])
def search():
	m = request.form.get("search")
	m = "%" + m + "%"
	books = db.execute("SELECT * FROM books WHERE lower(title) LIKE :m OR lower(author) LIKE :m OR lower(isbn) LIKE :m",
	{"m":m}).fetchall()

	m = m.replace('%', '')

	return render_template("search.html", m=m, books=books)

@app.route("/review/<string:isbn>", methods=["POST"])
def review(isbn):

	rating = request.form.get("rating")
	text = request.form.get("review")

	user = session.get('user')
	user_id = int(user.id)

	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	book_id = int(book.id)

	db.execute("INSERT INTO reviews (text, user_id, rating, book_id) VALUES(:text, :user_id, :rating, :book_id)",
	{"text": text, "user_id": user_id, "rating": rating, "book_id": book_id})
	db.commit()

	return redirect(url_for('book', isbn=book.isbn))


@app.route("/access")
def access():
	if session.get('user') is None:
		return render_template("access.html")
	else:
		return redirect(url_for('profile'))

# segongora -
# segongora2 - sergio
@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username").strip()
		password = request.form.get("password")

		user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
		if user and check_password_hash(user.password, password):
			session['user'] = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
			return redirect(url_for('profile'))

		session['message'] = "Login credentials incorrect. Try again."
		return redirect(url_for('error'))

@app.route("/signup", methods=["POST"])
def signup():

	if request.method=="POST":
		name = request.form.get("name").title()
		username = request.form.get("username").strip()
		password = request.form.get("password")
		pw_hash = generate_password_hash(password, method="sha256")

		if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).rowcount == 1:
			session['message'] = 'There is already a user with that username. Try other'
			return redirect(url_for('error'))

		else:
			db.execute("INSERT INTO users (name, username, password) VALUES (:name, :username, :pw_hash)",
			{"name": name,"username": username, "pw_hash": pw_hash})
			db.commit()
			session['user'] = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
			return redirect(url_for('profile'))

		session['message'] = "Something weird just happened. If the problem persists try again later."
		return redirect(url_for('error'))

@app.route("/profile")
def profile():
	user = session.get('user')
	reviews = db.execute("SELECT * FROM reviews WHERE user_id = :id", {"id": user.id}).fetchall()

	reviewed_books = []
	for review in reviews:
		reviewed_books.append(db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": review.book_id}).fetchone())

	return render_template("profile.html", user=user, reviews=reviews, reviewed_books=reviewed_books)

@app.route("/edit", methods=["POST"])
def edit_profile():
	name = request.form.get("name")
	username = request.form.get("username")
	password = request.form.get("password")
	pw_hash = generate_password_hash(password, method="sha256")
	if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).rowcount == 0:

		db.execute("UPDATE users SET name = :name, username = :username, password = :password WHERE id = :id",
		{"name": name, "username": username, "password": pw_hash, "id": session.get('user').id})
		db.commit()

		session['user'] = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
		return redirect(url_for('profile'))



@app.route("/logout")
def logout():
	# remove the username from the session if it's there
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	if book is None:
		return jsonify({"error": "Invalid ISBN. There is no book with that ISBN."}), 422

	ratings = requests.get("https://www.goodreads.com/book/review_counts.json",
	params={"key": "ThoUB9JBXDw1owggqq88A", "isbns": isbn}).json()
	if ratings is None:
		ratings['books'][0]['work_ratings_count'] = "No review count available."
		ratings['books'][0]['average_rating'] = "No average rating available."

	return jsonify({
	"title": book.title,
	"author": book.author,
	"year": book.year,
	"isbn": book.isbn,
	"review count": ratings['books'][0]['work_ratings_count'],
	"rating average": ratings['books'][0]['average_rating']})


@app.route("/error")
def error():
	message = session['message']
	return render_template("error.html", message=message)

if __name__ == '__main__':
    app.run()
