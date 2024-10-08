import requests
import csv
import configparser
import telebot
import os
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup

dir_path = (os.path.dirname(__file__))

def check_series_date(name,date):
    sleep(10)

    url = "https://kinozal.tv/browse.php?s="+name

    print ("-----------------------------------")
    print ("Checking " + name + " since " + date)

    try:
        request = requests.get(url, timeout = 5)
        html = request.content
        soup = BeautifulSoup(html, 'html.parser')
        html_data = soup.find_all('td', attrs={'class': 's'})

        last_date = (html_data[2].text[:11]).strip()
        if last_date[:5] == "вчера" or last_date[:5] == "сегод":
            last_date = datetime.now().date()
        else:
            last_date = datetime.strptime(last_date, '%d.%m.%Y').date()

        full_name = soup.find('a', attrs={'class': 'r1'}).text

    except Exception as e:
        print (f"Error: {e}")
        return (datetime.strptime(date, '%Y-%m-%d').date(), name)

    return (last_date, full_name)

def get_series_list():
    with open(f'{dir_path}/checklist.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data

def save_series_list(data):
    with open(f'{dir_path}/checklist.csv', 'w') as csvfile:
        fieldnames = ['search_name', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    # Load config
    config = configparser.ConfigParser()
    config.read(f'{dir_path}/settings.ini')
    bot = telebot.TeleBot(config['Telegram']['token'])
    myid = int(config['Telegram']['myid'])
    
    data = get_series_list()

    for indx, elem in enumerate(data):
        last_date, full_name = check_series_date(elem['search_name'], elem['date'])
        if last_date > datetime.strptime(elem['date'], '%Y-%m-%d').date():
            data[indx]['date'] = last_date.strftime('%Y-%m-%d')
            bot.send_message(myid, f"Вышла новая серия: {full_name} - {last_date}")
            print (f"New episode for {full_name} - {last_date}")
    
    save_series_list(data)
