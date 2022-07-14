from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import random


db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = 'books'
    __table_args = {'schema': 'public'}

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_user_id = db.Column(db.Integer)
    file_location = db.Column(db.String(255))

    # category = enum
    # TODO: every book to category

    def __init__(self, book_name, uploaded_user_id=None, file_location=None):
        self.book_name = book_name
        self.uploaded_user_id = uploaded_user_id
        self.file_location = file_location


class Page(db.Model):
    __tablename__ = 'pages'
    __table_args = {'schema': 'public'}

    page_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    page_number = db.Column(db.Integer)
    file_location = db.Column(db.String(255))

    def __init__(self, book_id, page_number, file_location):
        self.book_id = book_id
        self.page_number = page_number
        self.file_location = file_location


class ROI(db.Model):
    __tablename__ = 'roi'

    roi_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.page_id'))

    coordinate_x = db.Column(db.Integer)
    coordinate_x_end = db.Column(db.Integer)
    coordinate_y = db.Column(db.Integer)
    coordinate_y_end = db.Column(db.Integer)

    def __init__(self, page_id, coordinate_x, coordinate_x_end, coordinate_y, coordinate_y_end):
        self.page_id = page_id
        self.coordinate_x = coordinate_x
        self.coordinate_x_end = coordinate_x_end
        self.coordinate_y = coordinate_y
        self.coordinate_y_end = coordinate_y_end


class Fragments(db.Model):
    __tablename__ = 'fragments'
    __table_args = {'schema': 'public'}

    fragment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roi_id = db.Column(db.Integer, db.ForeignKey('roi.roi_id'))

    row_number = db.Column(db.Integer)
    word_number = db.Column(db.Integer)

    coordinate_x = db.Column(db.Integer)
    coordinate_x_end = db.Column(db.Integer)
    coordinate_y = db.Column(db.Integer)
    coordinate_y_end = db.Column(db.Integer)

    file_location = db.Column(db.String(255))

    def __init__(self, roi_id, row_number, word_number, coordinate_x, coordinate_x_end,
                 coordinate_y, coordinate_y_end, file_location=None):
        self.roi_id = roi_id
        self.row_number = row_number
        self.word_number = word_number
        self.coordinate_x = coordinate_x
        self.coordinate_x_end = coordinate_x_end
        self.coordinate_y = coordinate_y
        self.coordinate_y_end = coordinate_y_end
        self.file_location = file_location


class Labeling(db.Model):
    __tablename__ = 'labeling'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    fragment_id = db.Column(db.Integer, db.ForeignKey('fragments.fragment_id'))
    user_id = db.Column(db.Integer, nullable=False)

    text = db.Column(db.Text)
    is_skipped = db.Column(db.Boolean)

    def __init__(self, fragment_id, user_id, text, is_skipped):
        self.fragment_id = fragment_id
        self.user_id = user_id
        self.text = text
        self.is_skipped = is_skipped


#  это очень тупо так делать - методы идентичны, нужен какой-то шаблон
def book_upload(book_name, file_location) -> int:
    book = Book(book_name=book_name, file_location=file_location)
    db.session.add(book)
    db.session.commit()
    db.session.refresh(book)
    return book.book_id


def page_upload(book_id, page_number, file_location):
    page = Page(book_id=book_id, page_number=page_number, file_location=file_location)
    db.session.add(page)
    db.session.commit()
    db.session.refresh(page)
    return page.page_id


def roi_upload(page_id, coordinate_x, coordinate_x_end, coordinate_y, coordinate_y_end):
    roi = ROI(page_id=page_id,coordinate_x=coordinate_x, coordinate_x_end=coordinate_x_end,
                         coordinate_y=coordinate_y, coordinate_y_end=coordinate_y_end)
    db.session.add(roi)
    db.session.commit()
    db.session.refresh(roi)
    return roi.roi_id


def fragment_upload(roi_id,row_number, word_number, coordinate_x, coordinate_x_end,
                    coordinate_y, coordinate_y_end, file_location):
    fragment = Fragments(roi_id=roi_id,row_number=row_number, word_number=word_number,
                         coordinate_x=coordinate_x, coordinate_x_end=coordinate_x_end,
                         coordinate_y=coordinate_y, coordinate_y_end=coordinate_y_end,
                         file_location=file_location)
    db.session.add(fragment)
    db.session.commit()
    db.session.refresh(fragment)
    return fragment.fragment_id

# fuck this function
def get_fragments_by_book(book_id: int = None):
    if book_id is None:
        # random choose
        book_ids_list = [i[0] for i in db.session.query(Book.book_id).all()]
        book_id = random.choice(book_ids_list)
    page_id = [i[0] for i in db.session.query(Page.page_id).filter(Page.book_id == book_id).all()]
    fragments = db.session.query(Fragments.file_location).filter(Fragments.page_id.in_(page_id)).all()
    return [fragment[0] for fragment in fragments]


def get_random_fragment():
    pass
    # TODO: get random fragment func
