import base64
import datetime
import json
import re
import sys
import threading
import time
from urllib.parse import urlparse

import lxml.html    # https://pypi.org/project/lxml/         | pip install lxml
import requests     # https://pypi.org/project/requests/     | pip install requests

R18_HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
    "Referer": "https://www.r18.com/"
}
JAV_HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
    "Referer": "http://www.javlibrary.com/"
}
# Print debug message
DEBUG_MODE = True
# We can't add movie image atm in same time as Scene
STASH_SUPPORTED = False
# Tags you don't want to see appear in Scraper window
IGNORE_TAGS = ["Features Actress", "Digital Mosaic", "Hi-Def", "Risky Mosaic",
               "Beautiful Girl", "Blu-ray", "Featured Actress", "VR Exclusive", "MOODYZ SALE 4"]
# Some performer don't need to be reversed
IGNORE_PERF_REVERSE = ["Lily Heart"]
# Tag you always want in Scraper window
FIXED_TAGS = ""
# Take Javlibrary and R18 tags
BOTH_TAGS = False
# Don't care about getting the Aliases (Japanese Name)
IGNORE_ALIASES = False
# Always wait for the aliases or you are not sure to have it. (Depends if request are quick)
WAIT_FOR_ALIASES = False
# Mirror to use
JAVLIBRARY_MIRROR = "n53i.com"

BANNED_WORDS = {
    "A*****t": "Assault",
    "A*****ted": "Assaulted",
    "A****p": "Asleep",
    "A***e": "Abuse",
    "A***ed": "Abused",
    "A***es": "Abuses",
    "B*****k": "Berserk",
    "B*****p": "Bang Up",
    "B***d": "Blood",
    "B***dy": "Bloody",
    "B******y": "Brutally",
    "C*****y": "Cruelty",
    "C***d": "Child",
    "C***dcare": "Childcare",
    "C***dhood": "Childhood",
    "C***dish": "Childish",
    "C***dren": "Children",
    "C*ck": "Cock",
    "C*cks": "Cocks",
    "C*llegiate": "Collegiate",
    "Chai*saw": "Chainsaw",
    "CrumB**d": "Crumbled",
    "D*ck": "Dick",
    "D******e": "Disgrace",
    "D******ed": "Disgraced",
    "D******eful": "Disgraceful",
    "D***k": "Drunk",
    "D***ken": "Drunken",
    "D***kest": "Drunkest",
    "D***king": "Drinking",
    "D***ks": "Drinks",
    "D**g": "Drug",
    "D**gged": "Drugged",
    "D**gs": "Drugs",
    "EnS***ed": "Enslaved",
    "F*****g": "Fucking",
    "F***e": "Force",
    "F***ed": "Fucked",
    "F***eful": "Forceful",
    "F***efully": "Forcefully",
    "F***es": "Forces",
    "G*********d": "Gang-Banged",
    "G*******g": "Gangbang",
    "G*******ged": "Gangbanged",
    "G*******ging": "Gangbanging",
    "G******ging": "Gangbanging",
    "G*******gs": "Gangbangs",
    "G******g": "Gangbang",
    "G******ged": "Gangbanged",
    "G****gers": "Gangbangers",
    "H*********n": "Humiliation",
    "H*******ed": "Hypnotized",
    "H*******m": "Hypnotism",
    "H**t": "Hurt",
    "H**ts": "Hurts",
    "Half-A****p": "Half-Asleep",
    "HumB**d": "Humbled",
    "I****t": "Incest",
    "I****ts": "Insults",
    "I****tuous": "Incestuous",
    "J*": "Jo",
    "J*s": "Jos",
    "K****pped": "Kidnapped",
    "K****pper": "Kidnapper",
    "K****pping": "Kidnapping",
    "K**l": "Kill",
    "K**led": "Killed",
    "K**ler": "Killer",
    "K**ling": "Killing",
    "K*d": "Kid",
    "K*dding": "Kidding",
    "K*ds": "Kids",
    "Lo**ta": "Lolita",
    "Lol*pop": "Lolipop",
    "M****t": "Molest",
    "M****tation": "Molestation",
    "M****ted": "Molested",
    "M****ter": "Molester",
    "M****ters": "Molesters",
    "M****ting": "Molesting",
    "M****tor": "Molestor",
    "Ma*ko": "Maiko",
    "P****h": "Punish",
    "P****hment": "Punishment",
    "P**hed": "Punished",
    "P*ssy": "Pussy",
    "R****g": "Raping",
    "R**e": "Rape",
    "R**ed": "Raped",
    "R**es": "Rapes",
    "S*********l": "School Girl",
    "S*********ls": "School Girls",
    "S*********s": "Schoolgirls",
    "S********l": "Schoolgirl",
    "S********ls": "Schoolgirls",
    "S********n": "Submission",
    "S******g": "Sleeping",
    "S*****t": "Student",
    "S*****ts": "Students",
    "S***e": "Slave",
    "S***ery": "Slavery",
    "S***es": "Slaves",
    "Sch**lgirl": "Schoolgirl",
    "Sch**lgirls": "Schoolgirls",
    "SK**led": "Skilled",
    "SK**lful": "Skillful",
    "SK**lfully": "Skillfully",
    "SK**ls": "Skills",
    "StepB****************r": "StepBrother And Sister",
    "StepK*ds ": "StepKids",
    "StepM************n": "Stepmother And Son",
    "T******e": "Tentacle",
    "T******es": "Tentacles",
    "T*****e": "Torture",
    "T*****ed": "Tortured",
    "T*****es": "Tortures",
    "U*********sly": "Unconsciously",
    "U*******g": "Unwilling",
    "V******e": "Violence",
    "V*****e": "Violate",
    "V*olated": "Violated",
    "V*****ed": "Violated",
    "V*****es": "Violates",
    "V*****t": "Violent",
    "Y********l": "Young Girl",
    "Y********ls": "Young Girls"
}


