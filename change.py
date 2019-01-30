# -*- coding: UTF-8 -*-
#!/usr/bin/python
#############################################################################################################
# Felipe Torres Fabregas
# Created on 10/22/2017: Felipe
# LCP website publication reconfiguration file
# #
# This file takes as an input the actual "http://lcp.mit.edu/lcp_references.html" generated 
# by Ken's script and re-arranges it to the a page with a sidebar of all the years.
# 
# ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** TODO ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
# If the lcp_references.html file were to change locations, the inpout of the file has also to be changed
#############################################################################################################
import datetime, urllib2
from hashlib import sha256
from re import match, sub, DOTALL

def File_Change(File_Content):
  """
  This function is designed to take the file that Ken generates for the publications, and re-arrange it to show the 
  publications by year.
  """
  Years = {'ALL':''} # we create a dictionary for the years from 2003, that the publications were started to get recorded int he website.
  Current_Year = datetime.datetime.now().year
  for item in reversed(range(2003, Current_Year+1)):# We add the keys to the dictionary of years, basicly we add a every year, until the current year
      Years[int(item)] = ""
  
  File_Content = sub(r"<!--(.|\s|\n)*?-->", "", File_Content, flags=DOTALL).split("""<dl compact="1" class="bib2xhtml">""")
  
  Size            = len(File_Content)
  Header          = File_Content[0] # We take the header, and we sicard it.
  Journal_Tag     = """\r\n<a name="journal"></a><h3>Journal articles</h3>\r\n</dl>\r\n\r\n"""
  Conferences_Tag = """\r\n<a name="conferences"></a><h3>Conference proceedings and presentations</h3>\r\n</dl>\r\n\r\n"""
  Books_Tag       = """\r\n<a name="books"></a><h3>Books and book chapters</h3>\r\n</dl>\r\n\r\n"""
  Theses_Tag      = """\r\n<a name="theses"></a><h3>Theses</h3>\r\n</dl>\r\n\r\n"""

  # Here we find where the stirngs above are located. 
  Journal_idx     = File_Content.index(Journal_Tag)     #1
  Conferences_idx = File_Content.index(Conferences_Tag) #16
  Books_idx       = File_Content.index(Books_Tag)       #31
  Theses_idx      = File_Content.index(Theses_Tag)      #38
  All = {'journal':{}, 'conferences':{}, 'books':{}, 'theses':{}}

  # Here we itterate throught all four elements of the file. 
  # We keep a copy of the current row, each row is a journal or conference or book, depends on what for loop you are in.
  # Since there are two places the year is located at, we have to try and search for it.
  # The output of the try exept, will be (2016 16</ OR ">20 2015), since we use that variable to set the year, we need a try exept to see if the item is a intiger or a string.
  # We remove all newlines because they dont work on html, set the ID of the journal, conference... and we remove the commented data, just to try and clean out the code.
  # If the year wasnt found, then there was a change in the perl creation script, and now we have to check what happened and where is the year. 

  for row in range(Journal_idx + 1, Conferences_idx):
    if File_Content[row][21:25].isdigit():
      Journal_Tag = Journal_Tag.replace("\r","").replace("\n","").replace("</dl>","")
      Years[int(File_Content[row][21:25])] += Journal_Tag.replace("journal", "journal"+File_Content[row][21:25]) + File_Content[row][File_Content[row].index('</dl>')+5:]
      All['journal'][int(File_Content[row][21:25])] = Journal_Tag + File_Content[row][File_Content[row].index('</dl>')+5:]
    else:
      print ("We could not find the year, the variables are not int. Check the HTML file.", row, "\n\n")

  for row in range(Conferences_idx + 1, Books_idx):
    if File_Content[row][21:25].isdigit():
      Conferences_Tag = Conferences_Tag.replace("\r","").replace("\n","").replace("</dl>","")
      Years[int(File_Content[row][21:25])] += Conferences_Tag.replace("conferences", "conferences"+File_Content[row][21:25]) + File_Content[row][File_Content[row].index('</dl>')+5:]
      All['conferences'][int(File_Content[row][21:25])] = Conferences_Tag + File_Content[row][File_Content[row].index('</dl>')+5:]
    else:
      print ("We could not find the year, the variables are not int. Check the HTML file.", row, "\n\n")

  for row in range(Books_idx + 1, Theses_idx):
    if File_Content[row][21:25].isdigit():
      Books_Tag = Books_Tag.replace("\r","").replace("\n","").replace("</dl>","")
      Years[int(File_Content[row][21:25])] += Books_Tag.replace("books", "books"+File_Content[row][21:25]) + File_Content[row][File_Content[row].index('</dl>')+5:]
      All['books'][int(File_Content[row][21:25])] = Books_Tag + File_Content[row][File_Content[row].index('</dl>')+5:]
    else:
      print ("We could not find the year, the variables are not int. Check the HTML file.", row, "\n\n")

  for row in range(Theses_idx + 1, Size):
    if File_Content[row][21:25].isdigit():
      Theses_Tag = Theses_Tag.replace("\r","").replace("\n","").replace("</dl>","")
      Years[int(File_Content[row][21:25])] += Theses_Tag.replace("theses","theses"+File_Content[row][21:25]) + File_Content[row][File_Content[row].index('</dl>')+5:]
      All['theses'][int(File_Content[row][21:25])] = Theses_Tag + File_Content[row][File_Content[row].index('</dl>')+5:]
    else:
      print ("We could not find the year, the variables are not int. Check the HTML file.", row, "\n\n")

  Recent = []
  for item in Years[Current_Year].split('<dd>'):
    if "http" in item.split("</a>")[0].split('<a')[1]:
      Recent.append("<li><a" + item.split("</a>")[0].split('<a')[1] + "</a></li>")
  if len(Years[Current_Year].split('<dd>')) < 5:
    for item in Years[Current_Year-1].split('<dd>'):
      if "http" in item.split("</a>")[0].split('<a')[1]:
        Recent.append("<li><a" + item.split("</a>")[0].split('<a')[1] + "</a></li>")  
  #####
  temp = ""

  for key in ['journal', 'conferences', 'books', 'theses']:
    if key == 'journal':
      temp += "<h3 id='journalall'>Journal articles</h3>"
    elif key == 'conferences':
      temp += "<h3 id='conferencesall'>Conference proceedings and presentations</h3>"
    elif key == 'books':
      temp += "<h3 id='booksall'>Books and book chapters</h3>"
    elif key == 'theses':
      temp += "<h3 id='thesesall'>Theses</h3>"
    else:
      print ('key', key)
    for item in reversed(range(2003, Current_Year+1)):
      if item in All[key].keys():
        if key == 'journal':
          temp += All[key][item].replace('<h3>Journal articles</h3>', '<h4>{0}</h4>'.format(item))
        elif key == 'conferences':
          temp += All[key][item].replace('<h3>Conference proceedings and presentations</h3>', '<h4>{0}</h4>'.format(item))
        elif key == 'books':
          temp += All[key][item].replace('<h3>Books and book chapters</h3>', '<h4>{0}</h4>'.format(item))
        elif key == 'theses':
          temp += All[key][item].replace('<h3>Theses</h3>', '<h4>{0}</h4>'.format(item))
        else:
          print ('key', key)

  Head_tag = """<center><a href="#journalall">Journal articles</a> | <a href="#conferencesall">Conference  presentations</a> | 
  <a href="#booksall">Books and book chapters</a> | <a href="#thesesall">Theses</a></center>"""
  Content  = """<div id="ALL" class="container tab-pane fade">{0}{1}</div>\n""".format(Head_tag, temp)
