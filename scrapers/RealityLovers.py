import json
import sys
import re
import requests
import time
import base64

# Set these cookies to the values from your RealityLovers browser session
cookies = []

# create our session with cookies
session = requests.session()
for cookie in cookies:
    session.cookies.set_cookie(cookie)

try:
    import py_common.log as log
except ModuleNotFoundError:
    print(
        "You need to download the folder 'py_common' from the community repo (CommunityScrapers/tree/master/scrapers/py_common)",
        file=sys.stderr)
    sys.exit(1)

try:
    from lxml import html
except ModuleNotFoundError:
    print("You need to install the lxml module. (https://lxml.de/installation.html#installation)", file=sys.stderr)
    print("If you have pip (normally installed with python), run this command in a terminal (cmd): pip install lxml",
          file=sys.stderr)
    sys.exit()


#  --------------------------------------------

# This is a scraper for: RealityLovers sites
#
# These fields will be populated if available:
# Title, URL, Image, Date
#


# Get the scene by the fragment.  The title is used as the search field.  Should return the JSON response.
# This is a script instead of a JSON scraper since the search is a POST
def sceneByName():
    # read the input.  A title or name must be passed in
    inp = json.loads(sys.stdin.read())
    log.trace("Input: " + json.dumps(inp))
    query_value = inp['title'] if 'title' in inp else inp['name']
    if not query_value:
        log.error('No title or name Entered')
    log.trace("Query Value: " + query_value)

    # call the query url based on the input and validate the response code
    data = {
        "sortBy": "MOST_RELEVANT",
        "searchQuery": query_value,
        "offset": 0,
        "isInitialLoad": True,
        "videoView": "MEDIUM",
        "device": "DESKTOP"
    }
    scraped_scenes = session.post(f"https://realitylovers.com/videos/search?tc={time.time()}",
                                  data=data)
    log.debug("Called: " + scraped_scenes.url + " with body: " + json.dumps(data))
    if scraped_scenes.status_code >= 400:
        log.error('HTTP Error: %s' % scraped_scenes.status_code)

    # get the data we can scrape directly from the page
    scenes = json.loads(scraped_scenes.content)
    log.debug("Scenes: " + json.dumps(scenes))
    results = []
    for scene in scenes['contents']:
        # Parse the date published.  Get rid of the 'st' (like in 1st) via a regex. ex: "Sep 27th 2018"
        published = time.strptime(re.sub(r"(st|nd|rd|th)", r"", scene['released']), '%b %d %Y')
        main_image_src = re.sub(r'.*1x,(.*) 2x', r'\1', scene['mainImageSrcset'])
        log.debug("Image: " + main_image_src)
        # Add the new scene to the results
        results.append({
            'Title': scene['title'],
            'URL': "https://realitylovers.com/" + scene['videoUri'],
            'Image': main_image_src,
            'Date': time.strftime("%Y-%m-%d", published)
        })

    # create our output
    return results


# Figure out what was invoked by Stash and call the correct thing
if sys.argv[1] == "sceneByURL":
    # print(json.dumps(sceneByURL()))
    log.error("Scene by url not supported yet")
elif sys.argv[1] == "sceneByName":
    scenes = sceneByName()
    print(json.dumps(scenes))
elif sys.argv[1] == "sceneByQueryFragment":
    scenes = sceneByName()
    if len(scenes) > 0:
        # return the first query result
        print(json.dumps(scenes[0]))
    else:
        # empty array for no results
        log.info("No results")
        print("{}")
else:
    log.error("Unknown argument passed: " + sys.argv[1])
    print(json.dumps({}))
