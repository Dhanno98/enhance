# Enhance - Connecting Artists and Buyers

#### Video Demo: <https://www.youtube.com/watch?v=O6watxygZsg>

#### Description:

Enhance is a platform designed to connect artists with buyers, combining features of both stock image marketplaces and freelance hiring platforms. It is designed to bridge the gap between artists and buyers, offering a platform where artists can showcase and sell their work, while buyers can easily purchase royalty-free stock images or hire artists for custom projects. Enhance aims to be a comprehensive solution to Sell Images, Buy Images, Get Hired and Hire Others.

### Project Structure

The Enhance Web Application is built using Flask framework, and it consists of several key files and directories that contribute to its functionality:

- **app.py:** This is the main file that runs the flask application. It handles routing, form submissions, database interactions, and other backend logic.

- **helpers.py:** It contains helper functions that are then called in the `app.py`.

- **templates/:** This directory contains all HTML templates used in the application. These templates use Jinja to dynamically render content based on the data passed from Flask.
    - **layout.html:** The base template that includes common elements like the header, footer, and navigation menu. It also has the element that handles display resizing for mobile and tablet screens. Other templates extend on this layout to maintain consistency across the site.
    - **register.html:** The registration page where users can create an account. It extends `layout.html` and includes form for email, username, password and password confirmation inputs.
    - **login.html:** The login page, which also extends `layout.html`. It has a form for users to input their username and password here to access their account.
    - **index.html:** The homepage that users see after logging in. It displays profile details on the left and artist's portfolio on the right.
    - **upload.html:** The page where artists can upload their work. It includes a form that contains fields for accepting image files as .jpg or .png, title, keywords, category, and price.
    - **search.html:** Displays search results when users search for images. This template shows the images with watermarks, the artist's name, image price and other relevant details.
    - **buy.html:** A page for purchasing a single image. It shows a full-sized watermarked image and additional information with a button to purchase the image.
    - **pay.html:** Shows the final screen after the user has purchased the image. It shows a full-sized watermark-free image with a button to download this image.
    - **cart.html:** Displays items that the user has added to their cart, along with options to remove items or proceed to checkout.
    - **checkout.html:** Shows the final screen after purchasing the images, where users can download watermark-free versions.
    - **profile.html:** Similar to `index.html`, but used for viewing another artist's profile and portfolio. So the images are watermarked.
    - **sales.html:** Displays the artist's sales data in a bar graph showing daily earnings created using the `Chart.js` library of JavaScript, and a detailed list of sold files.
    - **analytics.html:** Provides a comprehensive view of the artist's monthly earnings with the help of a bar graph created using the `Chart.js` library of JavaScript, lifetime earnings and best-performing images.
    - **earnings.html:** Allows artists to view and withdraw their earnings from the platform into their bank accounts.
    - **edit.html:** Allows users to make changes to the title, keywords, category and price of an already uploaded image.
    - **edit_profile:** Allows users to change their email address and add a new profile picture to give their account a distinct personality to stand out.

- **static/:** This directory contains static files like style.css. Since Enhance is not hosted on a server, images uploaded by users cannot be stored on it. These images are then stored in folders in static directory.
    - **style.css:** The main stylesheet for the application, which defines the visual appearance of the site.
    - **uploads/:** A folder where user-uploaded images are stored.
    - **watermark:** A folder that stores watermarked versions of the images to protect the artist's work.
    - **profile/:** A folder for storing users' profile pictures.

- **project.db:** The database for the entire Enhance web app that contains various tables.

### Database Schema

Enhance uses SQLite as its database system. Below is the structure of the database, including all the tables and their corresponding columns:

1. **Users Table:**
    - **Table Name:** `users`
    - **Description:** Stores information about each user on the platform.
    - **Columns:**
        - `id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL`: A unique identifier for each user.
        - `username TEXT NOT NULL`: The unique username of the user.
        - `email TEXT NOT NULL`: The email address of the user.
        - `hash TEXT NOT NULL`: The hashed password of the user.

2. **SQLite Sequence Table:**
    - **Table Name:** `sqlite_sequence`
    - **Description:** Maintains the auto-increment sequence for tables.
    - **Columns:**
        - `name TEXT`: The name of the table.
        - `seq INTEGER`: The last used sequence number.

3. **Username Index:**
    - **Index Name:** `username`
    - **Description:** Ensures that the username is unique across platform.
    - **Index On:** `username` column of the `users` table.

