from flask import Flask, flash, render_template, request, redirect, url_for
import mysql.connector
from wtforms import Form, BooleanField, StringField, PasswordField, validators



app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'library'
app.config['MYSQL_HOST'] = 'localhost'
app.secret_key = "flaskproje123*"

mysql = mysql.connector.connect(
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    host=app.config['MYSQL_HOST'],
    database=app.config['MYSQL_DB']
)



@app.route("/")
def home_page():
    cursor = mysql.cursor()
    cursor.execute("show tables")
    data = cursor.fetchall()
    return render_template("home.html", data = data)

class SearchForm(Form):
    book_title = StringField('book_title', [validators.Length(min = 1, max = 500)])
    

@app.route("/search-book", methods = ['GET', 'POST'])
def search_page():
    cursor = mysql.cursor()
    form = SearchForm(request.form)
    
    if request.method == 'POST' and form.validate():
        name = form.book_title.data
        search_option = request.form.get('search_option')
        if search_option == 'title':
            query = "SELECT * FROM books WHERE books.book_title LIKE %s"
        elif search_option == 'isbn':
            query = "SELECT * FROM books WHERE books.ISBN LIKE %s"
        else:
            query = "SELECT * FROM books WHERE books.book_title LIKE %s"

        cursor.execute(query, ('%' + name + '%',))
        data = cursor.fetchall()
        return render_template("book-search.html", data=data)

    return render_template("book-search.html")

def add_book():
    pass
def remove_book():
    pass
def edit_book():
    pass




class BorrowForm(Form):
    user_name = StringField('user_name', [validators.Length(min = 1, max = 500)])

@app.route('/search-borrowing', methods = ["GET", "POST"])
def show_borrowing_records():
    cursor = mysql.cursor()
    form = BorrowForm(request.form)
    if request.method == 'POST' and form.validate():
        user_name = form.user_name.data
        query = '''
        Select borrow_id, users.user_name, borrows.ISBN, borrow_date, return_date 
        from borrows, users, books 
        where borrows.ISBN = Books.ISBN and borrows.user_id = users.user_id and users.user_name = %s;
        '''
        cursor.execute(query, (user_name,))
        data = cursor.fetchall()
        if not data:
            flash(f"No borrowing records for {user_name}, Search for another user", 'error')
            return render_template("search-borrowing.html", form = form)
        return render_template("show-borrowing-records.html", data=data)
    return render_template("search-borrowing.html", form = form)
    
@app.route('/show-popular-books', methods = ["GET"])
def most_popular_books_list():
    query = '''
        Select books.book_title, books.ISBN,authors.name_surname, books.publisher, books.year_of_publication,
        books.image_URL_M, count(*) as total_count
        From books, borrows, authors, writtenby
        Where books.ISBN = borrows.ISBN and books.ISBN = writtenby.ISBN and writtenby.author_id = authors.author_id
        Group By books.ISBN, authors.name_surname
        Order By total_count DESC
        Limit 10;
        '''
    cursor = mysql.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("show-popular-books.html", data = data)

@app.route('/show-popular-authors', methods = ["GET"]) 
def most_popular_author_list():
    query = '''
        Select authors.name_surname, count(*) as total_count
        From borrows, authors, writtenby
        Where borrows.ISBN = writtenby.ISBN and writtenby.author_id = authors.author_id
        Group by authors.name_surname
        Order by total_count DESC
        Limit 10;
    '''
    cursor = mysql.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("show-popular-authors.html", data = data)

class IssueBookForm(Form):
    book_title = StringField('book_title', [validators.Length(min=1, max=500)])
    username = StringField('Username', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired()])

@app.route("/issue-book", methods=['GET', 'POST'])
def issue_book():
    cursor = mysql.cursor()
    form = IssueBookForm(request.form)
    book_title = request.args.get('book_title', '')
    selected_book = {}
    if book_title:
        cursor.execute("SELECT * FROM books WHERE book_title LIKE %s", ('%' + book_title + '%',))
        data = cursor.fetchall()
        if data:
            selected_book = data[0]
    if request.method == 'POST' and form.validate():
        flash('Book issued', 'success')
        return redirect(url_for('home_page'))
    print("Selected Book:", selected_book)
    return render_template("issue-book.html", form=form, selected_book=selected_book)



def return_book():
    pass




class AddUserForm(Form):
    """username = StringField('Username', [validators.Length(min=1, max=50)])
    password = PasswordField('Password', [validators.Length(min=6, max=50)])
    """
    id = StringField('User ID', [validators.Length(min=1, max=100000)])

    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Optional(), validators.Regexp('^\d+$', message='Age must be a number')])
   


@app.route("/add-user", methods=['GET', 'POST'])
def add_user():
    cursor = mysql.cursor()
    form = AddUserForm(request.form)
    if request.method == 'POST' and form.validate():
        id = form.id.data
        address = form.address.data
        age = form.age.data
        query = "INSERT INTO users (user_id, address, age) VALUES (%s, %s, %s)"
        cursor.execute(query, (id, address, age))
        mysql.commit()
        return redirect(url_for('home_page'))
    return render_template("add-user.html", form=form)


class RemoveUserForm(Form):
    id = StringField('User ID', [validators.Length(min=1, max=100000)])


@app.route("/remove-user", methods=['GET', 'POST'])
def remove_user():
    form = RemoveUserForm(request.form)
    if request.method == 'POST' and form.validate():
        cursor = mysql.cursor()
        user_id = form.id.data
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        mysql.commit()
        #return redirect(url_for('home_page'))
    return render_template("remove-user.html", form=form)


"""
@app.route("/edit-user/<username>", methods=['GET', 'POST'])
def edit_user(username):
    form = AddUserForm(request.form)
    if request.method == 'POST' and form.validate():
        new_id = form.id.data
        new_address = form.address.data
        new_age = form.age.data
        # Example: cursor.execute("UPDATE users SET username = %s, password = %s WHERE username = %s", (new_username, new_password, username))
        cursor.execute("UPDATE users SET user_id = %s, address = %s, age = %s WHERE id = %s", (new_id, new_address, new_age, id))
        mysql.commit()
        return redirect(url_for('home_page'))
    # Fetch the existing user data and pre-fill the form fields
    # Example: cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    cursor.execute("SELECT * FROM users WHERE id = %s", (id))
    # existing_user_data = cursor.fetchone()
    existing_user_data = cursor.fetchone()
    # form.username.data = existing_user_data['username']
    form.id.data = existing_user_data['user_id']
    # form.password.data = existing_user_data['password']
    return render_template("edit-user.html", form=form)

"""

class EditUserForm(Form):
    user_id = StringField('User ID', [validators.Length(min=1, max=100000)])
    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Optional(), validators.Regexp('^\d+$', message='Age must be a number')])

@app.route("/edit-user", methods=['GET', 'POST'])
def edit_user():
    cursor = mysql.cursor()
    form = EditUserForm(request.form)
    user = None  # Initialize user as None

    if request.method == 'POST' and form.validate():
        user_id = form.user_id.data
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()  # Fetch user data

        if user:
            # If user found, update user data
            address = form.address.data
            age = form.age.data
            cursor.execute("UPDATE users SET address = %s, age = %s WHERE user_id = %s", (address, age, user_id))
            mysql.commit()
            return redirect(url_for('home_page'))
        else:
            # If user not found, show an error message
            error_message = f"User with ID {user_id} not found."

    return render_template("edit-user.html", form=form, user=user, error_message=error_message)


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


if __name__ == "__main__":
    app.run(debug=True)
    show_borrowing_records()