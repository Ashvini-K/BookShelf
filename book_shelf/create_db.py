from bookshelf import app, db
import bookshelf.models  # ensure models are imported

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("bookshelf.db initialized") 