"""Database models for authors and books in the BookAlchemy app."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Author(db.Model):
    """Represent an author stored in the library database."""

    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        """Return a developer-friendly representation of the author."""
        return f"<Author {self.name}>"

    def __str__(self):
        """Return the author's display name."""
        return self.name


class Book(db.Model):
    """Represent a book stored in the library database."""

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("authors.id"),
        nullable=False,
    )

    author = db.relationship(
        "Author",
        backref=db.backref("books", lazy=True),
    )

    def __repr__(self):
        """Return a developer-friendly representation of the book."""
        return f"<Book {self.title}>"

    def __str__(self):
        """Return the book's display title."""
        return self.title
