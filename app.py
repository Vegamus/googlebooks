from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import requests


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
db = SQLAlchemy(app)

class Book(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Book {self.id}: {self.title} by {self.author}>"

@app.route('/', methods=["GET"])
def home():
    return render_template('home.html')

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    new_book = Book(title=data["title"], author=data["author"])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book created", "book": str(new_book)}), 201

@app.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([str(book) for book in books])

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(str(book))

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    book.title = data["title"]
    book.author = data["author"]
    db.session.commit()
    return jsonify({"message": "Book updated", "book": str(book)})

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted", "book": str(book)})

@app.route('/search')
def search():
    author = request.args.get('author', '')
    title = request.args.get('title', '')
    publisher = request.args.get('publisher', '')
    published_year = request.args.get('published_year', '')

    query = ''
    if author:
        query += f'+inauthor:{author}'
    if title:
        query += f'+intitle:{title}'
    if publisher:
        query += f'+inpublisher:{publisher}'
    if published_year:
        query += f'+inpdate:{published_year}'


    api_key = "AIzaSyD4vJr6uxxYfmJQN_6tZmJ87w8U_kHAZlo"  # Replace with your actual API key
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "An error occurred while fetching data from the Google Books API."}), response.status_code

    data = response.json()
    books = []

    for item in data["items"]:
        volume_info = item["volumeInfo"]
        book = {
            "id": item["id"],
            "title": volume_info["title"],
            "authors": volume_info.get("authors", []),
            "publisher": volume_info.get("publisher", ""),
            "publishedDate": volume_info.get("publishedDate", ""),
            "description": volume_info.get("description", ""),
            "pageCount": volume_info.get("pageCount", 0),
            "imageLinks": volume_info.get("imageLinks", {}),
        }
        books.append(book)

    return render_template("search_results.html", books=books)
    return render_template("search_results.html", books=books)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
