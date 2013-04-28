import os
from bs4 import BeautifulSoup
import urllib

path = '../../data/'
os.chdir(path)

soup = BeautifulSoup(urllib.urlopen("http://www.asxhistoricaldata.com/").read())
links = soup.findAll('a')
zips = []
for link in links:
    link = link['href']
    if link.endswith("zip"):
        filename = link.split('/')[-1]
        if not os.path.isfile(filename):
            zips.append((link, filename))


for z in zips:
    os.system('wget %s -O %s' % z)
    os.system('unzip %s' % z[1])
    os.unlink(z[1])
