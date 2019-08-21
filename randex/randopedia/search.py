import requests
import bs4
import json
from random import randint
from randomwordgenerator import randomwordgenerator as r_backup
from random_word import RandomWords

URBAN_URL = ''
MERRIAM_URL = ''

result = {}


def info_source(search=" "):

    if search == " ":
        search = get_word()

    return wikipedia_info(search)


def wikipedia_info(search, pageid=0):
    """ Returns a dictionary with the wikipedia title and main text from the given search term """

    wiki_result = {"wiki_title": "", "wiki_text": ""}
    WIKI_URL = "https://en.wikipedia.org/w/api.php"
    search_limit = 7
    pageids = []

    # Get a list of page ids from the API
    PARAMS = {
        'action': "query",
        'list': "search",
        'srsearch': search,
        'srlimit': search_limit,
        'format': "json"
    }
    req = requests.get(url=WIKI_URL, params=PARAMS)
    check_url(req)
    DATA = req.json()
    pageids = [sr["pageid"] for sr in DATA["query"]["search"]]
    main_id = pageids[pageid]

    # Use the given page id to go to right page and extract the information
    PARAMS = {
        'action': "parse",
        'pageid': main_id,
        'format': "json"
    }
    req = requests.get(url=WIKI_URL, params=PARAMS)
    check_url(req)
    DATA = req.json()

    # Add page headert to the result
    title = DATA["parse"]["title"]
    wiki_result["wiki_title"] = title

    print(title)

    # Get the main html from the json url
    parser_output = DATA["parse"]["text"]["*"]
    soup = bs4.BeautifulSoup(parser_output, "html.parser")
    main_text = soup.find(class_="mw-parser-output")

    # If the phrase " refer to" is any of the p tags the wikipedia page
    # the page is ambiguous so the function is recalled with a different page id"
    for p in main_text.find_all('p'):
        if " refer to:" in p.text:
            return wikipedia_info(search, randint(1, len(pageids)-1))

    # Loop through the p tags and get the main information
    tags = main_text.children
    for tag in tags:

        # Add main paragraphs and remove all the references([1],[2]...) from the text
        if tag.name == 'p':
            if tag.sup != None:
                for i in range(len(tag.find_all("sup"))):
                    tag.sup.decompose()
            wiki_result["wiki_text"] = wiki_result["wiki_text"] + \
                tag.text + "\n"

        # When a new headline is found return the result
        if tag.name == 'h2':
            wiki_result["wiki_text"] = wiki_result["wiki_text"].strip()
            # print(wiki_result)
            return wiki_result


def get_word():
    while(True):
        try:
            # r.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=1, maxCorpusCount=10, minDictionaryCount=1, maxDictionaryCount=10, minLength=5, maxLength=10, sortBy="alpha", sortOrder="asc", limit=15)
            word = RandomWords().get_random_word(hasDictionaryDef="true")
        except Exception as exc:
            print('There was a problem: %s' % (exc))
            word = r_backup.generate_random_words(1)
        print("Random word: " + word)

        """
        wiki = 'https://en.wikipedia.org/wiki/{}'.format(word)
        wiki_res = requests.get(wiki)
        try:
            wiki_res.raise_for_status()
            return word
        except Exception as exc: 
            print('There was a problem: %s' % (exc))
            continue
        """
        return word


def check_url(req):
    """Checks if the request was successful"""

    try:
        req.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))
        return None


print(wikipedia_info("queen"))
