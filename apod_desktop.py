""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author       Description
  2022-03-11  J.Dalby      Initial creation
  2022-04-29  C.Tompsett   Added functionality to the script
"""
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
from os import path
from urllib import request
import requests
import re
import sqlite3

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = apod_dict['hdurl']
#   image_msg = apod_dict['explanation']
    image_msg = download_apod_image(image_url)
    image_sha256 = sha256(download_apod_image(image_url)).hexdigest()
    image_size = len(download_apod_image(image_url))
    image_path = get_image_path(image_url, image_dir_path)

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)
  
    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256,apod_dict)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def create_image_db(db_path):
    
    
    #Creates an image database if it doesn't already exist.
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()

#Creates the table where the apod information will be stored in the database
    Create_Table = """CREATE TABLE IF NOT EXISTS apod (
                      id integer PRIMARY KEY,
                      Name text NOT NULL,
                      Location text NOT NULL,
                      File_Size integer NOT NULL,
                      SHA256 text NOT NULL,
                      Date_Added date NOT NULL
                    );"""

    myCursor.execute(Create_Table)
#commits the changes to the db and then closes it   
    myConnection.commit()
    myConnection.close()
  
    return

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
#uses a regex to make the name of the file more manageable and readable for the user
    match =re.search(r'.*/(.*)', image_url )
    short_name = match.group(1)

#adds the image to the folder specified by the user
    save_spot = dir_path + "\\" + short_name

    return(save_spot)

def get_apod_info(date): 
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.
    """
#making the http request to the NASA APOD API    
    api_key = "oWaOkx1MjdytmIa9VcVA74jpek7Qe7ippCfbKgr2"
    Apod_photo = requests.get("https://api.nasa.gov/planetary/apod?api_key="+api_key+"&date="+date)

#makes the http request in to a dictionary
    apod_dict = Apod_photo.json()
    
    
    return(apod_dict)

def print_apod_info(image_url, image_path, image_size, image_sha256):
    
    #Prints useful information to the CLI to inform the user of
    #what is happening during the process of runnnign the program

    print("Retrieving the image from", image_url, "\n ")
    print("The image will be stored at", image_path, "\n")
    print("The image is", image_size,"bytes \n") 
    print("The sha256 value of the image is", image_sha256,"\n")
    
        
    return

def download_apod_image(image_url):

#Downloads an image from a specified URL. and returns the binary string of the image
    get_image = requests.get(image_url)
    image_data= get_image.content
    



    return (image_data)

def save_image_file(image_msg, image_path):

    #saves image that was downloaded from the url
    with open(image_path, 'wb') as fp:
        fp.write(image_msg)

    return

def add_image_to_db(db_path, image_path, image_size, image_sha256,apod_dict):
    """
    Adds a specified APOD image to the DB.
    """
#used datetime to add a specific time the APOD was added to the db
    from datetime import datetime

#connecting to the db
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()

#makes the query requirments for the image    
    new_apod_query="""INSERT INTO apod (
                      Name, 
                      Location, 
                      File_size, 
                      SHA256, 
                      Date_Added)
                   VALUES (?, ?, ?, ?, ?);"""

#adds the information about the APOD to the db 
    new_apod = ( apod_dict["title"], 
                image_path, 
                image_size, 
                image_sha256, 
                datetime.now())
    
    myCursor.execute(new_apod_query, new_apod)
#commits changes to the db and closes it
    myConnection.commit()
    myConnection.close()
    
    return

def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.
    """ 
    print("Checking Database...",end=" ")

    myConnection = sqlite3.connect(db_path)
    my_cursor = myConnection.cursor()

#grabs the SHA256 entries from the db
    image_check_query = """SELECT SHA256 from apod"""

    my_cursor.execute(image_check_query)
    results = my_cursor.fetchall()

#compares the SHA256 of the downloaded image to the ones in the db. Saves it if not in the db, if it is in db it does nothing
    for compare_sha256 in results:
        if compare_sha256[0] == image_sha256:
            print("Image already in database")
            myConnection.close()
            return(True)
    
    print("Image saved to database")    
    
    return(False)
     
def set_desktop_background_image(image_path):
    import ctypes
    """
    Changes the desktop wallpaper to a specific image.

    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

    return

main()