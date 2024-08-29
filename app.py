import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)
app.secret_key = os.environ.get('PROJECT_SECRET_KEY')

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache_Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login User """

    # Forget any user_id
    session.clear()

    # User reached the route via POST
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("Must provide username", 403)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("Must provide password", 403)

        # Query database for username
        row = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists
        if len(row) != 1:
            return apology("Username does not exist", 403)

        # Ensure password matches
        if not check_password_hash(row[0]["hash"], password):
            return apology("Incorrect Password", 403)

        # Remember the user logged in
        session["user_id"] = row[0]["id"]

        # Redirect user to homepage
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """ Log User Out """

    # Forget any user_id
    session.clear()

    # Redirect user to login page
    return redirect("/")


# Route defined to send uplaoded files from directory
@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)


# Route defined to send profile pics files from directory
@app.route("/static/profile/<filename>")
def uploaded_pic(filename):
    return send_from_directory('static/profile', filename)


@app.route("/")
@login_required
def index():
        # Get user_id
    user_id = session["user_id"]

    # Check if picture_path exists
    picture_path = db.execute("SELECT picture_path FROM pictures WHERE user_id = ?", user_id)

    # If profile pic presntso the path present
    if picture_path:
        # Get profile details
        profile = db.execute("SELECT users.username, users.email, pictures.picture_path FROM users JOIN pictures ON users.id = pictures.user_id WHERE id = ?", user_id)

    # If no profile pic present then no path
    else:
        profile = db.execute("SELECT username, email FROM users WHERE id = ?", user_id)

    # Get the files
    file_rows = db.execute("SELECT * FROM files WHERE user_id = ?", user_id)

    # If files found
    if file_rows:

        files = list()

        for i in range(len(file_rows)):
            files.append(file_rows[i])

        return render_template("index.html", files=files, profile=profile)


    if not file_rows:
        return render_template("index.html", profile=profile)


@app.route("/edit_profile", methods=["POST"])
@login_required
def edit_profile():

    user_id = session["user_id"]

    if request.method == "POST":

        # If profile pic present
        pic_path = db.execute("SELECT picture_path FROM pictures WHERE user_id = ?", user_id)
        if pic_path:
            profile = db.execute("SELECT users.username, users.email, pictures.picture_path FROM users JOIN pictures ON users.id = pictures.user_id WHERE id = ?", user_id)

        # If profile pic not present
        else:
            profile = db.execute("SELECT username, email FROM users WHERE id = ?", user_id)

        return render_template("edit_profile.html", profile=profile)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():

    user_id = session["user_id"]
    if request.method == "POST":

        # Get the email
        email = request.form.get("email")

        # Get the profile pic file
        pic = request.files["picture"]

        if pic:
            # Split the pic name from right at the first occurance of a '.' just once to get a list of two elements
            pic_split = pic.filename.rsplit('.', 1)

            # Get the element 1 which is the extension of the filename
            pic_type = pic_split[1]

            # Convert the extension to lowercase
            pic_type = pic_type.lower()

            # Check for correct file type and return apology if not jpg or png
            if pic_type not in ["jpg", "png"]:
                return apology("Invalid filetype", 400)

            # Get the current date and time
            now = datetime.now()
            # Convert it into a string format
            pic_timestamp = now.strftime("%Y%m%d%H%M%S%f")

            # Create a new filename for the pic
            pic_name = pic_split[0] + pic_timestamp + '.' + pic_split[1]

            # Get the path where the pic will be stored on the server
            pic_path = "static/profile/" + pic_name

            # Store the pic at this path
            pic.save(pic_path)

        # Update the changes in users
        db.execute("UPDATE users SET email = ? WHERE id = ?", email, user_id)

        # Check if the user already had a profile pic and is changing the profile pic
        pic_data = db.execute("SELECT * FROM pictures WHERE user_id = ?", user_id)

        if pic:
            # If pic data found
            if pic_data:
                # Update the existing data with new data
                db.execute("UPDATE pictures SET picture_path = ? WHERE user_id = ?", pic_path, user_id)

            # If pic data not found
            else:
                # Insert the new data about profile pic
                db.execute("INSERT INTO pictures (user_id, picture_path) VALUES (?, ?)", user_id, pic_path)

        return redirect("/")

    else:
        return render_template("edit_profile.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached the route via post
    if request.method == "POST":
        # Get email from user and return apology if no input
        email = request.form.get("email")
        if not email:
            return apology("Enter your email", 400)

        # Basic defense for bogus email
        if '@' not in email or '.' not in email:
            return apology("Enter correct email", 400)

        # Check if the email is already registered and return apology if registered
        db_email = db.execute("SELECT email FROM users WHERE email = ?", email)
        if db_email:
            return apology("Email already registered", 400)

        # Get the username and return apology if no input
        username = request.form.get("username")
        if not username:
            return apology("Enter a username", 400)

        # Check if the username is already taken and return apology if taken
        db_username = db.execute("SELECT username FROM users WHERE username = ?", username)
        if db_username:
            return apology("Username already taken", 400)

        # Get password and return apology if no input
        password = request.form.get("password")
        if not password:
            return apology("Enter a password", 400)

        # Get confirm password and return apology if no input
        confirm_pass = request.form.get("confirm")
        if not confirm_pass:
            return apology("Confirm password", 400)

        # Check if password and confirm password match and return apology if not
        if password != confirm_pass:
            return apology("Password did not match", 400)

        # Convert the password to hashed password before storing for security
        hashed_password = generate_password_hash(password, method='scrypt', salt_length=16)

        # Insert this data to columns in users table
        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hashed_password)

        flash("Registered!")

        return redirect("/login")

    # User reached Register via GET
    else:
        return render_template("register.html")


@app.route("/change", methods=["GET", "POST"])
def change():

    if request.method == "POST":
        # Get email and return apology if no input
        email = request.form.get("email")
        if not email:
            return apology("Enter your email", 400)

        # Basic check for bogus email
        if '@' not in email or '.' not in email:
            return apology("Enter correct email", 400)

        # Get the complete data of the user from email and return apology if no data found
        row = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(row) != 1:
            return apology("Email is not registered", 400)

        # Get the username and return apology if no input
        username = request.form.get("username")
        if not username:
            return apology("Enter username", 400)

        # If username doesn't match the username in data return apology
        if username != row[0]["username"]:
            return apology("Username is incorrect", 400)

        # Get the old password and return apology if no input
        old_password = request.form.get("old_password")
        if not old_password:
            return apology("Enter old password", 400)

        # Get the hashed password from data and retrieve it to compare with user password input
        hashed_password = row[0]["hash"]
        if not check_password_hash(hashed_password, old_password):
            return apology("Old Password is incorrect", 400)

        # Get new password and return apology if no input
        new_password = request.form.get("new_password")
        if not new_password:
            return apology("Enter New password", 400)

        # Get confirm password and return apology if no input
        confirm_password = request.form.get("confirm")
        if not confirm_password:
            return apology("Confirm the password", 400)

        # Compare new password and confirm password and return apology if not equal
        if new_password != confirm_password:
            return apology("Confirm password did not match new password", 400)

        # Convert the new password to hashed form for securely storing it
        new_hashed_password = generate_password_hash(new_password, method='scrypt', salt_length=16)

        # Insert the new password into the users table for the username
        db.execute("INSERT INTO users (hash) VALUES (?) where username = ?", new_hashed_password, username)

        flash("Password changes Successfully!")

        return redirect("/login")

    # User reached via GET
    else:
        return render_template("change.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    # User id
    user_id = session['user_id']

    categories = ['Abstract', 'Animals/Wildlife', 'Arts', 'Backgrounds/Textures', 'Beauty/Fashion', 'Buildings/Landmarks', 'Business/Finance', 'Celebrities', 'Education', 'Food and Drink', 'Healthcare/Medical', 'Holidays', 'Industrial', 'Interiors', 'Miscellaneous', 'Nature', 'Objects', 'Parks/Outdoor', 'People', 'Religion', 'Science', 'Signs/Symbols', 'Sports/Recreation', 'Technology', 'Transportation', 'Vintage']
    # User reached via POST
    if request.method == "POST":

        # Get access to uploaded file and return apology if not
        file = request.files["file"]
        if not file:
            return apology("Choose a File", 400)

        # Split the filename from right at the first occurence of '.' just once to get a list of two elements
        file_split = file.filename.rsplit('.', 1)
        # Get the element 1 which is the extension of the filename
        file_type = file_split[1]
        # Convert the extension to lowercase
        file_type = file_type.lower()

        # Check for correct file type and return apology if not
        if file_type not in ['jpg', 'png']:
            return apology("Invalid filetype", 400)

        # Get the current date and time
        now = datetime.now()
        # Convert it to a string format
        file_timestamp = now.strftime("%Y%m%d%H%M%S%f")

        # Get filename
        file_name = file_split[0] + file_timestamp + '.' + file_split[1]


        # Get the path where file will be stored on the server
        file_path = "static/uploads/" + file_name

        # Store the file at this path
        file.save(file_path)

        # Get the file size
        file_size = os.stat(file_path).st_size

        # Open the uploaded image
        image = Image.open(file_path)

        # Get the width and height of the image
        width, height = image.size

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Open the watermark
        watermark_path = "static/watermark/watermark.png"
        watermark = Image.open(watermark_path)

        # Resize the watermark to the size of the image
        resized_watermark = watermark.resize((width, height))

        # Add the watermark to the image
        watermarked = Image.alpha_composite(image, resized_watermark)

        # Remove the alpha channel from the image to convert it back to JPEG for reducing size
        watermarked_rgb = watermarked.convert("RGB")

        # Create a new path for watermarked file and save it there as JPEG
        watermarked_path = "static/watermark/" + file_split[0] + file_timestamp + '.' + 'jpg'
        watermarked_rgb.save(watermarked_path, 'JPEG', quality=70)

        watermarked_size = os.stat(watermarked_path).st_size

        # Get the title and return apology if not
        title = request.form.get("title")
        if not title:
            return apology("Give Title", 400)

        # Get the keywords and return apology if not
        keywords = request.form.get("keywords")
        if not keywords:
            return apology("Give keywords", 400)

        # Convert all keywords to lowercase
        keywords = keywords.lower()

        # Split the keywords at comma into a list of seperate keywords
        keyword_list = keywords.split(',')

        # Get a new list of keywords by removing leading and trailing whitespaces
        keyword_list = [keyword.strip() for keyword in keyword_list]

        # Get the category and return apology if not
        category = request.form.get("category")
        if not category:
            return apology("Give Category", 400)

        # Get price and return apology if no input
        price = request.form.get("price")
        if not price:
            return apology("Give price to your file", 400)

        # Convert string price to an integer price and return apology of price is not an integer
        try:
            price = int(price)
        except ValueError:
            return apology("Price must be an integer", 400)

        # Check for price greater than zero and return apology if not
        if price < 0:
            return apology("Price must be greater than zero", 400)

        # Insert file data into files table
        db.execute("INSERT INTO files (user_id, file_name, file_path, file_timestamp, file_size, file_type, file_title, file_category, file_price, watermark_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, file_name, file_path, file_timestamp, file_size, file_type, title, category, price, watermarked_path)

        row_id = db.execute("SELECT file_id FROM files WHERE file_timestamp = ?", file_timestamp)
        file_id = row_id[0]["file_id"]

        # Insert keyword into keywords table
        for keyword in keyword_list:
            db.execute("INSERT INTO keywords (file_id, keyword) VALUES (?, ?)", file_id, keyword)

        return redirect("/")

    # User reached route via GET
    else:
        print(os.getcwd())
        return render_template("upload.html", categories=categories)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    # Get user id
    user_id = session["user_id"]

    # User reached via POST
    if request.method == "POST":

        # Get the search term and return apology if no input
        sentence = request.form.get("search")
        if not sentence:
            return apology("Search bar empty", 400)

        # Convert the sentence to lowercase
        sentence = sentence.lower()

        # Split the sentence into seperate words
        words = sentence.split()

        # Get all the keywords of other artists except the ones used by the user logged in
        keywords = db.execute("SELECT keyword FROM keywords WHERE file_id IN (SELECT file_id FROM files WHERE user_id <> ?)", user_id)
        # Create a list of just the values of the keyword_list dictionary
        keyword_list = list()
        for dictionary in keywords:
            for value in dictionary.values():
                keyword_list.append(value)

        # Get all the file_ids of the files by the user logged in for excluding them from remaining file_ids further
        userfileid = list()
        userfile_ids = db.execute("SELECT file_id FROM files WHERE user_id = ?", user_id)
        # Create a list of just the values of the userfile_ids dictionary
        for dictionary in userfile_ids:
            for value in dictionary.values():
                userfileid.append(value)

        # Create a new list to create a list of dictionaries
        file_id1 = list()
        # Compare each word with the keywords in the databse
        for word in words:
            if word in keyword_list:
                # Get all file_ids with the same keyword
                file_ids = db.execute("SELECT file_id FROM keywords WHERE keyword = ?", word)
                file_id1.extend(file_ids)


        # Create a list of just the values of the file_id1 dictionary and store this list in file_id2
        file_id2 = list()
        for dictionary in file_id1:
            for value in dictionary.values():
                file_id2.append(value)


        # Remove the repeating file_ids from file_id2 to keep only unique file_ids to avoid repition of same files
        file_id2 = list(set(file_id2))

        # Create a final_id list which has all the file ids excpet the file ids of the art uploaded by the user logged in
        final_id = list()
        for i in file_id2:
            if i not in userfileid:
                final_id.append(i)

        # If we are left with final_id list then proceed
        if final_id:
            # Create an empty list of files
            files = list()

            # Iterate over final_id list to get every file data with those ids
            for i in range(len(final_id)):
                file_data = db.execute("SELECT * FROM files WHERE file_id = ?", final_id[i])

                # Iterate over the file_data and append the files list
                if file_data:
                    for j in range(len(file_data)):
                        files.append(file_data[j])

                    # Get the artist username from final_id
                    user_data = db.execute("SELECT username FROM users WHERE id IN (SELECT user_id FROM files WHERE file_id = ?)", final_id[i])

                    # Get the artist username and create a new key-value pair in files with key 'username' and a value
                    username = user_data[0]["username"]
                    files[i]["username"] = username

            # After all files are appended send the files to the render_template as argument
            return render_template("search.html", files=files)

        # If we don't get any final_id list
        else:
            return render_template("search.html")

    # User reached via GET
    else:
        return render_template("index.html")


@app.route("/profile/<username>")
@login_required
def profile(username):

    # We have got the username from the link and this formatting
    # Now let's get the id and find all the files
    id = db.execute("SELECT id FROM users WHERE username = ?", username)

    user_id = id[0]["id"]

    # Check if picture_path exists
    picture_path = db.execute("SELECT picture_path FROM pictures WHERE user_id = ?", user_id)

    # If profile pic presntso the path present
    if picture_path:
        # Get profile details
        profile = db.execute("SELECT users.username, users.email, pictures.picture_path FROM users JOIN pictures ON users.id = pictures.user_id WHERE id = ?", user_id)

    # If no profile pic present then no path
    else:
        profile = db.execute("SELECT username, email FROM users WHERE id = ?", user_id)

    # Now get all the files in the portfolio of this user and send them to template
    file_data = db.execute("SELECT * FROM files WHERE user_id = ?", user_id)
    if file_data:
        files = list()
        for i in range(len(file_data)):
            files.append(file_data[i])

        return render_template("profile.html", files=files, username=username, profile=profile)


@app.route("/buy/<file_id>", methods=["POST"])
@login_required
def buy(file_id):

    if request.method == "POST":

        # Get all the file data associated with the file
        file_data = db.execute("SELECT * FROM files WHERE file_id = ?", file_id)
        if file_data:
            # Get the artist data from the file data
            artist_id = file_data[0]["user_id"]
            artist_data = db.execute("SELECT username FROM users WHERE id = ?", artist_id)
            artist_name = artist_data[0]["username"]

            # Add a new key-value pair of artist name to the file_data
            file_data[0]["artist_name"] = artist_name

            # Create an empty list for storing all data as list of dictionary
            files = list()
            for i in range(len(file_data)):
                files.append(file_data[i])

        return render_template("buy.html", files=files)


@app.route("/pay/<file_id>", methods=["GET", "POST"])
@login_required
def pay(file_id):

    #User reached via POST
    if request.method == "POST":

        # Get the file_data
        file_data = db.execute("SELECT * FROM files WHERE file_id = ?", file_id)
        if file_data:

            # Get the money earned from the file_price
            money_earned = file_data[0]["file_price"]

            # Get the artist name from user_id and file_id
            artist_id = file_data[0]["user_id"]
            artist_data = db.execute("SELECT username FROM users WHERE id = ?", artist_id)
            artist_name = artist_data[0]["username"]

            file_data[0]["artist_name"] = artist_name

            # Insert data to sales table
            db.execute("INSERT INTO sales (timestamp, money_earned, user_id) VALUES (datetime('now'), ?, ?)", money_earned, artist_id)

            # Get the last sales_id inserted
            recent_sales_id = db.execute("SELECT LAST_INSERT_ROWID() AS id")
            sales_id = recent_sales_id[0]["id"]

            # Insert data into files_sales table
            db.execute("INSERT INTO files_sales (file_id, sales_id) VALUES (?, ?)", file_id, sales_id)

            # If the artist already earned before
            init_earning = db.execute("SELECT * FROM earnings WHERE user_id = ?", artist_id)
            userId = init_earning[0]["user_id"]
            initial_money = init_earning[0]["earning"]
            if userId:
                final_earning = initial_money + money_earned

                # Update the earning table to display final earning
                db.execute("UPDATE earnings SET earning = ? WHERE user_id = ?", final_earning, artist_id)

            # if the artist earned for the first time
            if not userId:
                db.execute("INSERT INTO earnings (user_id, earning) VALUES (?, ?)", artist_id, money_earned)

            # Create sessions to pass each file_data to the downloads page to avoid form resubmitting after reload
            session["file_path"] = file_data[0]["file_path"]
            session["file_title"] = file_data[0]["file_title"]
            session["file_category"] = file_data[0]["file_category"]
            session["file_size"] = file_data[0]["file_size"]
            session["file_type"] = file_data[0]["file_type"]
            session["artist_name"] = file_data[0]["artist_name"]

        return redirect("/download")

    # User reached via GET
    else:
        return render_template("buy.html")

@app.route("/download")
@login_required
def download():
    return render_template("pay.html", file_path=session.get('file_path'), file_title=session.get('file_title'), file_category=session.get('file_category'), file_size=session.get('file_size'), file_type=session.get('file_type'), artist_name=session.get('artist_name'))


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    # Get the user id of the buyer
    user_id = session["user_id"]

    # User reached via POST method
    if request.method == "POST":

        # Get the file_id of the file that user added to the cart
        file_id = request.form.get("file_id")
        if file_id:
            # Insert the buyer and the file_id data into the cart table in database
            db.execute("INSERT INTO cart (user_id, file_id) VALUES (?, ?)", user_id, file_id)

        return redirect("/cart")

    # User reached via GET method
    else:

        # Get the file data of the files in the cart from their file_id and user_id or buyer_id in this case
        files = db.execute("SELECT * FROM files WHERE file_id IN (SELECT file_id FROM cart WHERE user_id IN (?))", user_id)

        # Find the Grand Total price for checkout and the name of the file owner or artist
        grand_total = 0
        for i in range(len(files)):
            file_id = files[i]["file_id"]
            artist_name = db.execute("SELECT username FROM users WHERE id IN (SELECT user_id FROM files WHERE file_id IN (?))", file_id)
            artist = artist_name[0]["username"]
            files[i]["artist_name"] = artist

            price = files[i]["file_price"]
            grand_total = grand_total + price

        # Pass these list of dictionaries to the template
        return render_template("cart.html", files=files, grand_total=grand_total)


@app.route("/remove", methods=["POST"])
@login_required
def remove():

    # User reached via POST
    if request.method == "POST":

        # Get the file_id
        file_id = request.form.get("remove_id")
        if file_id:
            # Delete the cart item with the file_id
            db.execute("DELETE FROM cart WHERE file_id = ?", file_id)

            return redirect("/cart")


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    # Get the user_id
    user_id = session["user_id"]

    # User reached via POST
    if request.method == "POST":
        file_data = db.execute("SELECT * FROM files WHERE file_id IN (SELECT file_id FROM cart WHERE user_id IN (?))", user_id)

        # Iterate over the length of file_data and get all the data related to the file one at a time
        for i in range(len(file_data)):
            file_price = file_data[i]["file_price"]

            file_id = file_data[i]["file_id"]
            artist_data = db.execute("SELECT user_id FROM files WHERE file_id IN (?)", file_id)
            artist_id = artist_data[0]["user_id"]

            artist_name = db.execute("SELECT username FROM users WHERE id = ?", artist_id)
            file_data[i]["artist_name"] = artist_name[0]["username"]

            # Insert data to sales table
            db.execute("INSERT INTO sales (timestamp, money_earned, user_id) VALUES (datetime('now'), ?, ?)", file_price, artist_id)

            # Get the last sales_id inserted
            recent_sales_id = db.execute("SELECT LAST_INSERT_ROWID() AS id")
            sales_id = recent_sales_id[0]["id"]

            # Insert data into files_sales table
            db.execute("INSERT INTO files_sales (file_id, sales_id) VALUES (?, ?)", file_id, sales_id)

            init_earning = db.execute("SELECT * FROM earnings WHERE user_id = ?", artist_id)
            userId = init_earning[0]["user_id"]
            initial_money = init_earning[0]["earning"]
            # UserId present means user had a sale before so not the first sale
            if userId:
                final_money = initial_money + file_price
                db.execute("UPDATE earnings SET earning = ? WHERE user_id = ?", final_money, artist_id)

            # No initial sales so it's the first sale
            if not userId:
                db.execute("INSERT INTO earnings (user_id, earning) VALUES (?, ?)", artist_id, file_price)

        # Pass the file_data in a session
        session["file_data"] = db.execute("SELECT files.*, users.username FROM files JOIN users ON files.user_id = users.id WHERE file_id IN (SELECT file_id FROM cart WHERE user_id IN (?))", user_id)

        # Clear cart after checkout
        db.execute("DELETE FROM cart WHERE user_id = ?", user_id)

        return redirect("/many_downloads")

    # User reached via GET
    else:
        return render_template("cart.html")


@app.route("/many_downloads")
@login_required
def many_downloads():
    return render_template("checkout.html", files=session.get('file_data'))


@app.route("/sales")
@login_required
def sales():

    user_id = session["user_id"]

    sales = db.execute("SELECT DATE(timestamp) as date, SUM(money_earned) as total_sales FROM sales WHERE user_id IN (?) GROUP BY DATE(timestamp)", user_id)

    sales_data = db.execute("SELECT sales.*, files_sales.file_id, files.file_path FROM sales JOIN files_sales ON sales.sales_id = files_sales.sales_id JOIN files ON files_sales.file_id = files.file_id WHERE files.user_id IN (?) ORDER BY timestamp DESC", user_id)

    return render_template("sales.html", sales=sales, sales_data=sales_data)


@app.route("/earnings")
@login_required
def earnings():

    user_id = session["user_id"]

    earnings = db.execute("SELECT * FROM earnings WHERE user_id = ?", user_id)

    if earnings:
        earning = earnings[0]["earning"]

    else:
        earning = 0

    return render_template("earnings.html", earning=earning)


@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():

    user_id = session["user_id"]

    if request.method == "POST":

        session["money_withdraw"] = db.execute("SELECT earning FROM earnings WHERE user_id = ?", user_id)

        final_deposit = 0

        # Withdraw all the earning from earnings for the user
        db.execute("UPDATE earnings SET earning = ? WHERE user_id = ?", final_deposit, user_id)

        return redirect("/money_earned")

    else:
        return render_template("withdraw.html")


@app.route("/money_earned")
@login_required
def money_earned():
    return render_template("withdraw.html", earnings=session.get("money_withdraw"))


@app.route("/analytics")
@login_required
def analytics():

    user_id = session["user_id"]

    lifetime_earnings = 0

    sales = db.execute("SELECT strftime('%m-%Y', timestamp) as month, SUM(money_earned) as total_sales FROM sales WHERE user_id IN (?) GROUP BY strftime('%m-%Y', timestamp)", user_id)

    sales_count = db.execute("SELECT files.file_id, files.file_path, COUNT(sales.sales_id) AS total_sales, SUM(sales.money_earned) AS total_earnings FROM files JOIN files_sales ON files.file_id = files_sales.file_id JOIN sales ON files_sales.sales_id = sales.sales_id WHERE files.user_id = ? GROUP BY files.file_id ORDER BY total_sales  DESC", user_id)

    total_earnings = db.execute("SELECT SUM(money_earned) FROM sales WHERE user_id IN (?)", user_id)

    if total_earnings is not None:
        lifetime_earnings = total_earnings[0]["SUM(money_earned)"]

        if lifetime_earnings is not None:
            lifetime_earnings = int(lifetime_earnings)

    return render_template("analytics.html", sales=sales, sales_count=sales_count, lifetime_earnings=lifetime_earnings)


@app.route("/edit/<file_id>", methods=["POST"])
@login_required
def edit(file_id):

    categories = ['Abstract', 'Animals/Wildlife', 'Arts', 'Backgrounds/Textures', 'Beauty/Fashion', 'Buildings/Landmarks', 'Business/Finance', 'Celebrities', 'Education', 'Food and Drink', 'Healthcare/Medical', 'Holidays', 'Industrial', 'Interiors', 'Miscellaneous', 'Nature', 'Objects', 'Parks/Outdoor', 'People', 'Religion', 'Science', 'Signs/Symbols', 'Sports/Recreation', 'Technology', 'Transportation', 'Vintage']

    files = db.execute("SELECT * FROM files WHERE file_id = ?", file_id)

    keywords = list()
    keyword = db.execute("SELECT keyword FROM keywords WHERE file_id = ?", file_id)
    for i in range(len(keyword)):
        keywords.append(keyword[i]["keyword"])

    keyword_str = ', '.join(keywords)

    for i in range(len(files)):
        files[i]["keyword"] = keyword_str

    return render_template("edit.html", files=files, categories=categories)


@app.route("/edited/<file_id>", methods=["GET", "POST"])
@login_required
def edited(file_id):

    if request.method == "POST":

        title = request.form.get("title")
        if not title:
            return apology("Give Title", 400)

        # Get the keywords and return apology if not
        keywords = request.form.get("keywords")
        if not keywords:
            return apology("Give keywords", 400)

        # Convert all keywords to lowercase
        keywords = keywords.lower()

        # Split the keywords at comma into a list of seperate keywords
        keyword_list = keywords.split(',')

        # Get a new list of keywords by removing leading and trailing whitespaces
        keyword_list = [keyword.strip() for keyword in keyword_list]

        # Get the category and return apology if not
        category = request.form.get("category")
        if not category:
            return apology("Give Category", 400)

        # Get price and return apology if no input
        price = request.form.get("price")
        if not price:
            return apology("Give price to your file", 400)

        # Convert string price to an integer price and return apology of price is not an integer
        try:
            price = float(price)
        except ValueError:
            return apology("Price must be an integer", 400)

        # Check for price greater than zero and return apology if not
        if price < 0:
            return apology("Price must be greater than zero", 400)

        # Update files table with new data for a file
        db.execute("UPDATE files SET file_title = ?, file_category = ?, file_price = ? WHERE file_id = ?", title, category, price, file_id)

        # Delete the existing keywords for a file_id and Insert new keywords
        db.execute("DELETE FROM keywords WHERE file_id = ?", file_id)

        for keyword in keyword_list:
            db.execute("INSERT INTO keywords (file_id, keyword) VALUES (?, ?)", file_id, keyword)

        return redirect("/")

    else:
        return render_template("edit.html")


@app.route("/delete/<file_id>", methods=["GET", "POST"])
@login_required
def delete(file_id):

    if request.method == "POST":
        # Get the file_path from file_id
        path = db.execute("SELECT file_path FROM files WHERE file_id = ?", file_id)
        file_path = path[0]["file_path"]

        # Get watermark path from file_id
        water_path = db.execute("SELECT watermark_path FROM files WHERE file_id = ?", file_id)
        watermark_path = water_path[0]["watermark_path"]

        # Delete the file and file_id from all tables where it is present
        db.execute("DELETE FROM keywords WHERE file_id = ?", file_id)
        db.execute("DELETE FROM cart WHERE file_id = ?", file_id)
        db.execute("DELETE FROM files_sales WHERE file_id = ?", file_id)
        db.execute("DELETE FROM files WHERE file_id = ?", file_id)

        # Delete file from the server
        if os.path.isfile(file_path):
            os.remove(file_path)

        else:
            print("Error: %s file not found")

        # Delete watermarked file from server
        if os.path.isfile(watermark_path):
            os.remove(watermark_path)

        return redirect("/")

    else:
        return render_template("edit.html")
