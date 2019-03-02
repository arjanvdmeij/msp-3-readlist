# [MARVEL comics reading-list](https://readlist-msp3.herokuapp.com)

## Overview

### What is this website for?

This website was made as part of my training towards Full Stack Web Developer at [Code Institute](https://codeinstitute.net).
The goal was to create a site that made use of several different technologies, outlined below. 
Being a life-long Marvel fan, I decided to do project using Marvel's API, as I did in the previous project, 
this time erecting a site where people can create what works as a to-do list, maintaining an archive of comics they want to read, or have read alrady.
They also should be presented with new comics, as well as a total list of comics for them to add to the list(s).
This resulted in this site, where people can:

- Create an account
- See the most recent comics released, or
- All comics released (and in the database so far)
- Add comics to their reading list
- Mark comics as read once done
- If needed, delete their read comics from the list (not the goal of an archive though!)
- Change their display name, or change their password for the site

### What does it do?

On a schedule (daily), a script connects to Marvel using their API, and retrieves any newly released comics.
The comics are normally released weekly, however, sometimes specials will come out in between. The script covers eight days, 
to make sure that there will always be comics in the list where releases are done weekly.
Logic within the script decides if what's downloaded is already in the database, and if so, it is disregarded.
Whenever a user logs on, they are presented with their current reading list (or a message when the list is empty).
From there, additions to the list can be done, or comics can be marked as read, where they will be moved to the list of comcis that were read.

For admin purposes a separate page was created where the admin (based in Mongo) can delete user entries, effectively removing them from:
- users
- admin table
- comics list table (all entries owned by this user)

### How does it work

The site runs on Flask, with a Mongo DB as backend. 
Users can create accounts (where logic prevents double names for accounts) with a degree of 'enforcement' on valid characters, and password restrictions/rules.
Once the account is in place, users can started adding comics to their list.
Items marked, are added into the table for comics lists, with a field linking them to the specific user.
Available comics are filtered against the user's current reading list, to make sure that items in the list aren't shown as available to add.
Whenever the list is then shown, it is populated using a query to show all comics in that table that relate to the user and have a field marked 'unread'.
If a user marks a comic as read, the entry is looked up and the field is marked 'read'. 
Whenever a user deletes a comic from their list, the entry in the table is removed. This immediately allows a user to add this specific comic once more, as 
the check performed when loading new comics will no longer filter the comic as being in the list.

The site relies on the [MARVEL API](https://developer.marvel.com), any and all content retrieved is © 2019 MARVEL.
<b>For the record (and it can't be stressed enough), this site offers titles and covers <U>only</u>, not the actual comics!</b>

The code used is mostly based on **Flask**, version 1.0.2 and **Python**, version 3.4.3.
Database backend (MongoDB) for the site is hosted with [mLab](https://mlab.com).<br>
Additionally, **jQuery**, version 3.3.1, is used to aid with marking comics.<br>
Styling is done using [Materialize](https://materializecss.com), version 1.0.0.<br>
<sup>As little additional CSS as needed was used. The majority is straight Materialize. </sup>

Pop-up images make use of [Lightbox](https://lokeshdhakar.com/projects/lightbox2/).
The site can be viewed [HERE](https://readlist-msp3.herokuapp.com).

## Features

### Existing Features
- Clear opening page with some explanation, and the option to sign up, or sign in
- Validation of existing users when adding a new user
- Password validation, option to view entered passwords for the user
- Hashed password storage in the database
- Constantly updated list of released comics, and archive of previously released comics
- Option to zoom in on comic covers using **LightBox**
- Options for user to change displayed name, or change password

### Features Left to Implement
- Have production run using gunicorn on Heroku
- Create a way to filter the list of comics
- Extended information when clicking on (e.g.) comics, using further API calls with:
  - Character(s) information
  - Comics information (price, link to buy/read)
  - Series information

## Tech Used

### Technologies and outside sources:
- **HTML**, **CSS**, **jQuery** / **Javascript**, **Python**
- [Flask](http://flask.pocoo.org)
  - Base framework for the site
- **MongoDB** hosted by [mLab](https://mlab.com)
  - database backend containing all user and comic information
  - separate databases for the development and production environment
- [Materialize](http://materializecss.com/) version 1.0.0
  - Used to give the site a simple, responsive layout
- [JQuery](https://jquery.com) version 3.3.1
  - Used to support the python code using ajax and for styling of marked items
- [Lightbox](https://lokeshdhakar.com/projects/lightbox2/)
  - Used to zoom in on comic covers
- [Stack Overflow](https://stackoverflow.com/)
- [Heroku](https://dashboard.heroku.com)
  - Used to host the site
  - Heroku Scheduler add-on used to run daily comics update script

## Deployment
Two separate databases exist, one for development and one for production.
Originally the current production database was used in development, in order to quickly fill it with a good amount of data.
Towards the end, a new specific development database was created. Based on the environment the app is executed in, the correct database is loaded.<br>
Both databases have an identical set of tables, to ensure no unnecessary precautions need to be taken.<br>

Git is used for the deployment of the application. The order of steps is:
- Development and testing on Cloud 9
- Commit changes to Git
- When needed, push changes to Github
- Heroku is connected to Github and picks up the new changes
- Heroku kicks off a new build based on the changes

Within the code, measures are taken to ensure that the application uses the correct data for the environment it's running in.
The config file reads environment variables, one of which is the FLASK_ENV variable.
This is set to 'development' and 'production' for the respective environments.
Based on the host the application runs on, this then triggers the correct settings.

The one thing that is identical between environments are the settings for the Marvel API, as this is always the same.

The update_comics script is run manually on Cloud 9, since cron jobs won't run in stopped environemnts.
For the production environment, the Heroku Scheduler has been added and set to run daily at 5AM to check for new additions to available comics.

## File structure
Despite it being glaringly obvious in the repository, a small explanation of the structure:
The root of the structure contains the main app, its config file and the script to update comics.
A <em>templates</em> directory holds all the HTML files used.
Within a directory <em>static</em> are sub-directories containing CSS files and JS files.
In order to not be dependent on the CDN for jQuery and Materialize, the min.css and min.js versions of files are included in the application.
Within the sub-directory <em>images</em> under <em>static</em> are the few images used within the application.
These images are needed for the favicon, the error pages and empty comic lists for users.
The remaining small files are used by Lightbox.

## Wireframes and User Stories
- In the root of the repository is a document with stories and mockups (hand drawn and scanned)
    -  The document also contains extended information on the testing described below

## Testing
- Testing was done two-fold, by continuous testing of every step created, as well as unit tests
  - Manual tests:
    - initial HTML page with just placeholders
    - any subsequent view tested with every change
    - script creation and data retrieval tested by pulling data, deleting and pulling again. And again. And again..
    - process data onto page placeholders
    - expand code and page continuously making calls to the database and updating comics used
    - make modifications to the code (whether python, jquery or html) and immediately test results
    - ensure user accounts are always unique by creating an account, retry creation and see and modify responses returned
    - test user creation, user re-creation (for errors), user deletion, user re-creation (to verify deletion of comics list)
    - change user's display name, change user's password, log in with new password
    - testing scheduler on Heroku by updating during day time and check logging in Heroku, eventually setting run at 05:00
    - Heroku scheduler logging snippet for update script available in wireframe and user story document
  - Unit tests:
    - for a result, see the word document in the root
  
- Testing was done on the following browsers:
  - Safari
  - Google Chrome
  
- Mobile device testing was done:
  - Using Chrome's developer tools, emulating all available formats
  - iPhone 7+
    - iOS Safari
    - iOS Opera
    - iOS Chrome
  - iPad Air2
    - iOS Safari
    - iOS Opera
    - iOS Chrome

## Media and Information
##### Data provided by Marvel. © 2019 MARVEL
- All other images (Drax, Black Widow, Iron Army Drone and Deadpool) <br> originally © 2019 MARVEL
    ###### Images were modified in all cases to suit my needs
