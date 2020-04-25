# 507Final_project
Scraped the teams' and players' information from the https://www.basketball-reference.com/. Created a website and some user interface part by using flask to show these results.

The packages that I used for my project are: requests, BeautifulSoup, sqlite3, pandas, webbrowser, plotly, Flask and json.
You could run my program under my folder by entering: 'python3 app.py', and then copy and paste the link 'http://127.0.0.1:5000/' to your browser.
And then you could see my home page, and click the different button to get the information you like.
Since it could be a little bit slow loading the data from the website to the database,
I commentted the function db_insert() on 398 row of the app.py file, and I provided the database that I loaded before for you to test this project.
Also you could uncomment this line to check the function of loading the data to the database.
