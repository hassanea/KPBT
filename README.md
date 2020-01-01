# Kingpin Bowling Tracker (KPBT) - Fall 2019 Senior Project
## Project Overview

The purpose of the **Kingpin** project was to create an application to enable present bowling leagues to create and manage leagues, and to provide individual bowlers detailed history and statistics for analyzing their game over the course of their league seasons.

![KPBT's Homepage](https://github.com/cjtrombley/KPTracker/blob/master/Documents/UI_Screenshots/Home-Page.png)

## Running the Project

1.  Clone the project from https://github.com/cjtrombley/KPTracker
      * Use `git clone` https://github.com/cjtrombley/KPTracker    
2.  Navigate to the directory where KPTracker/kptracker_serv/ folder is located.
3.  In the terminal, change directory `cd` into the KPTracker/kptracker_serv/ folder.
4.  Next, use the commands below depending on your OS and apply the migrate command.
     * **Note**: You must do migrations in order for the SQLite database and Django Webapp to work properly together.
* **Window**
    * Use the command `py manage.py runserver` to start development server
    * Use the command `py manage.py migrate` for applying and unapplying migrations.
* **macOS**
    * Use the command `python3 manage.py runserver` to start development server. 
    * Use the command `python3 manage.py migrate` for applying and unapplying migrations.
* **Linux**
    * Use the command `python3 manage.py runserver` to start development server. 
    * Use the command `python3 manage.py runserver` to start development server. 
5.  By default, visit the project at: http://127.0.0.1:8000/ in a web browser of your choice.  

## How the project was built? (Dependencies)
* Django
  * Resources on Django:
    * [Django](https://www.djangoproject.com)  
    * [MCD Web Docs (Django) ](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)
    * [Django Girls Tutorial](https://tutorial.djangogirls.org/en/)
* Python3
  * Resources on Python3:
    * [Python](https://www.python.org)
* JavaScript
  * Resources on JS:
    * [W3Schools (JavaScript)](https://www.w3schools.com/js/default.asp)   
    * [MCD Web Docs](https://developer.mozilla.org/en-US/)
    * [Stack Overflow](https://stackoverflow.com)
* jQuery    
  * Resources on JS:
    * [jQuery](https://jquery.com)
    * [W3Schools (jQuery)](https://www.w3schools.com/jquery/default.asp)
* Google Maps
    * Resources on Google Fonts:
        * [Google Maps](https://cloud.google.com/maps-platform/)
* Google Fonts
    * Resources on Google Fonts:
        * [Google Fonts](https://fonts.google.com)
* Font Awesome
    * Resources on Font Awesome:
        * [Font Awesome](https://fontawesome.com) 
* CSS
    * Resources on CSS: 
        * [W3Schools (CSS)](https://www.w3schools.com/css/default.asp) 
        * [MCD Web Docs (CSS)](https://developer.mozilla.org/en-US/docs/Web/CSS)
        * [CSS-Tricks](https://css-tricks.com)
        * [W3Schools (Bootstrap)](https://www.w3schools.com/bootstrap4/default.asp)