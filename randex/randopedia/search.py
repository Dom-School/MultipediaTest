import requests
import bs4
import json
import re
from random import randint
from wiktionaryparser import WiktionaryParser
from randomwordgenerator import randomwordgenerator as r_backup
from random_word import RandomWords

WORDNIK_KEY = 'wlaurbdjhhd8uql2fa84x3skvw8g1uw5ffogaozp7sya3zg90'


def info_source(search=" "):

    result = {}

    if search == " ":
        search = get_word()
        # If the random is plural recall the function as a singular word
        non_plural = wiktionary_info(search, unplurify=True)
        if non_plural != None:
            return info_source(non_plural)

    result["original_search"] = search
    result["no_result"] = False

    wiktionary_dic = wiktionary_info(search)
    result.update(wiktionary_dic)

    wiki_dic = wiki_info(search)
    result.update(wiki_dic)

    urban_dic = urban_info(search)
    result.update(urban_dic)

    print(result)

    if len(result) <= 2:
        result["no_result"] = True
        return result
    return result


def wiki_info(search, pageid=0):
    """ Returns a dictionary with the wikipedia title and main text from the given search term """

    wiki_result = {"wiki_title": "", "wiki_text_brief": "", "wiki_text": []}

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
    if DATA["query"]["search"] == []:
        return {}
    pageids = [sr["pageid"] for sr in DATA["query"]["search"]]
    main_id = pageids[pageid]

    # Use the given page id to go to right page and extract the information
    PARAMS = {
        'action': "parse",
        'pageid': main_id,
        'format': "json"
    }
    req = requests.get(url=WIKI_URL, params=PARAMS, headers={
                       "User-Agent": "Mozilla/5.0"})
    check_url(req)
    DATA = req.json()

    # Add page headert to the result
    title = DATA["parse"]["title"]
    wiki_result["wiki_title"] = title

    # Console Debug Teter Code
    print("Wiki title: " + wiki_result["wiki_title"])

    # Get the main html from the json url
    parser_output = DATA["parse"]["text"]["*"]
    soup = bs4.BeautifulSoup(parser_output, "html.parser")
    main_text = soup.find(class_="mw-parser-output")

    # If the phrase " refer to" is any of the p tags the wikipedia page
    # the page is ambiguous so the function is recalled with the most relevent option"
    for p in main_text.find_all('p'):
        if " refer to:" in p.text:
            for ul in main_text.find_all('ul'):
                if "#" not in ul.li.a['href']:
                    new_search = ul.li.a['href']
                    break
            req = requests.get("https://en.wikipedia.org" +
                               new_search, headers={"User-Agent": "Mozilla/5.0"})
            check_url(req)
            soup = bs4.BeautifulSoup(req.text, "html.parser")
            wiki_result["wiki_title"] = soup.find(
                "h1", id="firstHeading").text
            # Console Debug Teter Code
            print("Wiki title: " + wiki_result["wiki_title"])
            main_text = soup.find(class_="mw-parser-output")

    # Loop through the p tags and get the main information
    tags = main_text.children
    for tag in tags:

        # Add main paragraphs and remove all the references([1],[2]...) from the text
        if tag.name == 'p':
            if tag.sup != None:
                for i in range(len(tag.find_all("sup"))):
                    tag.sup.decompose()
            # wiki_result["wiki_text"] = wiki_result["wiki_text"] +
            wiki_result["wiki_text"].append(tag.text)

        # When a new headline is found return the result
        if tag.name == 'h2':
            # wiki_result["wiki_text"] = wiki_result["wiki_text"].strip().split('\n')

            while '\n' in wiki_result["wiki_text"]:
                wiki_result["wiki_text"].remove('\n')

            wiki_result["wiki_text_brief"] = wiki_result["wiki_text"][0]
            wiki_result["wiki_text"] = wiki_result["wiki_text"][1:]

            return wiki_result


def urban_info(search):
    urban_result = {"urban_title": "", "urban_text": ""}
    URBAN_API_URL = 'http://api.urbandictionary.com/v0/define?term='
    URBAN_URL = 'https://www.urbandictionary.com/define.php?term='

    req = requests.get(URBAN_API_URL+search)
    check_url(req)
    DATA = req.json()

    if DATA['list'] == []:
        req = requests.get(URBAN_URL + search)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        if not soup.find(class_="try-these"):
            return {}
        close_word = soup.find(class_="try-these").find("a").text
        return urban_info(close_word)

    title = DATA['list'][0]['word'].title()
    # Console Debug Teter Code
    print("Urban title: " + title)
    urban_result["urban_title"] = title

    definition = DATA['list'][0]['definition']
    useless_chars = ['[', ']', '\n', '\r']
    for char in useless_chars:
        definition = definition.replace(char, "")

    urban_result["urban_text"] = definition

    return urban_result


def wiktionary_info(search, unplurify=False):
    wiktionary_result = {"wikti_defins_1": [],
                         "wikti_defins_2": []}
    definitions = []

    parser = WiktionaryParser()
    DATA = parser.fetch(search)

    if unplurify:
        if len(DATA) == 1 and len(DATA[0]['definitions']) == 1 and "plural of" in DATA[0]['definitions'][0]['text'][1]:
            non_plural = DATA[0]['definitions'][0]['text'][1].replace(
                "plural of ", "")
            return non_plural
        else:
            return None

    for word in DATA:
        for word_def in word['definitions']:
            for defin in word_def['text'][1:]:
                definitions.append(defin)

    if definitions == []:
        return {}

    # Console Debug Teter Code
    print("Wiktionary title: " + definitions[0])

    defins_num = 3

    if len(definitions) > defins_num:
        wiktionary_result["wikti_defins_1"] = definitions[:defins_num]
        wiktionary_result["wikti_defins_2"] = definitions[defins_num:]
    else:
        wiktionary_result["wikti_defins_1"] = definitions

    return wiktionary_result


def get_word():
    while(True):
        try:
            # r.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=1, maxCorpusCount=10, minDictionaryCount=1, maxDictionaryCount=10, minLength=5, maxLength=10, sortBy="alpha", sortOrder="asc", limit=15)
            word = RandomWords().get_random_word(
                hasDictionaryDef="true", includePartOfSpeech="noun")
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
        return False


# print(info_source(get_word()))
# print(info_source("turtlenecks"))
# print(wiki_info("cat"))
# print(urban_info("tinselly"))
# print(wiktionary_info("turtlenecks"))
# print(wiktionary_info("demi-jambe"))

"""
    if len(DATA) == 1 and len(DATA[0]['definitions']) == 1 and "plural of" in DATA[0]['definitions'][0]['text'][1]:
        print(DATA[0]['definitions'][0]['text'][1].replace("plural of ", ""))
"""
