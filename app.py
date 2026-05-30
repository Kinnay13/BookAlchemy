"""Flask routes and application setup for the BookAlchemy library app."""

import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, "data/library.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def parse_date(date_value):
    """Convert a form date string into a date object."""
    if not date_value:
        return None
    return datetime.strptime(date_value, "%Y-%m-%d").date()


def parse_int(int_value):
    """Convert an optional form value into an integer."""
    if not int_value:
        return None
    return int(int_value)


@app.route("/")
def home():
    """Render the library home page with search and sorting options."""
    sort_by = request.args.get("sort", "title")
    search_query = request.args.get("search", "").strip()
    deleted = request.args.get("deleted") == "1"

    books_query = Book.query

    if search_query:
        books_query = books_query.filter(Book.title.like(f"%{search_query}%"))

    if sort_by == "author":
        books = (
            books_query
            .join(Author)
            .order_by(Author.name, Book.title)
            .all()
        )
    else:
        books = books_query.order_by(Book.title).all()

    return render_template(
        "home.html",
        books=books,
        deleted=deleted,
        search_query=search_query,
        sort_by=sort_by,
    )


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Render the author form and save submitted authors."""
    success = False

    if request.method == "POST":
        author = Author(
            name=request.form["name"],
            birth_date=parse_date(request.form["birthdate"]),
            date_of_death=parse_date(request.form.get("date_of_death")),
        )
        db.session.add(author)
        db.session.commit()
        success = True

    return render_template("add_author.html", success=success)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Render the book form and save submitted books."""
    success = False
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        book = Book(
            isbn=request.form["isbn"],
            title=request.form["title"],
            publication_year=parse_int(request.form.get("publication_year")),
            author_id=request.form["author_id"],
        )
        db.session.add(book)
        db.session.commit()
        return redirect(url_for("add_book", success=1))

    success = request.args.get("success") == "1"
    return render_template("add_book.html", authors=authors, success=success)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a book and remove its author when no books remain."""
    book = Book.query.get_or_404(book_id)
    author = book.author
    author_id = book.author_id

    db.session.delete(book)
    db.session.flush()

    has_other_books = Book.query.filter_by(author_id=author_id).first()
    if author is not None and not has_other_books:
        db.session.delete(author)

    db.session.commit()

    return redirect(url_for("home", deleted=1))


if __name__ == "__main__":
    app.run(debug=True)
