# LCP Website - Flask app

A bit of information of the contents of this directory

There are some key files in this folders.

- change.py - Takes as input three different lcp_references.html files and changes them to the version in the website
- config.py - Has the connection to Postgres 
- main.py   - The actual application file
- Postgres.py - All the postgres functions

## From NGINX the web application used to serve the files instead of apache/httpd, there are several IMPORTANT files that must NOT be touched.

- /etc/uwsgi.sockets/lcp_uwsgi.sock - Auto generated file by lcp_website.service
- wsgi_lcp.ini  - The reference file that the lcp_website.service takes to serve the application
- wsgi.py - The actual calling the application used by main.ini
- main_nginx.conf - The nginx configuration file

## How to run the server locally
    # Pull down the project contents
    git clone https://github.com/MIT-LCP/lcp-website.git
    # Change to the project directory
    cd lcp-website
    # Create a new Python3.5+ virtual environment
    python3 -m venv env
    # Activate the virtual environment
    source env/bin/activate
    # Install the package requirements
    pip install -r requirements.txt
    # Run the Flask App on localhost...
    # http://127.0.0.1:5000/ (debug mode off)
    flask run
    # http://0.0.0.0:8083/ (debug mode on)
    # Debug will allow to see crash errors and access the interactive debugger
    python main.py

## Deploying to the Bare Repository

Before deploying for the first time, make sure to set the variables in the `post-receive` file in the bare repository.

Add the remote bare repositories from your local development machines:

`git remote add <production> <user>@<address>:/home/webuser/lcp-website.git`

Push to the remotes when appropriate

`git push <production> <production>`
