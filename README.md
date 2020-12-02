# Programming-Languages-DBPedia

Steps for getting up and running<br>
Download the latest version of Python from this link:<br>
https://www.python.org/downloads/<br>

Open command prompt<br>
Run this to install Juypter Notebook<br>
python -m pip install jupyter<br>

Run this in a Jupyter Notebook segment to install SPARQL Client for Python<br>
!pip install sparql-client<br>

Run Jupyter Notebook<br>
Use the upload option to add the .ipynb file from the repository to edit in Jupyter<br>

# Installation/development

To run this web server for development you must 
1. Have `make` installed.
2. Have Python 3 and pip 3 installed: https://www.python.org/downloads/, https://pip.pypa.io/en/stable/installing/.
3. Have Flask installed, `pip install Flask`.
4. Have the Python SPARQL client installed, `pip install sparql-client`

One installation is complete you can run the makefile commands to start the web
server. Open a terminal in the projects working directory, then run `make` you
will now be able to visit http://localhost:5000/. 
