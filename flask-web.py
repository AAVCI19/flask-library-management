from flask import Flask, flash, render_template, request, redirect, url_for
import mysql.connector
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from datetime import date 


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

@app.route('/show-borrowing-records', methods = ["GET", "POST"])
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
        return render_template("search-borrowing.html", data=data)
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
    username = StringField('Username', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired()])

@app.route("/issue-book", methods=['GET', 'POST'])
def issue_book():
    form = IssueBookForm(request.form)
    book_title = request.args.get('book_title', '')
    selected_book = {}
    no_of_copies = 0
    isbn = ""
    user_id = 0
    borrow_date = date.today()
    if book_title:
        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM books WHERE book_title LIKE %s", ('%' + book_title + '%',))
        data = cursor.fetchall()
        if data:
            selected_book = data[0]
            no_of_copies = selected_book[4]
            isbn = selected_book[0]

    print(f"number of copies {no_of_copies}")    
    print(f"isbn {isbn}")    

    if request.method == 'POST' and form.validate():
        print("validate ediyor")
        username = form.username.data
        password = form.password.data
        cursor1 = mysql.cursor()
        cursor1.execute("Select user_id From users where user_name = %s and user_password = %s", (username, password))
        data = cursor1.fetchall()
        if data:
            user_id = data[0][0]
        
        if(no_of_copies > 0):
            print(f"number of copies {no_of_copies}")    
            print("yes stock")
            cursor2 = mysql.cursor()
            query = '''
                    Select borrow_id from borrows
                    '''
            cursor2.execute(query)
            data = cursor2.fetchall()
            print(data)
            borrow_id = max(data, key=lambda x: x[0])
            borrow_id_int = borrow_id[0] + 1
            cursor3 = mysql.cursor()
            query = '''
                    INSERT INTO borrows (borrow_id, user_id, ISBN, borrow_date) VALUES (%s, %s, %s, %s)
                    '''
            cursor3.execute(query, (borrow_id_int,user_id, isbn, borrow_date))

            cursor4 = mysql.cursor()
            query = '''
                    Update books
                    Set books.no_of_copies = books.no_of_copies  - 1
                    Where ISBN = %s
                    '''
            cursor4.execute(query, (isbn,))
            mysql.commit()

            
        

        flash('Book issued', 'success')
        return redirect(url_for('home_page'))
    
    print("Selected Book:", selected_book)
    return render_template("issue-book.html", form=form, selected_book=selected_book)


class ReturnBookForm(Form):
    isbn = StringField('isbn', [validators.Length(min = 1, max = 20)])


@app.route("/return-book", methods=['GET', 'POST'])
def return_book():
    form = ReturnBookForm(request.form)
    print("hello")
    if request.method == 'POST' and form.validate():
        print("hello")
        isbn = form.isbn.data
        cursor1 = mysql.cursor()
        return_date = date.today()
        query = '''
        Update borrows
        Set return_date = %s, actual_return_date = %s
        Where borrows.ISBN = %s 
        '''
        cursor1.execute(query, (return_date, return_date, isbn))
        cursor2 = mysql.cursor()
        query = '''
        Update books
        Set no_of_copies = no_of_copies + 1
        Where books.ISBN = %s
        '''
        cursor2.execute(query, (isbn,))
        mysql.commit()
        print("succesfully returned book")
        flash('Book successfully returned', 'success')
        return redirect(url_for('home_page'))
    
    return render_template("return-book.html")

class AddUserForm(Form):
    """username = StringField('Username', [validators.Length(min=1, max=50)])
    password = PasswordField('Password', [validators.Length(min=6, max=50)])
    """
    id = StringField('User ID', [validators.Length(min=1, max=100000)])

    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Optional(), validators.Regexp('^\d+$', message='Age must be a number')])
   


@app.route("/add-user", methods=['GET', 'POST'])
def add_user():
    try:
        # Attempt to create a cursor for database operations and an instance of AddUserForm
        cursor = mysql.cursor()
        form = AddUserForm(request.form)

        if request.method == 'POST' and form.validate():
            # Retrieve user data from the form
            userName = form.userName.data
            userPassword = form.userPassword.data
            address = form.address.data
            age = form.age.data

            # Execute an SQL query to insert user data into the database
            query = "INSERT INTO users (user_name, user_password, address, age) VALUES (%s,%s, %s, %s)"
            cursor.execute(query, (userName, userPassword, address, age))
            mysql.commit()

            return redirect(url_for('home_page'))
    except Exception as e:
        return render_template("error.html", error_message=str(e))
    finally:
        cursor.close()

    # Render the add-user.html template with the form
    return render_template("add-user.html", form=form)


class RemoveUserForm(Form):
    id = StringField('User ID', [validators.Length(min=1, max=100000)])


@app.route("/remove-user", methods=['GET', 'POST'])
def remove_user():
    # Initialize cursor variable outside the try block
    cursor = None
    try:
        # Attempt to create an instance of RemoveUserForm
        form = RemoveUserForm(request.form)
        
        if request.method == 'POST' and form.validate():
            cursor = mysql.cursor()
            # Retrieve user name from the form and delete the corresponding user from the database
            userName = form.userName.data
            cursor.execute("DELETE FROM users WHERE user_name = %s", (userName,))
            mysql.commit()

            # Redirect user to the home page
            return redirect(url_for('home_page'))
    except Exception as e:
        return render_template("error.html", error_message=str(e))
    finally:
        if cursor:
            cursor.close()

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
    # Initialize cursor variable outside the try block
    cursor = None
    try:
        # Attempt to create an instance of EditUserForm and initialize variables
        form = EditUserForm(request.form)
        user = None
        error_message = None

        if request.method == 'POST' and form.validate():
            cursor = mysql.cursor()
            # Retrieve user name from the form and query the database to fetch user data
            userName = form.userName.data
            cursor.execute("SELECT * FROM users WHERE user_name = %s", (userName,))
            user = cursor.fetchone()

            # If the user is found, update the user's password, address, and age in the database
            if user:
                new_user_password = form.userPassword.data
                new_address = form.address.data
                new_age = form.age.data

                cursor.execute("UPDATE users SET user_password = %s, address = %s, age = %s WHERE user_name = %s",
                               (new_user_password, new_address, new_age, userName))
                mysql.commit()

                print("User Updated Successfully")
                return redirect(url_for('home_page'))
            else:
                # If the user is not found, set an error message
                error_message = f"User with name {userName} not found."
    except Exception as e:
        return render_template("error.html", error_message=str(e))
    finally:
        if cursor:
            cursor.close()

    return render_template("edit-user.html", form=form, user=user, error_message=error_message)


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route('/show-not-all-borrowed-books', methods = ["GET"]) 
def show_not_all_borrowed_books():
    query = '''
        Select books.book_title, books.ISBN, books.publisher, books.year_of_publication,
        books.image_URL_M, books.no_of_copies - count(borrows.ISBN) as available_copies
        From books 
        Left Join borrows on books.ISBN = borrows.ISBN
        Group By books.ISBN
        Having available_copies > 0 OR available_copies is null
        Limit 100;
    '''
    cursor = mysql.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("show-not-all-borrowed-books.html", data = data)


if __name__ == "__main__":
    app.run(debug=True)
    show_borrowing_records()