from itsdangerous import URLSafeTimedSerializer as Serializer
from bookshelf import db, login_manager, app
from datetime import datetime, timezone
from flask_login import UserMixin

#function to find user by id

@login_manager.user_loader
def load_user(customer_id):
    return Customer.query.get(int(customer_id))



#book model for db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher= db.Column(db.String, nullable=False)
    Image = db.Column(db.String)
    Image2 = db.Column(db.String)
    Image3 = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Book('{self.isbn}', '{self.title}', '{self.author}', '{self.year}', '{self.publisher}','{self.Image}','{self.Image2}','{self.Image3}')"


#user model for db

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    review = db.relationship('Review', backref='reviewer',lazy=True)
    

     #creating a token which accepts the secret key and also we can set the expiration of the same
    def get_reset_token(self, expires_sec=1800):  #1800 seconds is 30 minutes
        s = Serializer(app.config['SECRET_KEY'])
        # URLSafeTimedSerializer returns a str in modern itsdangerous
        return s.dumps({'customer_id': self.id})

    @staticmethod         #don't accept the self as the arg insted accept token as arg
    #verify the token
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            customer_id = s.loads(token, max_age=expires_sec)['customer_id']
        except:
            return None
        return Customer.query.get(customer_id)
    
    def __repr__(self):
        return f"Customer('{self.username}', '{self.email}', '{self.image_file}')"

#review model for db

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    comment = db.Column(db.Text, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)


    def __repr__(self):
        return f"Review('{self.rating}', '{self.date_posted}', '{self.comment}' )"