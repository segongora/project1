# Project 1

Web Programming with Python and JavaScript
I added requests to the requirements.txt

To run the project you should first run pip3 install -r requirements.txt. Then cd into project1 folder and run source .start (if on macos).

 I only used three tables for the project: Users, Books and Reviews.
 Users have a name, username (non-repeatable across the page) and password.
 Books have a title, author, year and isbn.
 Reviews have text (which is the review), rating and user_id (who placed the review) and book_id (in which book).
 All have id property.

- First I have a index.html which is a page where the list of the books is displayed. In this page you can also search for any book with the search box.

- Layout.html is the page I use to have the same code in all .html pages. I use a simple navigation bar from bootstrap, to link all my other pages. I also use it to define if the button access or profile should be displayed.

- In access.html is where the login and the signup happens. I have tabs to navigate between login tab or signup. The signup has a post method and first checks if there's no other user with that username. Then hashes the password to make it secure and don't store it as plain text and then sends the command to create a users. Login is also post method but checks if it exists a user with that username, and then if that username has the same password.

- Error.html is just a page where signup or login redirects the user if something was wrong. It also has a custom message which I access via session.

- The book.html is just where the book has a its own page. You can see author, year, title, and reviews. You can see who left that review, and if you left it you can't review again. You can also find your review if you click the button.

- profile.html is the page where a user gets redirected after a successful login or sign up. There you can see the name you signed up with, the username you choose and then you have buttons as to what you want to do. If you cant to find a book you  get redirected to index.html,  you can see which reviews you have left on which books and redirect to those single book pages. And lastly edit your info (name, username or password).

- Lastly the search.html page just display a list of every result your search has. Every result has title, author, year, isbn and it is a link to their single book page.
