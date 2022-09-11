#this scraper scrapes title and uses it to search the site and grab a cover from the search results, among other things
import base64
import datetime
import json
import re
import sys
import urllib.parse
# extra modules below need to be installed
try:
    import py_common.log as log
except ModuleNotFoundError:
    print("You need to download the folder 'py_common' from the community repo! (CommunityScrapers/tree/master/scrapers/py_common)", file=sys.stderr)
    sys.exit()

try:
    import cloudscraper
except ModuleNotFoundError:
    log.error("You need to install the cloudscraper module. (https://pypi.org/project/cloudscraper/)")
    log.error("If you have pip (normally installed with python), run this command in a terminal (cmd): pip install cloudscraper")
    sys.exit()
    
try:
    from lxml import html, etree
except ModuleNotFoundError:
    log.error("You need to install the lxml module. (https://lxml.de/installation.html#installation)")
    log.error("If you have pip (normally installed with python), run this command in a terminal (cmd): pip install lxml")
    sys.exit()

STUDIO_MAP = {
    'https://missax.com/tour/': 'MissaX',
    'https://allherluv.com/tour/': 'All Her Luv',
}

proxy_list = {
    }
timeout = 10

def scraped_content(scraper, url):
    try:
        scraped = scraper.get(url, timeout=timeout, proxies=proxy_list)
    except:
        log.error("scrape error")
    if scraped.status_code >= 400:
        log.error('HTTP Error: %s' % scraped.status_code)
    return scraped.content

def scrape_scene_page(url): #scrape the main url
    tree = scraped_content(scraper, url) #get page content
    tree = html.fromstring(tree) #parse html
    title = tree.xpath('//p[@class="raiting-section__title"]/text()')[0].strip() #title scrape
    log.trace(f'Title:{title}')
    date = tree.xpath('//p[@class="dvd-scenes__data"][1]/text()[1]')[0] #get date
    date = re.sub("(?:.+Added:\s)([\d\/]*).+", r'\g<1>', date).strip() #date cleanup
    date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d") #date parse
    log.trace(f'Date:{date}')
    studio = tree.xpath('//base/@href')[0].strip() #studio scrape
    studio = STUDIO_MAP[studio] # studio map
    log.trace(f'Studio:{studio}')
    performers = tree.xpath('//p[@class="dvd-scenes__data"][1]/a/text()') #performers scrape
    log.trace(f'Performers:{performers}')
    tags = tree.xpath('//p[@class="dvd-scenes__data"][2]/a/text()') #tags scrape
    log.trace(f'Tags:{tags}')
    details = tree.xpath('//p[count(preceding-sibling::p[@class="dvd-scenes__title"])=1]/text()|//p[@class="text text--marg"]/strong/text()|//p/em/text()') #details scrape
    details = ''.join(details) #join details
    details = '\n'.join(' '.join(line.split()) for line in details.split('\n')) #get rid of double spaces
    details = re.sub("\r?\n\n?", r'\n', details) #get rid of double newlines
    log.trace(f'Details:{details}')
    bad_cover_url = tree.xpath("//img[@src0_4x]/@src0_4x") #cover from scene's page if better one is not found (it will be)
    datauri = "data:image/jpeg;base64,"
    b64img = scrape_cover(scraper, studio, title, bad_cover_url)
    return output_json(title,tags,date,details,datauri,b64img,studio,performers)


def scrape_cover(scraper, studio, title, bad_cover_url):
    p = 1
    # loop throught search result pages until img found
    while p<20:
        log.trace(f'Searching page {p} for cover')
        url = 'https://'+studio.replace(" ", "")+'.com/tour/search.php?query='+urllib.parse.quote(title)+f'&page={p}'
        tree = scraped_content(scraper, url) #get page content
        tree = html.fromstring(tree) #parse html
        if tree.xpath('//*[@class="photo-thumb video-thumb"]'): #if any search results present
            try:
                imgurl = tree.xpath(f'//img[@alt="{title}"]/@src0_4x')[0]
                img = scraped_content(scraper, imgurl)
                b64img = base64.b64encode(img)
                log.trace('Cover found!')
                return b64img
            except:
                if tree.xpath('//li[@class="active"]/following-sibling::li'): #if there is a next page
                    p+=1
                else:
                    break
        else:
            break
    #just a failsafe
    log.warning('better cover not found, returning the bad one')
    img = scraped_content(scraper, bad_cover_url)
    b64img = base64.b64encode(img)
    return b64img
    


def output_json(title,tags,date,details,datauri,b64img,studio,performers):
    return {
    'title': title,
    'tags': [{
        'name': x
    } for x in tags],
    'date': date,
    'details': details.strip(),
    'image': datauri + b64img.decode('utf-8'),
    'studio': {
        'name': studio
    },
    'performers': [{
        'name': x.strip()
    } for x in performers]
}



# frag = {"url": "https://allherluv.com/tour/trailers/Like-I-Do.html"}

frag = json.loads(sys.stdin.read())
if not frag['url']:
    log('No URL entered.')
url = frag["url"]

scraper = cloudscraper.create_scraper()
ret = scrape_scene_page(url)
print(json.dumps(ret))


# Based on the PerfectGonzo scraper
# Last Updated September 11, 2022