# Setting the content of the years
  for key, value in Years.iteritems():
      Head_tag = """<center><a href="#journal{}">Journal articles</a> | <a href="#conferences{}">Conference  presentations</a> | 
      <a href="#books{}">Books and book chapters</a> | <a href="#theses{}">Theses</a></center>""".format(key, key, key, key)
      if key == Current_Year:
          if Years[Current_Year] != "":
              Content += """<div id="P_{0}" class="container tab-pane active">{1}{2}</div>\n""".format(key, Head_tag, value)
          else:
              Content += """<div id="P_{0}" class="container tab-pane fade">{1}{2}</div>\n""".format(key, Head_tag, value)
      elif key == 'ALL':
          pass
          # Content += """<div id="%s" class="tab-pane fade">%s%sUnder development</div>\n""" % (key, Head_tag, value)
      else:
          if Years[Current_Year] == "" and key == Current_Year -1:
              Content += """<div id="P_{0}" class="container tab-pane active">{1}{2}</div>\n""".format(key, Head_tag, value)
          else:
              Content += """<div id="P_{0}" class="container tab-pane fade">{1}{2}</div>\n""".format(key, Head_tag, value)

          # Content += """<div id="%s" class="tab-pane fade">%s%sUnder development</div>\n""" % (key, Head_tag, value)
