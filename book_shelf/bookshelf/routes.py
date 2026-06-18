import os
import secrets
from datetime import datetime, timezone
from PIL import Image  #for re-sizing the images before uploading
from bookshelf import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort, session
from bookshelf.forms import RegistrationForm, LoginForm, UpdateAccountForm, ReviewForm, HomeForm, RequestResetForm, ResetPasswordForm
from bookshelf.models import Book, Customer, Review
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

query = ' ' 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    form = HomeForm()  
    if form.validate_on_submit():
        query = form.search.data or ''
        result = db.session.execute(
    text(""" 
        SELECT isbn, title, author, year FROM book
        WHERE isbn LIKE '%' || :query || '%' COLLATE NOCASE
           OR title LIKE '%' || :query || '%' COLLATE NOCASE
           OR author LIKE '%' || :query || '%' COLLATE NOCASE
           OR CAST(year AS TEXT) LIKE '%' || :query || '%' COLLATE NOCASE
        LIMIT 15
    """),
    {"query": query}
        )
        books = result.fetchall()
        if result.rowcount == 0:
            flash('The Book does not exist', 'info')
            return redirect(url_for('home'))
        return render_template('results.html', books=books)
    return render_template('search.html', title='search', form=form)
    

@app.route('/about')
def about():
    return render_template('about.html',title='About')

#registration from 
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #to store the password hash
        user = Customer(username=form.username.data, email=form.email.data, password=hashed_password) #create user
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created, You are now able to login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Sign Up', form=form)

#login form 

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        if (user) and (bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #to get the 'next' which is added to the browser when you access the account page without logging in 
            return redirect( next_page) if  next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check Email and Password', 'danger')

    return render_template('login.html', title='Login', form=form)

#logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename) #if there is a variable unused then make as undescored
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) #root_path will give the path all the way up to the flaskblog(package) 

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)


    i.save(picture_path)

    return picture_fn

#account
@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data =  current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title="Account", image_file=image_file, form= form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Rest Request', sender='noreply@demo.com', recipients=[user.email])#put your email 
    msg.body = f''' To reset your password, visit the following link:{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

#user restting the pwd through this url
@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Customer.verify_reset_token(token)
    if user is None:
        flash('That is an invalid token or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #to store the password hash
        user.password =  hashed_password
        db.session.commit()
        flash(f'Your password has been updated, You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):
    form = ReviewForm()
    """ Save user review and load same page with reviews updated."""

    if request.method == "POST":
        book_id = db.session.execute(
            text("SELECT id FROM book WHERE isbn = :isbn"),
            {"isbn": isbn}
        )
        bookId = book_id.fetchone()
        bookId = bookId[0]
    
        
        if form.validate_on_submit():
            # Check for user submission (ONLY 1 review/user allowed per book)
            oneUser = db.session.execute(
                text("SELECT * FROM review WHERE customer_id = :customer_id AND book_id = :book_id"),
                {"customer_id": current_user.id, "book_id": bookId}
            ) 
            if oneUser.rowcount == 1:
                flash('You already submitted a review for this book', 'warning')
                return redirect(url_for('home'))

            reviews = Review(rating=form.rating.data, date_posted=datetime.now(timezone.utc), comment=form.comment.data, customer_id=current_user.id, book_id=bookId)
            db.session.add(reviews)
            db.session.commit()

            flash('Your review has been submitted!', 'info')
            return redirect('/book/' + isbn)
    else:

        book_info = db.session.execute(text("SELECT isbn, title, author, year, publisher, Image3 FROM book WHERE isbn = :isbn"),
            {"isbn": isbn})
        bookInfo = book_info.fetchall()

        """ Users reviews """

         # Search book_id by ISBN
        books = db.session.execute(
            text("SELECT id FROM book WHERE isbn = :isbn"),
            {"isbn": isbn}
        )

        # Save id into variable
        book = books.fetchone() 
        book = book[0]

       
        

        results = db.session.execute(
            text(
                "SELECT review.comment, customer.username, review.date_posted, review.customer_id, review.rating "
                "FROM review LEFT JOIN customer ON review.customer_id = customer.id "
                "WHERE review.book_id = :book ORDER BY date_posted DESC"
            ),
            {"book": book}
        ).fetchall()
        




        return render_template("book.html", bookInfo=bookInfo, form=form, legend='Review',results=results)

       
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Use paginate
    paginated_items = Item.query.paginate(page=page, per_page=per_page)

    return render_template('index.html',
                           items=paginated_items.items,
                           page=page,
                           total_pages=paginated_items.pages)





