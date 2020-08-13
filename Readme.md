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
### Set up the local environment
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
### Run the server
    # Run the Flask App on localhost using the following:
    # (1) http://127.0.0.1:5000/ 
    #     debug mode off (preferred): more realistic to actual
    #     production environment, 500 errors will be
    #     replaced by general error pages
    flask run
    # (2) http://0.0.0.0:8083/
    #     debug mode on: better suited for
    #     development environment, 500 errors will be
    #     displayed with detailed stack traces
    python main.py