# Setting the sidebar with the years
  Side_Tab = """<li class="nav-item"><a class="nav-link" data-toggle="tab" id="ALL_tab" href="#ALL">All</a></li>"""
  for item in reversed(range(2003, Current_Year+1)):
      if item == Current_Year:
          if Years[Current_Year] != "":
              Side_Tab += """<li class="nav-item"><a class="nav-link active" data-toggle="tab" id="{}_tab" href="#P_{}">{}</a></li>\n""".format(item, item, item)
          else:
              Side_Tab += """<li class="nav-item"><a class="nav-link btn disabled" data-toggle="tab" id="{}_tab" href="#P_{}">{}</a></li>\n""".format(item, item, item)
      else:
          if Years[Current_Year] == "" and item == Current_Year -1:
              Side_Tab += """<li class="nav-item"><a class="nav-link active" data-toggle="tab" id="{}_tab" href="#P_{}">{}</a></li>\n""".format(item, item, item)
          else:
              Side_Tab += """<li class="nav-item"><a class="nav-link" data-toggle="tab" id="{}_tab" href="#P_{}">{}</a></li>\n""".format(item, item, item)
  # Head = "<center>"+ File_Content[0].replace("""| <a href="#theses">Theses</a>""", """<!--| <a href="#theses">Theses</a>-->""") + "</center>"
  File_Content[0] = File_Content[0].replace("""<a href="#journal">""", """<center><a href="#journal">""").replace("""<a href="#theses">Theses</a>""", """<a href="#theses">Theses</a></center>""").replace("""\r\n\r\n<p>\r\n(A separate listing of PhysioNet tutorials is available at <a href="http://physionet.org/tutorials/" target="_blank" >http://physionet.org/tutorials/</a>.)\r\n</p>\r\n\r\n""","").replace("\r","").replace("\n","").replace("<br>","").replace("< br>","").replace("<br >","").replace("<br />","").replace("""<center><a href="#journal">Journal articles</a> | <a href="#conferences">Conference  presentations</a> | <a href="#books">Books and book chapters</a> | <a href="#theses">Theses</a></center>""","")

  Head = str(File_Content[0])
  Header_HTML = """
  {% extends "base.html" %}
  {% block title %}Laboratory for Computational Physiology{% endblock %}
  {% block head2 %}
  <style type='text/css'>

  #left ul.menu li.menu_publications a:link,
  #left ul.menu li.menu_publications a:visited {
  background: #DFE8F5;
  border-left:solid 1px #9BA8BE;
  border-right:solid 1px #9BA8BE;
  }

  #left ul.menu li.menu_publications a:hover,
  #left ul.menu li.menu_publications a:active,
  #left ul.menu li.menu_publications a:focus {
  color: #25385D;
  }

  dl.bib2xhtml {
    margin:1em 0 0 10em;
    margin:1em 0 0 0em;
  }

  dl.bib2xhtml dt {
    font-weight:normal;
    padding:0 .5em .3em 0;
    float: left;
    text-align: right;
    min-width: 2em;
  }

  dl.bib2xhtml dt a:link,
  dl.bib2xhtml dt a:visited {
    color: inherit;
    background-color: inherit;
  }

  dl.bib2xhtml dt a:hover,
  dl.bib2xhtml dt a:active,
  dl.bib2xhtml dt a:focus {
    color: inherit;
    background-color: inherit;
  }

  dl.bib2xhtml dd {
    padding:0 0 1em 2.8em;
  }

  dl.bib2xhtml .year {
    font-style:italic;
  }
  ul.bib2xhtml li {
    padding-bottom: 1em 
  }
  .nav-tabs{
    border-right: 1px solid #ddd;
    border-bottom: transparent !important;
  }
/*  .tabs-left { max-width:100% }*/  
  .tab-pane { width:100% }

  .nav-tabs .nav-item.show .nav-link, .nav-tabs .nav-link.active{
    border: 2px solid #000 !important;
    border-right-color: transparent !important;
    font-weight: bolder;
    color: #000;
  }

  a {color: #202123;}
  </style>
  {% endblock %}
  {% block content %}"""

  Header_HTML += """
  <div class="container about">
    <div class="row">
      <div class="col-md-12 col-sm-12 col-xs-12">
        <div class="feature_header text-center">
          <h3 class="feature_title">Publications</h3>
          <div class="divider"></div>
        </div>
      </div>  <!-- Col-md-12 End -->
    </div>
    <div class='row'>
      <div class="col-md-12">
        %s
      </div>
    </div>
    <div class='row'>
      <div class="col-md-1 tabs-left">
      <ul class="nav nav-tabs" id="Publications" role="tablist">%s</ul>
      </div>
      <div class="col-md-10">
      <div class="tab-content">%s""" % (Head, Side_Tab, Content)
  Footer_HTML = """</div></div>
    </div>
  </div>
  <br>
  {% endblock %}
  """
  return Recent, Header_HTML + Footer_HTML





