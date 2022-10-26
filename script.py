from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import gspread
import string


def chuanHoa(price:string) -> float:
    length = len(price)
    prefix = price[-1]

    if prefix == 'B':
        val = float(price[1:length-1])
        return val*1000000000
    elif prefix == 'M':
        val = float(price[1:length-1])
        return val*1000000
    elif prefix == 'K':
        val = float(price[1:length-1])
        return val*1000
    else:
        val = float(price[1:])
        return val


def request(url):
    setup = requests.Session()
    setup.headers['User-Agent'] = 'Chrome/103.0.5060.114' # version of chrome 
    page = setup.get(url)
    soup = BeautifulSoup(page.content ,'html.parser')
    return soup


def parse(soup):
    time_stamp = datetime.now()
    time_stamp = time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    data = soup.find('div', class_="lcw-table-container main-table").find('tbody').find_all('tr')[0]

    sym = data.find('div', class_="filter-item-name mb0 text-left").text
    name = data.find('small', class_="abr text-truncate").text
    main_price = data.find('td', class_= "filter-item table-item main-price").text
    MarketCap = data.find('td', class_= "filter-item table-item price").text
    VolumePrice = data.find('td', class_= "filter-item table-item volume price").text
    Liquidity =  data.find_all('td', class_= "filter-item table-item")[1].text
    AllTimeHeight =  data.find('td', class_= "filter-item table-item ath-col").text
 
    sym = sym[0:3]
        
    mainVal = chuanHoa(main_price)
    MarketCapVal = chuanHoa(MarketCap)
    VolmeValue = chuanHoa(VolumePrice)
    LiqidityVal = chuanHoa(Liquidity)
    AllTimeVal = chuanHoa(AllTimeHeight)

    product = { 'Time':time_stamp,
                'Symbol': sym,
                'Name': name,
                'Price': mainVal,
                'Marketcap' : MarketCapVal,
                'Volume 24h' : VolmeValue,
                'Liqidity ~2%' : LiqidityVal,
                'All-time High': AllTimeVal }
    return product


def getLogo(coin):
    link = coin.find('a', class_='text-left')
    retLink = ''
    if 'href' in link.attrs:
        retLink = link.attrs['href']
    
    return retLink


def output(product):
    gc = gspread.service_account(filename='creeps.json')
    sheet = gc.open('scrapSheets').sheet1

    sheet.append_row( [
        str(product['Time']),
        str(product['Symbol']),
        str(product['Name']),
        float(product['Price']),
        float(product['Marketcap']),
        float(product['Liqidity ~2%']),
        float(product['All-time High']) ])
    return

def main():
    while True: 
        data = request('https://www.livecoinwatch.com/trending')
        product = parse(data)
        output(product)
        sleep(4) 

if __name__ == '__main__':
    main()