def debug(q):
    if "[DEBUG]" in q and DEBUG_MODE == False:
        return
    print(q, file=sys.stderr)


def sendRequest(url, head):
    global maintenance_javlibrary
    global flag_cloudflare

    if maintenance_javlibrary == True and ("javlibrary.com" in url or JAVLIBRARY_MIRROR in url):
        return None
    if flag_cloudflare == True and "javlibrary.com" in url:
        return None
    debug("[DEBUG][{}] Request URL: {}".format(threading.get_ident(), url))
    for x in range(0, 3):
        response = requests.get(url, headers=head, timeout=10)
        #print(response.text, file=open("request.txt", "w", encoding='utf-8'))
        #debug("[DEBUG][{}] Returned URL: {}".format(threading.get_ident(),response.url))
        if response.content and response.status_code == 200:
            break
        else:
            if response.url == "https://www.javlib.com/maintenance.html":
                debug("[WARN] Javlibrary is Under Maintenance.")
                maintenance_javlibrary = True
                return None
            if "Why do I have to complete a CAPTCHA?" in response.text or "Checking your browser before accessing" in response.text:
                debug("[WARN] Cloudflare protection detected.")
                flag_cloudflare = True
                return None
            debug("[{}] Bad page...".format(x))
            time.sleep(5)
    if response.status_code == 200:
        pass
    else:
        debug("[Request] Error, Status Code: {}".format(response.status_code))
        response = None
    return response


def replace_banned_words(matchobj):
    word = matchobj.group(0)
    if word in BANNED_WORDS:
        return BANNED_WORDS[word]
    else:
        return word

def regexreplace(input):
    word_pattern = re.compile('(\w|\*)+')
    output = word_pattern.sub(replace_banned_words, input)
    return re.sub(r"[\[\]\"]", "", output)


def getxpath(xpath, tree):
    xPath_result = []
    # It handle the union strangely so it better to split and do one by one
    if "|" in xpath:
        for xpath_tmp in xpath.split("|"):
            xPath_result.append(tree.xpath(xpath_tmp))
        xPath_result = [val for sublist in xPath_result for val in sublist]
    else:
        xPath_result = tree.xpath(xpath)
    #debug("xPATH: {}".format(xpath))
    #debug("raw xPATH result: {}".format(xPath_result))
    list_tmp = []
    for a in xPath_result:
        # for xpath that don't end with /text()
        if type(a) is lxml.html.HtmlElement:
            list_tmp.append(a.text_content().strip())
        else:
            list_tmp.append(a.strip())
    if list_tmp:
        xPath_result = list_tmp
    xPath_result = list(filter(None, xPath_result))
    return xPath_result

# SEARCH PAGE


