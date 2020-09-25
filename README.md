#Extraction Tool 

Requirements: 
* python, version: 3.7, https://www.python.org/downloads/ 
* pip3 install redis numpy pandas sklearn 
* start redis service 
 
Requirements in more detail: 
* beautifulsoup4 (bs4), version: 4.8.0 (downloaded via pip3) 
* numpy, version: 1.17.4 (downloaded via pip3) 
* pandas, version: 0.25.3 (downloaded via pip3) 
* sklearn, version: 0.25.3 (downloaded via pip3) 
 
Adapting the path in main.py: 
* config_path = path to project directory 
 
Input parameters if tool is used as a standalone command-line tool: 
* uuid = unique identifier consisting of up to 4 numbers, can be set randomly 
* path to the PDF file 
* redis parameters e.g. "localhost" 
* (optional) a custom EPS 
 

run from the command line, or called by another application: 
by using the command ”python3 main.py” with the needed input parameters e.g. "python3 main.py [uuid] [filepath] [db_config] [optional eps parameter]"  
 
 
