import requests
# get the source code from webpage and store as a string

import selectorlib
# extract particular info from that source code

import smtplib
# For sending emails

import os
from email.message import EmailMessage
from dotenv import load_dotenv
import time
import sqlite3

load_dotenv()

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

connection = sqlite3.connect("data.db")
# outside the function so it doesn't keep repeating in the loop


def scrape(url):
    # scrape page source from URL
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["my_data"]
    return value


def send_email(message):
    email_message = EmailMessage()
    email_message["subject"] = "New Event Found..."
    email_message.set_content(message)

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(os.getenv('SENDER'), os.getenv('PASSWORD'))
    gmail.sendmail(os.getenv('SENDER'), os.getenv('RECEIVER'), email_message.as_string())
    gmail.quit()


# When only using txt file
# def store(value):
#     with open("data.txt", "a") as file:
#         file.write(value + "\n")
# def read():
#     with open("data.txt", "r") as file:
#         return file.read()


def store(new_item):
    data = new_item.split(",")
    data = [item.strip() for item in data]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events(band, city, date) VALUES(?,?,?)", data)
    connection.commit()


def read(new_item):
    data = new_item.split(",")
    print(data)
    data = [item.strip() for item in data]
    band, city, date = data
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city =? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(extracted)
        time.sleep(2)