def r18_search(html, xpath):
    r18_search_tree = lxml.html.fromstring(html.content)
    r18_search_url = getxpath(xpath['url'], r18_search_tree)
    r18_search_serie = getxpath(xpath['series'], r18_search_tree)
    r18_search_scene = getxpath(xpath['scene'], r18_search_tree)
    # There is only 1 scene, with serie.
    # Could be useful is the movie already exist in Stash because you only need the name.
    if len(r18_search_scene) == 1 and len(r18_search_serie) == 1 and len(r18_search_url) == 1:
        r18_result["series_name"] = r18_search_serie
    if r18_search_url:
        r18_search_url = r18_search_url[0]
        r18_id = re.match(r".+id=(.+)\/.+", r18_search_url)
        if r18_id:
            scene_url = "https://www.r18.com/api/v4f/contents/{}?lang=en".format(r18_id.group(1))
            debug("[DEBUG] Using API URL: {}".format(scene_url))
            r18_main_html = sendRequest(scene_url, R18_HEADERS)
        else:
            debug("[WARN] Can't find the 'id=' in the URL: {}".format(r18_search_url))
            return None
        return r18_main_html
    else:
        debug("[R18] There is no result in search")
        return None


def jav_search(html, xpath):
    if "/en/?v=" in html.url:
        debug("[DEBUG] No search page, directly the movie page ({})".format(html.url))
        return html
    jav_search_tree = lxml.html.fromstring(html.content)
    jav_url = getxpath(xpath['url'], jav_search_tree)  # ./?v=javme5it6a
    if jav_url:
        url_domain = urlparse(html.url).netloc
        jav_url = re.sub(r"^\.", "https://{}/en".format(url_domain), jav_url[0])
        jav_main_html = sendRequest(jav_url, JAV_HEADERS)
        return jav_main_html
    else:
        debug("[JAV] There is no result in search")
        return None


def buildlist_tagperf(data, type_scrape=""):
    list_tmp = []
    dict_jav = None
    if type_scrape == "perf_jav":
        dict_jav = data
        data = data["performers"]
    for i in range(0, len(data)):
        y = data[i]
        if y == "":
            continue
        if type_scrape == "perf_jav":
            if y not in IGNORE_PERF_REVERSE:
                # Invert name (Aoi Tsukasa -> Tsukasa Aoi)
                y = re.sub(r"([a-zA-Z]+)(\s)([a-zA-Z]+)", r"\3 \1", y)
        if type_scrape == "tags" and y in IGNORE_TAGS:
            continue
        if type_scrape == "perf_jav" and dict_jav.get("performer_aliases"):
            try:
                list_tmp.append({"name": y, "aliases": dict_jav["performer_aliases"][i]})
            except:
                list_tmp.append({"name": y})
        else:
            list_tmp.append({"name": y})
    # Adding personal fixed tags
    if FIXED_TAGS and type_scrape == "tags":
        list_tmp.append({"name": FIXED_TAGS})
    return list_tmp


def th_request_perfpage(page_url, perf_url):
    # vl_star.php?s=afhvw
    #debug("[DEBUG] Aliases Thread: {}".format(threading.get_ident()))
    javlibrary_ja_html = sendRequest(page_url.replace("/en/", "/ja/"), JAV_HEADERS)
    if javlibrary_ja_html:
        javlibrary_perf_ja = lxml.html.fromstring(javlibrary_ja_html.content)
        list_tmp = []
        try:
            for i in range(0, len(perf_url)):
                list_tmp.append(javlibrary_perf_ja.xpath('//a[@href="' + perf_url[i] + '"]/text()')[0])
            if list_tmp:
                jav_result['performer_aliases'] = list_tmp
                debug("[DEBUG] Got the aliases: {}".format(list_tmp))
        except:
            debug("[DEBUG] Error with the aliases")
    else:
        debug("[DEBUG] Can't get the Jap HTML")
    return


