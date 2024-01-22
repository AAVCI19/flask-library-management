from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from wtforms import Form, BooleanField, StringField, PasswordField, validators



app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'library'
app.config['MYSQL_HOST'] = 'localhost'

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
    print(form.validate())
    print(form.book_title)
    if request.method == 'POST' and form.validate():
        name = form.book_title.data
        query = "SELECT * FROM books WHERE books.book_title Like %s"
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





class AddUserForm(Form):
    userName = StringField('userName', [validators.Length(min=1, max=100)])
    userPassword = StringField('userPassword', [validators.Length(min=1, max=100)])
    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Length(min=1, max=200)])


@app.route("/add-user", methods=['GET', 'POST'])
def add_user():
    cursor = mysql.cursor()
    form = AddUserForm(request.form)

    if request.method == 'POST' and form.validate():
        userName = form.userName.data
        userPassword = form.userPassword.data
        address = form.address.data
        age = form.age.data

        query = "INSERT INTO users (user_name, user_password, address, age) VALUES (%s,%s, %s, %s)"
        cursor.execute(query, (userName, userPassword, address, age))  
        mysql.commit()

        return redirect(url_for('home_page'))
    return render_template("add-user.html", form=form)





class RemoveUserForm(Form):
    userName = StringField('userName', [validators.Length(min=1, max=100)])


@app.route("/remove-user", methods=['GET', 'POST'])
def remove_user():
    form = RemoveUserForm(request.form)
    if request.method == 'POST' and form.validate():
        cursor = mysql.cursor()
        userName = form.userName.data
        cursor.execute("DELETE FROM users WHERE user_name = %s", (userName,))
        mysql.commit()
        return redirect(url_for('home_page'))
    return render_template("remove-user.html", form=form)



class EditUserForm(Form):
    userName = StringField('userName', [validators.Length(min=1, max=100)])
    userPassword = StringField('userPassword', [validators.Length(min=1, max=100)])
    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Length(min=1, max=200)])



@app.route("/edit-user", methods=['GET', 'POST'])
def edit_user():
    cursor = mysql.cursor()
    form = EditUserForm(request.form)
    user = None  # Initialize user as None
    error_message = None  # Initialize error_message as None

    if request.method == 'POST' and form.validate():
        newUserName = form.userName.data
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (newUserName,))
        user = cursor.fetchone()  # Fetch user data

        if user:
            newuserPassword = form.userPassword.data
            newAddress = form.address.data
            newAge = form.age.data

            cursor.execute("UPDATE users SET user_password = %s, address = %s, age = %s WHERE user_name = %s", (newuserPassword, newAddress, newAge, newUserName))
            mysql.commit()
            return redirect(url_for('home_page'))
        else:
            # If user not found, show an error message
            error_message = f"User with name {newUserName} not found."

    return render_template("edit-user.html", form=form, user=user, error_message=error_message)


def issue_book():
    pass
def return_book():
    pass



if __name__ == "__main__":
    app.run(debug=True)