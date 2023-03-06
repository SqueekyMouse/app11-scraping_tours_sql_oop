import requests
import selectorlib
import os
import smtplib, ssl
import time
import sqlite3
# commit: add Database class class Sec40

URL='http://programmer100.pythonanywhere.com/tours/'
# some servers dont allow scraping so supply headers if necessary!!!
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class Event:
    def scrape(self,url):
        """Scrape the page source from the url"""
        response=requests.get(url, headers=HEADERS)
        source=response.text
        return(source)

    def extract(self,source):
        extractor=selectorlib.Extractor.from_yaml_file('extract.yaml')
        value=extractor.extract(source)['tours'] # tours key is set in the yaml file val is tag '#displaytimer'
        # #displaytimer - copied from firefox > page > inspector > copy css selector!!!
        return(value)


class Email:
    def send(self,message):
        host='smtp.gmail.com'
        port=465
        username='appuser565@gmail.com'
        password=os.getenv('APP_M_PASSWORD')
        receiver='appuser565@gmail.com'
        context=ssl.create_default_context()
        
        with smtplib.SMTP_SSL(host=host,port=port,context=context) as server:
            server.login(user=username,password=password)
            server.sendmail(from_addr=username,to_addrs=receiver,msg=message)


class Database:

    def __init__(self,db_path):
        self.dbconnection=sqlite3.connect(db_path)

    def store(self,extracted):
        row=extracted.split(',')
        row=[item.strip() for item in row]
        cursor=self.dbconnection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)",row)
        self.dbconnection.commit()

    def read(self,extracted):
        # Feng Suave, Minimalia City, 5.5.2089
        row=extracted.split(',')
        row=[item.strip() for item in row]
        band,city,date=row
        cursor=self.dbconnection.cursor()
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?",
                        (band,city,date))
        rows=cursor.fetchall()
        print(rows)
        return(rows)


if __name__=='__main__':
    while True:
        event=Event()
        scraped=event.scrape(URL)
        extracted=event.extract(scraped)
        print(extracted)
        
        if extracted!='No upcoming tours':
            database=Database(db_path='data.db') #class getting an arg!!!
            row=database.read(extracted) # to check if its already present in db
            if not row: # check for empty list!!! non-empty is True, empty is False!!!
                database.store(extracted)
                email=Email()
                email.send(message='Hey, new event was found')
        time.sleep(2)