def th_imagetoBase64(imageurl, typevar):
    #debug("[DEBUG] {} thread: {}".format(typevar,threading.get_ident()))
    head = JAV_HEADERS
    if typevar == "R18Series" or typevar == "R18":
        head = R18_HEADERS
    if type(imageurl) is list:
        for image_index in range(0, len(imageurl)):
            try:
                img = requests.get(imageurl[image_index].replace("ps.jpg", "pl.jpg"), timeout=10, headers=head)
                if img.status_code != 200:
                    debug("[Image] Got a bad request (status: {}) for <{}>".format(img.status_code,imageurl[image_index]))
                    imageurl[image_index] = None
                    continue
                base64image =  base64.b64encode(img.content)
                imageurl[image_index] = "data:image/jpeg;base64," + base64image.decode('utf-8')
            except:
                debug("[DEBUG][{}] Failed to get the base64 of the image".format(typevar))
        if typevar == "R18Series":
            r18_result["series_image"] = imageurl
    else:
        try:
            img = requests.get(imageurl.replace("ps.jpg", "pl.jpg"), timeout=10, headers=head)
            if img.status_code != 200:
                debug("[Image] Got a bad request (status: {}) for <{}>".format(img.status_code,imageurl))
                return
            base64image = base64.b64encode(img.content)
            if typevar == "JAV":
                jav_result["image"] = "data:image/jpeg;base64," + base64image.decode('utf-8')
            if typevar == "R18":
                r18_result["image"] = "data:image/jpeg;base64," + base64image.decode('utf-8')
            debug("[DEBUG][{}] Converted the image to base64!".format(typevar))
        except:
            debug("[DEBUG][{}] Failed to get the base64 of the image".format(typevar))
    return


#debug("[DEBUG] Main Thread: {}".format(threading.get_ident()))
fragment = json.loads(sys.stdin.read())
if fragment["url"]:
    scene_url = fragment["url"]
else:
    scene_url = None

if fragment.get("title"):
    scene_title = fragment["title"]
    # Remove extension
    scene_title = re.sub(r"\..{3}$", "", scene_title)
    scene_title = re.sub(r"-JG\d", "", scene_title)
    scene_title = re.sub(r"\s.+$", "", scene_title)
    scene_title = re.sub(r"[ABCDEFGH]$", "", scene_title)
else:
    scene_title = None

maintenance_javlibrary = False
flag_cloudflare = False

jav_search_html = None
r18_search_html = None
jav_main_html = None
r18_main_html = None

if scene_url:
    debug("[DEBUG] Using search with URL: {}".format(scene_url))
    if "javlibrary.com" in scene_url:
        jav_main_html = sendRequest(scene_url, JAV_HEADERS)
        if jav_main_html is None:
            scene_url = scene_url.replace("javlibrary.com", JAVLIBRARY_MIRROR)
    if JAVLIBRARY_MIRROR in scene_url:
        jav_main_html = sendRequest(scene_url, JAV_HEADERS)
    if "r18.com" in scene_url:
        r18_id = re.match(r".+id=(.+)\/.+", scene_url)
        if r18_id:
            scene_url = "https://www.r18.com/api/v4f/contents/{}?lang=en".format(r18_id.group(1))
            debug("[DEBUG] Using API URL: {}".format(scene_url))
            r18_main_html = sendRequest(scene_url, R18_HEADERS)
        else:
            debug("[WARN] Can't find the 'id=' in the URL: {}".format(scene_url))
if jav_main_html is None and r18_main_html is None:
    debug("[DEBUG] Using search with Title: {}".format(scene_title))
    jav_search_html = sendRequest("https://www.javlibrary.com/en/vl_searchbyid.php?keyword={}".format(scene_title), JAV_HEADERS)
    if jav_search_html is None:
        # A error for javlibrary, trying a mirror
        debug("[JAV] Error with Javlibrary, trying the mirror {}".format(JAVLIBRARY_MIRROR))
        jav_search_html = sendRequest("https://www.{}/en/vl_searchbyid.php?keyword={}".format(JAVLIBRARY_MIRROR, scene_title), JAV_HEADERS)

# XPATH
r18_xPath_search = {}
r18_xPath_search['series'] = '//p[text()="TOP SERIES"]/following-sibling::ul//a/span[@class="item01"]/text()'
r18_xPath_search['url'] = '//li[contains(@class,"item-list")]/a//img[string-length(@alt)=string-length(preceding::div[@class="genre01"]/span/text())]/ancestor::a/@href'
r18_xPath_search['scene'] = '//li[contains(@class,"item-list")]'

jav_xPath_search = {}
jav_xPath_search['url'] = '//div[@class="videos"]/div/a/@title[not(contains(.,"(Blu-ray"))]/../@href'

