import urllib.request as url
from bs4 import BeautifulSoup as bs
import pandas as pd


# add link into the new_link stack
def fetch_links(address, new, old, stack_size):
    print(address)

    try:
        response = url.urlopen(address)
        if response.getcode() != 200:
            print('bad url')
            return
        content = response.read()
        soup = bs(content, 'html.parser')
        links = soup.find_all('a')
    
        for l in links:
            try:
                link = l['href']
                if link[:5] == 'http:':
                    if link not in old:
                        new.add(link)
                        if len(new) >= stack_size:
                            return
            except:
                print("No href in a")
    except:
        print("bad URL")
        
        
def crawl(initial_link, iter_num, stack_size):
    old_url = set()
    new_url = set()

    new_url.add(initial_link)
    while iter_num > 0 and len(new_url) != 0:
        link = new_url.pop()
        old_url.add(link)
        fetch_links(link, new_url, old_url, stack_size)
        iter_num -= 1

        print('number of new urls:' + str(len(new_url)) + '   size of selected urls:' + str(len(old_url)))

    return old_url


def save_links(links, csv_name):
    df = pd.DataFrame(columns=['link'])
    for i, l in enumerate(links):
        df.loc[i] = l
    df.to_csv(csv_name)
