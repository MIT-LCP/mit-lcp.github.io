# LCP Website - Flask app

A bit of information of the contents of this directory

There are some key files in this folders.

- change.py - Takes as input three different lcp_references.html files and changes them to the version in the website
- config.py - Has the connection to Postgres 
- main.py   - The actual application file
- Postgres.py - All the postgres functions

##### From NGINX the web application used to serve the files instead of apache/httpd, there are several IMPORTANT files that must NOT be touched.

- /etc/uwsgi.sockets/lcp_uwsgi.sock - Auto generated file by lcp_website.service
- wsgi_lcp.ini  - The reference file that the lcp_website.service takes to serve the application
- wsgi.py - The actual calling the application used by main.ini
- main_nginx.conf - The nginx configuration file