jav_xPath = {}
jav_xPath["title"] = '//td[@class="header" and text()="ID:"]/following-sibling::td/text()'
jav_xPath["details"] = '//div[@id="video_title"]/h3/a/text()'
jav_xPath["url"] = '//meta[@property="og:url"]/@content'
jav_xPath["date"] = '//td[@class="header" and text()="Release Date:"]/following-sibling::td/text()'
jav_xPath["tags"] = '//td[@class="header" and text()="Genre(s):"]/following::td/span[@class="genre"]/a/text()'
jav_xPath["performers"] = '//td[@class="header" and text()="Cast:"]/following::td/span[@class="cast"]/span/a/text()'
jav_xPath["performers_url"] = '//td[@class="header" and text()="Cast:"]/following::td/span[@class="cast"]/span/a/@href'
jav_xPath["studio"] = '//td[@class="header" and text()="Maker:"]/following-sibling::td/span[@class="maker"]/a/text()'
jav_xPath["image"] = '//div[@id="video_jacket"]/img/@src'
jav_xPath["r18"] = '//a[text()="purchasing HERE"]/@href'

r18_result = {}
jav_result = {}

if jav_search_html:
    jav_main_html = jav_search(jav_search_html, jav_xPath_search)
if jav_main_html is None:
    # If javlibrary don't have it, there is no way that R18 have it but why not trying...
    debug("Javlibrary don't give any result, trying search with R18...")
    r18_search_html = sendRequest("https://www.r18.com/common/search/searchword={}/?lg=en".format(scene_title), R18_HEADERS)
    r18_main_html = r18_search(r18_search_html, r18_xPath_search)

if jav_main_html:
    #debug("[DEBUG] Javlibrary Page ({})".format(jav_main_html.url))
    jav_tree = lxml.html.fromstring(jav_main_html.content)
    # Get data from javlibrary
    for key, value in jav_xPath.items():
        jav_result[key] = getxpath(value, jav_tree)
    # PostProcess
    if jav_result.get("image"):
        tmp = re.sub(r"(http:|https:)", "", jav_result["image"][0])
        jav_result["image"] = "https:" + tmp
        if "now_printing.jpg" in jav_result["image"] or "noimage" in jav_result["image"]:
            # https://pics.dmm.com/mono/movie/n/now_printing/now_printing.jpg
            # https://pics.dmm.co.jp/mono/noimage/movie/adult_ps.jpg
            debug("[Warning][Javlibrary] Image was deleted or fail to loaded ({})".format(jav_result["image"]))
            jav_result["image"] = None
        else:
            imageBase64_jav_thread = threading.Thread(target=th_imagetoBase64, args=(jav_result["image"], "JAV",))
            imageBase64_jav_thread.start()
    if jav_result.get("url"):
        jav_result["url"] = "https:" + jav_result["url"][0]
    if jav_result.get("details"):
        jav_result["details"] = re.sub(
            r"^(.*? ){1}", "", jav_result["details"][0])
    if jav_result.get("performers_url") and IGNORE_ALIASES == False:
        javlibrary_aliases_thread = threading.Thread(target=th_request_perfpage, args=(jav_main_html.url, jav_result["performers_url"],))
        javlibrary_aliases_thread.daemon = True
        javlibrary_aliases_thread.start()
    # R18
    if jav_result.get("r18"):
        r18_search_url = re.sub(r"^redirect\.php\?url=\/\/", "https://", jav_result["r18"][0])
        r18_search_html = sendRequest(r18_search_url, R18_HEADERS)
        r18_main_html = r18_search(r18_search_html, r18_xPath_search)

# MAIN PAGE
if r18_main_html:
    r18_main_api = r18_main_html.json()
    if r18_main_api["status"] != "OK":
        debug("[ERROR] API Status {}".format(r18_main_api.get("status")))
    else:
        r18_main_api = r18_main_api["data"]
        if r18_main_api.get("title"):
            r18_result['title'] = [r18_main_api["title"]]
        if r18_main_api.get("release_date"):
            r18_result['date'] = re.sub(r"\s.+", "", r18_main_api["release_date"])
        if r18_main_api.get("detail_url"):
            r18_result['url'] = r18_main_api["detail_url"]
        if r18_main_api.get("comment"):
            r18_result['details'] = "{}\n\n{}".format(r18_main_api["title"], r18_main_api["comment"])
        else:
            r18_result['details'] = "{}".format(r18_main_api["title"])
        if r18_main_api.get("series"):
            r18_result['series_url'] = r18_main_api["series"].get("series_url")
            r18_result['series_name'] = [r18_main_api["series"].get("name")]
        if r18_main_api.get("maker"):
            r18_result['studio'] = [r18_main_api["maker"]["name"]]
        ### 
        if r18_main_api.get("actresses"):
            r18_result['performers'] = [x["name"] for x in r18_main_api["actresses"]]
        if r18_main_api.get("categories"):
            r18_result['tags'] = [x["name"] for x in r18_main_api["categories"]]
        debug("DEBUG: {}".format(r18_result))
        if r18_main_api.get("images"):
            # Don't know if it's possible no image ??????
            r18_result['image'] = r18_main_api["images"]["jacket_image"]["large"]
            imageBase64_r18_thread = threading.Thread(target=th_imagetoBase64, args=(r18_result["image"], "R18",))
            imageBase64_r18_thread.start()