4. **Files Table:**
    - **Table Name:** `files`
    - **Description:** Stores information about each uploaded image file.
    - **Columns:**
        - `file_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL`: A unique identifier for each file.
        - `user_id INTEGER NOT NULL`: The ID of the user who uploaded the file.
            - **Foreign Key:** References `users(id)`.
        - `file_name TEXT NOT NULL`: The new name of the uploaded file.
        - `file_path TEXT NOT NULL`: The path where the file is stored.
        - `file_timestamp TEXT NOT NULL`: The timestamp when the file was uploaded.
        - `file_size REAL NOT NULL`: The size of the file in megabytes.
        - `file_type TEXT NOT NULL`: The type of the file (eg., jpg, png).
        - `file_title TEXT NOT NULL`: The title of the file, set by the user.
        - `file_category TEXT NOT NULL`: The category under which the user classified the file.
        - `file_price REAL NOT NULL`: The price of the file set by the user.
        - `watermark_path TEXT`: The path to the watermarked version of the file.

5. **Keywords Table:**
    - **Table Name:** `keywords`
    - **Description:** Stores keywords associated with each image file for search functionality.
    - **Columns:**
        - `file_id INTEGER NOT NULL`: The ID of the file, linked to the `files` table.
            - **Foreign Key:** References `files(file_id)`.
        - `keyword TEXT NOT NULL`: A keyword associated with the file.

6. **Cart Table:**
    - **Table Name:** `cart`
    - **Description:** Stores the files that users have added to their shopping cart.
    - **Columns:**
        - `user_id INTEGER NOT NULL`: The ID of the user.
            - **Foreign Key:** References `users(id)`.
        - `file_id INTEGER NOT NULL`: The ID of the file in user's cart.
            - **Foreign Key:** References `files(file_id)`.

7. **Sales Table:**
    - **Table Name:** `sales`
    - **Description:** Tracks sales transactions on the platform.
    - **Columns:**
        - `sales_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL`: A unique identifier for each sale.
        - `user_id INTEGER NOT NULL`: The ID of the user who made the sale.
            - **Foreign Key:** References `users(id)`.
        - `timestamp DATETIME`: The date and time of the sale.
        - `money_earned REAL NOT NULL`: The amount earned from the sale.

8. **Files Sales Table:**
    - **Table Name:** `files_sales`
    - **Description:** Links files to their corresponding sales transactions.
    - **Columns:**
        - `file_id INTEGER NOT NULL`: The ID of the file sold.
            - **Foreign Key:** References `files(file_id)`.
        - `sales_id INTEGER NOT NULL`: The ID of the sale.
            - **Foreign Key:** References `sales(sales_id)`.

9. **Earnings Table:**
    - **Table Name:** `earnings`
    - **Description:** Tracks the earnings of each user from sales.
    - **Columns:**
        - `user_id INTEGER NOT NULL`: The ID of the user.
            - **Foreign Key:** References `users(id)`.
        - `earning REAL NOT NULL`: The total earnings of the user.

10. **Pictures Table:**
    - **Table Name:** `pictures`
    - **Description:** Stores the profile pictures of the users.
    - **Columns:**
        - `user_id INTEGER NOT NULL`: The ID of the user.
            - **Foreign Key:** References `users(id)`.
        - `picture_path TEXT NOT NULL`: The path where the profile picture is stored.

### Key Features and Functionalities

1. **User Registration and Login:**
    - The registration feature allows users to create an account with a unique username. The `register.html` template is responsible for rendering the registration form. In `app.py`, the `/register` route handles form submission, validates the input, and checks for existing usernames. Passwords are hashed using `generate_password_hash` from `werkzeug.security` before being stored in the `users` table in the database.
    - The login feature requires users to enter their username and password. The `login.html` template provides the input fields. The `/login` route in `app.py` checks the entered credentials against the database, using `check_password_hash` to verify the password. Upon successful login, users are redirected to the `index.html` page.

2. **Artist Portfolio:**
    - After logging in, users are taken to the `index.html` page, which displays their profile details on the left and their portfolio on the right. The portfolio section is designed to show up to 30 images at a time, in a grid of 3 columns and 10 rows, with additional images accessible via dynamically created buttons. This is achieved through JavaScript, which toggles the display of images based on the button clicked.
    - In `/` route in `app.py`, the images in the portfolio are fetched from the `files` table in the database, and their file paths are passed to the `index.html` template using Jinja. This allows for dynamic rendering of the user's uploaded content.

3. **Upload Images:**
    - Artists can upload images through the `upload.html` page. They provide the details such as the image file, title, keywords, category, and price. Keywords are especially important, as they determine whether the image will appear in search results.
    - Upon submission, the image is stored in the `uploads/` directory, and a watermarked version is created and stored in the `watermark/` directory. All relevant information about the image, including its file path, title, keywords, category, price, and artist's ID, is saved in the `files` and `keywords` tables in the database.
    - The `/upload` route in `app.py` handles the file upload, image processing, and database entry.

4. **Search Functionality:**
    - Buyers can search for images using the search bar in the menu. The `search.html` template displays the search results, which include watermarked images, their descriptions, categories, prices, and artist names.
    - The search algorithm is implemented in the `/search` route in `app.py`. When a user submits a search query, the algorithm splits the query into individual words and compares them with the keywords stored in the database. If matches are found, the corresponding images are retrieved using their file IDs and displayed in the `search.html` template.
    - To prevent buyers from purchasing their own images, the search algorithm makes sure to exclude any images uploaded by the currently logged-in user from the search results.

