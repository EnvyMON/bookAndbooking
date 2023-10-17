# 1:33:06

from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.auth_handler import ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme, extract_email_from_token, create_access_token, is_token_valid
from database.database import get_db, engine, Base
from database import crud
from database.schemas import *

Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

############################################################################
###### USER specific endpoints
############################################################################

@app.get("/users", tags=["user"])
def get_all_users(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.get_all_users(db)

@app.get("/user-by-email", tags=["user"])
def get_user_by_email(req_email: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.get_user_by_email(db, req_email)

@app.post("/register", tags=["user"])
def register_user(create_user: UserRegisterSchema, db = Depends(get_db)):
    if crud.is_email_already_registered(db, create_user.email) == False:
        created_user = crud.register_user(db, create_user)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {
            "email": created_user.email
        }
        token = create_access_token(data=data, expires_delta=access_token_expires)
        return {
            "access_token": token,
            "token_type": "bearer"
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="email is already registered. ",
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.post("/login", tags=["user"])
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    authenticated = crud.authenticate_user(db, form_data.username, form_data.password)
    if authenticated:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {
            "email": form_data.username
        }
        token = create_access_token(data=data, expires_delta=access_token_expires)
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. ",
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.put("/user/change-email", tags=["user"])
def update_email(new_email: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_email = extract_email_from_token(token=token)
    db_user = crud.get_user_by_email(db, current_email)
    if db_user:
        return crud.update_email(db, db_user, new_email)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist. ",
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.put("/user/change-pwd", tags=["user"])
def update_password(new_password: str, old_password: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_email = extract_email_from_token(token=token)
    db_user = crud.get_user_by_email(db, current_email)
    
    if db_user:
        authenticated = crud.authenticate_user(db, db_user.email, old_password)
        if authenticated:
            return crud.update_password(db, db_user, new_password)
        else:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not validate credentials. ",
            headers={"WWW-Authenticate": "Bearer"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist. ",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.delete("/user", tags=["user"])
def delete_current_user(password:str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_email = extract_email_from_token(token=token)
    db_user = crud.get_user_by_email(db, current_email)
    if db_user:
        authenticated = crud.authenticate_user(db, current_email, password) 
        if authenticated:
            if crud.remove_current_user(db, db_user) == True:
                return {"message": "User removed. "}
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials. ",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials. ",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist. ",
            headers={"WWW-Authenticate": "Bearer"}
        )


############################################################################
###### BOOK specific endpoints
############################################################################

@app.get("/books", tags=["book"])
def get_all_books(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.get_all_books(db)

@app.get("/books/{isbn}", tags=["book"])
def get_book_by_isbn(isbn: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.get_book_by_isbn(db, isbn)

@app.get("/books/author/{author}", tags=["book"])
def get_book_by_author(author: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.get_books_from_author(db, author)
 
@app.post("/book/add-single", tags=["book"])
def add_new_book(book: BookBaseSchema, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.add_new_book(db, book)

@app.post("/book/add-list", tags=["book"])
def add_new_books(book_list: BookBaseListSchema, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    for book in book_list:
        crud.add_new_book(db, book)

@app.delete("/book", tags=["book"])
def delete_book_by_isbn(isbn: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.delete_book_by_isbn(db, isbn)

@app.put("/book-title", tags=["book"])
def update_book_title(new_title: str, isbn: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    db_book = crud.get_book_by_isbn(db, isbn)
    if db_book:
        return crud.update_book_title(db, db_book, new_title)
    else:
        raise HTTPException(
        status_code=404,
        detail="Book with ISBN {} does not exist in database".format(isbn),
        headers={"WWW-Authenticate": "Bearer"},
    )

############################################################################
###### BOOKING specific endpoints
############################################################################

@app.get("/booking/all", tags=["booking"])
def get_all_bookings(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    return crud.get_all_bookings(db)

@app.get("/booking/user-bookings", tags=["booking"])
def get_all_bookings_of_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_email = extract_email_from_token(token)
    db_user = crud.get_user_by_email(db, current_email)
    if db_user:
        return crud.get_all_booking_of_current_user(db, db_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist. ",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@app.get("/booking/book-bookings", tags=["booking"])
def get_all_bookings_of_book(isbn: str, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    db_book = crud.get_book_by_isbn(db, isbn)
    if db_book:
        return crud.get_all_booking_of_book(db, db_book.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book does not exist. ",
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.post("/booking/add", tags=["booking"])
def add_single_booking(booking: BookingBaseSchema, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_email = extract_email_from_token(token)
    db_user = crud.get_user_by_email(db, current_email)
    if db_user:
        db_book = crud.get_book_by_isbn(db, booking.isbn)
        if db_book:
            if crud.book_has_booking_in_timerange(db, booking, db_book.id) == True:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book with ISBN is already booked in requested time range. ",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            else:
                return crud.add_new_booking(db, booking, db_book.id, db_user.id) 
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book does not exist. ",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist. ",
            headers={"WWW-Authenticate": "Bearer"}
        )