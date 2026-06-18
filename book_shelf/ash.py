from pathlib import Path
import os
from flask import Flask, session
from bookshelf import app, db

db_path = Path(__file__).resolve().parent / "bookshelfs.db"
print(db_path)


with app.app_context():
    print(db.engine.url)