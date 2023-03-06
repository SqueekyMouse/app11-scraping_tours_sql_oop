import requests
import selectorlib
import os
import smtplib, ssl
import time
import sqlite3
# commit: Initial commit Sec40

# "INSERT INTO events VALUES ('Tigers','Tiger City','2088.10.14')"
# "SELECT * FROM events WHERE date='2088.10.15'"
# "DELETE FROM events WHERE band='Tigres'"

URL='http://programmer100.pythonanywhere.com/tours/'
# some servers dont allow scraping so supply headers if necessary!!!
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Establish a connection
dbconnection=sqlite3.connect('data.sqlite')

def scrape(url):
    """Scrape the page source from the url"""
    response=requests.get(url, headers=HEADERS)
    source=response.text
    return(source)

def extract(source):
    extractor=selectorlib.Extractor.from_yaml_file('extract.yaml')
    value=extractor.extract(source)['tours'] # tours key is set in the yaml file val is tag '#displaytimer'
    # #displaytimer - copied from firefox > page > inspector > copy css selector!!!
    return(value)

def send_email(message):
    host='smtp.gmail.com'
    port=465
    username='appuser565@gmail.com'
    password=os.getenv('APP_M_PASSWORD')
    receiver='appuser565@gmail.com'
    context=ssl.create_default_context()
    
    with smtplib.SMTP_SSL(host=host,port=port,context=context) as server:
        server.login(user=username,password=password)
        server.sendmail(from_addr=username,to_addrs=receiver,msg=message)

def store(extracted):
    row=extracted.split(',')
    row=[item.strip() for item in row]
    cursor=dbconnection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)",row)
    dbconnection.commit()

def read(extracted):
    # Feng Suave, Minimalia City, 5.5.2089
    row=extracted.split(',')
    row=[item.strip() for item in row]
    band,city,date=row
    cursor=dbconnection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?",
                    (band,city,date))
    rows=cursor.fetchall()
    print(rows)
    return(rows)

if __name__=='__main__':
    while True:
        scraped=scrape(URL)
        extracted=extract(scraped)
        print(extracted)
        
        if extracted!='No upcoming tours':
            row=read(extracted) # to check if its already present in db
            if not row: # check for empty list!!! non-empty is True, empty is False!!!
                store(extracted) 
                send_email(message='Hey, new event was found')
        time.sleep(2)
