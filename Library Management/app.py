# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Book, Member, Transaction
from config import Config
from models import db, Book, Member, Transaction
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# Basic home route
@app.route('/')
def home():
    return render_template('base.html')

@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = int(request.form['quantity'])
        rental_fee = float(request.form['rental_fee'])
        new_book = Book(title=title, author=author, quantity=quantity, rental_fee=rental_fee)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('manage_books'))
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/books/update/<int:id>', methods=['POST'])
def update_book(id):
    book = Book.query.get(id)
    book.title = request.form['title']
    book.author = request.form['author']
    book.quantity = int(request.form['quantity'])
    book.rental_fee = float(request.form['rental_fee'])
    db.session.commit()
    flash('Book updated successfully!')
    return redirect(url_for('manage_books'))

@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!')
    return redirect(url_for('manage_books'))

@app.route('/members', methods=['GET', 'POST'])
def manage_members():
    if request.method == 'POST':
        name = request.form['name']
        new_member = Member(name=name)
        db.session.add(new_member)
        db.session.commit()
        flash('Member added successfully!')
        return redirect(url_for('manage_members'))
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/members/update/<int:id>', methods=['POST'])
def update_member(id):
    member = Member.query.get(id)
    member.name = request.form['name']
    db.session.commit()
    flash('Member updated successfully!')
    return redirect(url_for('manage_members'))

@app.route('/members/delete/<int:id>', methods=['POST'])
def delete_member(id):
    member = Member.query.get(id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted successfully!')
    return redirect(url_for('manage_members'))

@app.route('/transactions')
def transactions():
    # Retrieve all transactions and pass them to the template
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)


@app.route('/transactions/issue', methods=['POST'])
def issue_book():
    book_id = request.form['book_id']
    member_id = request.form['member_id']
    
    book = Book.query.get(book_id)
    member = Member.query.get(member_id)
    
    # Check if the book exists
    if not book:
        flash('Book not found. Please check the book ID.')
        return redirect(url_for('manage_books'))

    # Check if the member exists
    if not member:
        flash('Member not found. Please check the member ID.')
        return redirect(url_for('manage_members'))
    
    # Proceed if book exists
    if book.quantity <= 0:
        flash('Book not available in stock!')
        return redirect(url_for('manage_books'))
    
    if member.debt > 500:
        flash('Member debt exceeds Rs.500!')
        return redirect(url_for('manage_members'))
    
    # Reduce book quantity and create transaction
    book.quantity -= 1
    transaction = Transaction(book_id=book_id, member_id=member_id)
    db.session.add(transaction)
    db.session.commit()
    
    flash('Book issued successfully!')
    return redirect(url_for('manage_books'))


@app.route('/transactions/return/<int:id>', methods=['POST'])
def return_book(id):
    transaction = Transaction.query.get(id)
    book = transaction.book
    member = transaction.member
    
    # Assume a flat rental fee
    rental_fee = book.rental_fee
    member.debt += rental_fee
    transaction.return_date = datetime.utcnow()
    transaction.fees_charged = rental_fee
    
    # Increase book quantity
    book.quantity += 1
    db.session.commit()
    
    flash(f'Book returned successfully! Fee charged: Rs.{rental_fee}')
    return redirect(url_for('manage_books'))

@app.route('/books/search', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        search_term = request.form['search_term']
        books = Book.query.filter(
            (Book.title.ilike(f'%{search_term}%')) |
            (Book.author.ilike(f'%{search_term}%'))
        ).all()
        return render_template('books.html', books=books)
    return render_template('books.html')


if __name__ == "__main__":
    app.run(debug=True)