5. **Image Purchase:**
    - Buyers can purchase images either individually or in bulk. For single-image purchases, they are directed to the `buy.html` page, where they can view the full-sized watermarked image and proceed with the transaction.
    - For multiple images, buyers can add items to their cart, which is managed by the `cart.html` template. The cart retains its contents even after the user logs out, thanks to session management.
    - Upon checkout, the total amount is deducted from the buyer's account and transferred to the artist's account. The buyer is then redirected to `checkout.html`, where they can download the purchased images without watermarks.

6. **Find and Hire Artists:**
    - When browsing search results, buyers can click on an artist's name to view their profile and portfolio through the `profile.html` template. This page functions similarly to the user's own `index.html`, but with watermarked images to protect the artist's work.
    - Buyers can contact artists via email in the artist's profile to discuss freelance projects or commission work, facilitating a direct connection between the two parties.

7. **Sales Analytics:**
    - The `sales.html` template provides artists with a visual representation of their daily sales through a bar graph. The graph is created using the `Chart.js` library of JavaScript, which plots sales data fetched from the `sales` table in the database. The `/sales` route in `app.py` fetches the sales data from `sales` table and passes it to `sales.html`.
    - Below the graph, a detailed list of sales, including the date, time, and amount, is displayed. The `/sales` route in `app.py` fetches the sales data for particular files from `files_sales`, `sales`, and `files` tables in the database.
    - The `analytics.html` template offers more in-depth analysis, showing monthly sales, lifetime earnings, and identifying the best-performing images based on number of sales. This information helps artists understand market trends and optimize their portfolio accordingly. The `/analytics` route in `app.py` fetches the data to be displayed on the analytics page from `sales`, `files`, `files_sales`, and `earnings` tables in the database.

8. **Earning Management:**
    - Artists can view their earnings through the `earnings.html` template, which displays the total amount earned from sales. They can initiate a withdrawal to transfer the funds to their bank account. The payment processing logic is handled in the `/earnings` route in `app.py`.

9. **Profile Management:**
    - Users can edit their profile details through the `profile.html` template. They can change their email address, set a new profile picture, and update their portfolio. Profile pictures are stored in the `profile/` directory within `static/`.
    - Artists can also edit the information related to their uploaded images, such as title, add or change keywords to increase the overall searchability of the image, category, and price. These changes are updated in the database to reflect in future searches and displays.

### Design Choices:

- **Password Hashing:** Implemented using `werkzeug.security` to protect user credentials.
- **Keyword-Based Search Algorithm:** The search algorithm is designed to split the user query into individual keywords, allowing for more accurate and comprehensive search results.
- **Watermarking Images for Copyright Protection:** Ensures that  artists' work is protected from unauthorized use until a purchase is made.
- **Skipped Implementation of Payment Gateway:** The payment transactions after a purchase is not dealt with a payment gateway that actually deducts certain amount from buyer's real bank account and transfers that money into the seller's account as it comes with its own security management for secure transactions. Enhance application in its present state is made for the purpose of CS50 project and not for real world business. Although the application can certainly be modified to support a Payment Gateway for smooth transactions.
- **Storage of Uploaded Images in Static Folder:** Since Enhance is not hosted on a server, images uploaded by users are stored in the `static` directory, specifically within subfolders like `uploads/` and `watermark/`. This choice was made to simplify access and retrieval of images during development. However, in a production environment, images would ideally be stored on a dedicated file server or cloud storage to enhance performance and scalabilty.
- **Limited Search Functionality During Development:** Currently, users cannot search for anything on the app because the database, or server, is running locally on a personal computer, and there are no images from other users or images other than the ones I uploaded. When the application is hosted on a server and accessible to the public, artists will contribute a variety of images, making search results more functional and meaningful.
- **`files_sales` Table:** The need for creating a seperate table as a bridge between `sales` and `files` tables was felt to address the issue of keeping analytics data, especially the monthly earnings and lifetime earnings data unaffected even after a user deletes certain images from their portfolio.


### Conclusion
Enhance is a robust platform that bridges the gap between artists and buyers, offering a space for creativity, commerce, and collaboration. While the current version is a proof-of-concept developed as a final project for CS50x, it lays a solid foundation for a fully functional marketplace and hiring platform. Future developments could include integrating a payment gateway, optimizing the search algorithm for scalability, hosting the application on a cloud server to support a wider user base, and enabling users to generate AI-based images directly on the platform. These AI-generated images will be showcased under a dedicated "AI Images" banner in the artist's portfolio, further broadening the creative possibilities for artists and also help buyers get AI stock images.

Thank you for exploring Enhance, and I welcome any feedback, contributions, or inquiries about the project.
