import os
import sys

from sqlalchemy import and_, or_
sys.path.append(os.getcwd())

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from auth.password_handler import get_password_hash, verify_password
from database.models import *
from database.schemas import *
from database.utils import create_timestamp


############################################################################
###### USER
############################################################################

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_email(db: Session, req_email: str):
    return db.query(User).filter_by(email = req_email).first()

def register_user(db: Session, new_user: UserRegisterSchema):
    hashed_password = get_password_hash(new_user.password)
    create_user = User(
        email = new_user.email,
        hashed_password = hashed_password,
        is_employee = new_user.is_employee
    )
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
    return create_user

def login_user(db: Session, login_info: UserLoginSchema):
    pass

def update_password(db: Session, db_user: User, new_password: str):    
    hashed_password = get_password_hash(new_password)
    db_user.hashed_password = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    
def is_email_already_registered(db: Session, email: str):
    db_user = get_user_by_email(db, email)
    if db_user:
        return True
    else:
        return False
    
def authenticate_user(db:Session, email: str, password: str):
    db_user = get_user_by_email(db, email)
    if db_user:
        return verify_password(password, db_user.hashed_password)
    else:
        return False

def update_email(db: Session, db_user: User, new_email: str):
    db_user.email = new_email
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def remove_current_user(db: Session, db_user: User):
    check = db.query(User).filter_by(id = db_user.id).delete()
    if check != 0:
        db.commit()
        return True
    else:
        return False
    
############################################################################
###### BOOK
############################################################################
    
def get_all_books(db: Session, req_limit: int = 100):
    return db.query(Book).limit(limit=req_limit).all()

def get_book_by_isbn(db: Session, req_isbn: str):
    return db.query(Book).filter_by(isbn = req_isbn).first()

def get_books_from_author(db: Session, req_author: str, req_limit: int = 100):
    return db.query(Book).filter_by(author = req_author).limit(limit=req_limit).all()

def delete_book_by_isbn(db: Session, req_isbn: str):
    db.query(Book).filter_by(isbn = req_isbn).delete()
    db.commit()
    return {"message": "book with info remove"}

def add_new_book(db: Session, book: BookBaseSchema):
    db_book = Book(
        title = book.title,
        author = book.author,
        isbn = book.isbn
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return db_book

def update_book_title(db: Session, db_book: Book, new_title: str):
    db_book.title = new_title
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return db_book

def does_book_exist(db: Session, isbn: str):
    db_book = get_book_by_isbn(isbn)
    if db_book:
        return True
    else:
        return False

############################################################################
###### BOOKING
############################################################################

def get_all_bookings(db: Session, limit: int = 100):
    return db.query(Booking).limit(limit).all()

def get_all_booking_of_current_user(db: Session, user_id: int):
    return db.query(Booking).filter_by(user_id= user_id).all()

def get_all_booking_of_book(db: Session, book_id: int):
    return db.query(Booking).filter_by(book_id= book_id).all()

def book_has_booking_in_timerange(db: Session, booking: BookingBaseSchema, book_id: int):
    from_timestamp = create_timestamp(booking.from_date)
    to_timestamp = create_timestamp(booking.to_date)

    if (to_timestamp - from_timestamp) < 0.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end date is before start date. "
        )
        
    cond1 = and_(to_timestamp >= Booking.from_timestamp, to_timestamp < Booking.to_timestamp)
    cond2 = and_(from_timestamp >= Booking.from_timestamp, from_timestamp < Booking.to_timestamp)

    bookings = db.query(Booking).filter_by(book_id = book_id).filter(or_(cond1, cond2)).all()
    
    if bookings:
        return True
    else:
        return False

def add_new_booking(db: Session, booking: BookingBaseSchema, book_id: int, user_id: int):
    db_booking = Booking(
        from_timestamp = create_timestamp(booking.from_date),
        to_timestamp = create_timestamp(booking.to_date),
        
        book_id = book_id,
        user_id = user_id   
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking