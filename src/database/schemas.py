from datetime import datetime, date
from typing import List
from pydantic import BaseModel, Field, EmailStr

class UserBaseSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    
class UserLoginSchema(UserBaseSchema):
    class Config:
        json_schema_extra = {
            "user": {
                "email": "max@mustman.de",
                "password" : "qwer1234"
            }
        }
        
class UserRegisterSchema(UserBaseSchema):
    fullname: str | None = None
    is_employee: bool | None = None
    class Config:
        json_schema_extra = {
            "user": {
                "fullname": "max mustman",
                "email": "max@mustman.de",
                "password" : "qwer1234",
                "is_employee": True
            }
        }
        
class BookingBaseSchema(BaseModel):
    from_date: date | None = None
    to_date: date | None = None
    isbn: str | None = None 
    description: str | None = None 
    

class BookBaseSchema(BaseModel):
    isbn: str | None = None
    title: str | None = None
    author: str | None = None
    
class BookBaseListSchema(BaseModel):
    books: List[BookBaseSchema] = []
    class Config:
        json_schema_extra = {
            "example": {
                "books": [
                    {
                        "title": "example title1",
                        "isbn": "asdg123",
                        "author": "author1"
                    },
                                        {
                        "title": "example title2",
                        "isbn": "asdg123",
                        "author": "author2"
                    },
                    {
                        "title": "example title3",
                        "isbn": "asdg123",
                        "author": "author3"
                    }
                ]
            }
        }