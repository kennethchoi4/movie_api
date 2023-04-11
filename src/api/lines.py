from fastapi import APIRouter, HTTPException
from enum import ENUM 
from src import database as db

router = APIRouter()

"""
functions for lines.py
list conversation -> display all of the lines of a conversation 
write out the first line of each conversation character is part of (searched by character)

"""


# creating the database object 
data = db.db()

#@router.get("/characters/{id}", tags=["characters"])

