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
    #id = StringField('User ID', [validators.Length(min=1, max=100000)])

    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Optional(), validators.Regexp('^\d+$', message='Age must be a number')])
   


@app.route("/add-user", methods=['GET', 'POST'])
def add_user():
   
    cursor = mysql.cursor()
    query = "Select user_id from users"

    cursor.execute(query)
    user_id = int(cursor.fetchall()[-1][0])
    print(user_id)
    
    cursor2 = mysql.cursor()
    form = AddUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id += 1
        address = form.address.data
        age = form.age.data
        query2 = "INSERT INTO users (user_id, address, age) VALUES (%s,%s, %s)"
        
        result = cursor2.execute(query2, (user_id, address, age)) 
        print(result)
        if(result):
            
            print(result)    
            
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


class EditUserForm(Form):
    user_id = StringField('User ID', [validators.Length(min=1, max=100000)])
    address = StringField('Address', [validators.Length(min=1, max=100)])
    age = StringField('Age', [validators.Optional(), validators.Regexp('^\d+$', message='Age must be a number')])


@app.route("/edit-user", methods=['GET', 'POST'])
def edit_user():
    cursor = mysql.cursor()
    form = EditUserForm(request.form)
    user = None  # Initialize user as None
    error_message = None  # Initialize error_message as None

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





def issue_book():
    pass
def return_book():
    pass

    



if __name__ == "__main__":
    app.run(debug=True)