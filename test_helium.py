import helium
from bs4 import BeautifulSoup
import time

url = 'https://www.weather.gov/wrh/timeseries?site=CLN&headers=min&obs=raw&hourly=true&pview=full&history=yes&start=20231128&end=20231202'

browser = helium.start_chrome(url, headless = False)

time.sleep(0.5)

soup = BeautifulSoup(browser.page_source, 'html.parser')

table = soup.find('table')

print(table)