if r18_main_html is None and jav_main_html is None:
    debug("All request don't find anything")
    sys.exit(1)

#debug('[DEBUG][JAV] {}'.format(jav_result))
#debug('[DEBUG][R18] {}'.format(r18_result))

# Time to scrape all data
scrape = {}

# Title - Javlibrary > r18
if r18_result.get('title'):
    scrape['title'] = regexreplace(r18_result['title'][0])
if jav_result.get('title'):
    scrape['title'] = regexreplace(jav_result['title'][0])

# Date - R18 > Javlibrary
if jav_result.get('date'):
    scrape['date'] = jav_result['date'][0]
if r18_result.get('date'):
    scrape['date'] = r18_result['date']

# URL - Javlibrary > R18
if r18_result.get('url'):
    scrape['url'] = r18_result['url'][0]
if jav_result.get('url'):
    scrape['url'] = jav_result['url']

# Details - R18 > Javlibrary
if jav_result.get('details'):
    scrape['details'] = regexreplace(jav_result['details'])
if r18_result.get('details'):
    scrape['details'] = regexreplace(r18_result['details'])
if r18_result.get('series_name'):
    scrape['details'] = scrape['details'] + "\n\nFrom the series: " + regexreplace(r18_result['series_name'][0])

# Studio - Javlibrary > R18
scrape['studio'] = {}
if r18_result.get('studio'):
    scrape['studio']['name'] = r18_result['studio'][0]
if jav_result.get('studio'):
    scrape['studio']['name'] = jav_result['studio'][0]

# Performer - Javlibrary > R18
if r18_result.get('performers'):
    scrape['performers'] = buildlist_tagperf(r18_result['performers'])
if jav_result.get('performers'):
    if WAIT_FOR_ALIASES == True and IGNORE_ALIASES == False:
        try:
            if javlibrary_aliases_thread.is_alive() == True:
                javlibrary_aliases_thread.join()
        except NameError:
            debug("[DEBUG] No Jav Aliases Thread")
    scrape['performers'] = buildlist_tagperf(jav_result, "perf_jav")
# Tags - Javlibrary > R18
if r18_result.get('tags') and jav_result.get('tags') and BOTH_TAGS == True:
    scrape['tags'] = buildlist_tagperf(r18_result['tags'], "tags") + buildlist_tagperf(jav_result['tags'], "tags")
else:
    if r18_result.get('tags'):
        scrape['tags'] = buildlist_tagperf(r18_result['tags'], "tags")
    if jav_result.get('tags'):
        scrape['tags'] = buildlist_tagperf(jav_result['tags'], "tags")

# Image - Javlibrary > R18
try:
    if imageBase64_r18_thread.is_alive() == True:
        imageBase64_r18_thread.join()
    if r18_result.get('image'):
        scrape['image'] = r18_result['image']
except NameError:
    debug("[DEBUG] No R18 Thread")
try:
    if imageBase64_jav_thread.is_alive() == True:
        imageBase64_jav_thread.join()
    if jav_result.get('image'):
        scrape['image'] = jav_result['image']
except NameError:
    debug("[DEBUG] No JAV Thread")

# Movie - R18

if r18_result.get('series_url'):
    tmp = {}
    tmp['name'] = regexreplace(r18_result['series_name'][0])
    tmp['url'] = r18_result['series_url']
    if STASH_SUPPORTED == True:
        # If Stash support this part
        if jav_result.get('image'):
            tmp['front_image'] = jav_result["image"]
        if r18_result.get('image'):
            tmp['front_image'] = r18_result["image"]
        if scrape.get('studio'):
            tmp['studio'] = {}
            tmp['studio']['name'] = scrape['studio']['name']
    scrape['movies'] = [tmp]
print(json.dumps(scrape))