# Here will be the shasum and the content of the newly edited publications
Edited_File  = open("/var/www/vhosts/lcp.mit.edu/html/lcp_references.html", 'rb').read()
Download_SHA = sha256(Edited_File).hexdigest()

# Here we get the shasum of the older references file 
File_SHA = sha256(open("/var/www/vhosts/lcp.mit.edu/Flask/templates/lcp_references.html", 'rb').read()).hexdigest()

# Here we read Latest shasum of the references file
SHA = open("/var/www/vhosts/lcp.mit.edu/Flask/shasum.references", 'r').read()


if (SHA != File_SHA or SHA != Download_SHA or Download_SHA != File_SHA) or True:
  open("/var/www/vhosts/lcp.mit.edu/Flask/shasum.references", 'w').write(File_SHA)

  Recent, Content = File_Change(Edited_File)

  New_File = open("/var/www/vhosts/lcp.mit.edu/Flask/templates/publications.html", "w").write(Content)
  Upadate_File = open("/var/www/vhosts/lcp.mit.edu/Flask/templates/lcp_references.html", 'w').write(Edited_File)


  Recent_File = open("/var/www/vhosts/lcp.mit.edu/Flask/templates/recent_publications.html", "w")
  for indx, item in enumerate(Recent):
    if indx < 4:
      Recent_File.write(item)
  Recent_File.close()
  print ("CHANGE DONE")
else:
  print ("No changes to be done\nThe current shasum of the files are the following:")
  print ("- The latest  file: \t{0}".format(Download_SHA))
  print ("- The current file: \t{0}".format(File_SHA))
  print ("- The stored shasum: \t{0}".format(SHA))
