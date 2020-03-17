"""

"""
import requests
from googlesearch import search
from bs4 import BeautifulSoup
import re

NUMBER_OF_WEBSITE_TO_SCRAP = 5
NUMBER_OF_PAGE_TO_SCRAP_PER_WEBSITE = 10


def _get_domain_url(url):
    """ Get the domain from URL

    :param url:
    :return:
    """
    domain = url.split("/")
    while domain[0] == 'https:' or domain[0] == 'http:' or domain[0] == '':
        domain.pop(0)
    return domain[0]


def get_list_of_urls_to_scrap(keyword):
    """ Get list of urls of distinct website to scrap

    :param keyword:
    :return:
    """
    list_urls = []
    for url in search(keyword, tld="co.in", lang='en', pause=1):
        url_domain = _get_domain_url(url)
        # If the domain is not found in the list already
        if not any(url_domain in u for u in list_urls):
            list_urls.append(url)
            if len(list_urls) == NUMBER_OF_WEBSITE_TO_SCRAP:
                break

    return list_urls


def _clean_web_page(text):
    """

    :param text:
    :return:
    """
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    return "\n".join(chunk for chunk in chunks if chunk)


def _scrap_webpage(url, list_of_urls):
    """

    :param url:
    :param list_of_urls:
    :return:
    """
    data = requests.get(url=url, verify=False)
    soup = BeautifulSoup(data.content, 'lxml')

    # Init list of urls with current url
    list_of_urls[url] = ""

    # Get links from the page
    _get_links(list_of_urls, soup, url)

    # Kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Remove all text from links and buttons
    for anchor in soup.findAll('a'):
        anchor.decompose()
    for button in soup.findAll('button'):
        button.decompose()

    # Get text and clean
    text = _clean_web_page(soup.get_text())

    # Get the clean text from the webpage
    list_of_urls[url] = text


def _get_links(list_of_urls, soup, url):
    """

    :param list_of_urls:
    :param soup:
    :param url:
    :return:
    """
    # Get the links (only https links)
    url_domain = _get_domain_url(url)
    if "wikipedia" not in url_domain:
        for href_link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
            link = href_link.get('href')
            # Case anchor
            if "#" in link:
                link = link.split("#")[0]
            if url_domain == _get_domain_url(link) and link not in list_of_urls.keys() and len(
                    list(list_of_urls.keys())) < NUMBER_OF_PAGE_TO_SCRAP_PER_WEBSITE:
                list_of_urls[link] = ""


def scrap_web_site(url):
    """ Scrap a website

    :param url:
    :return:
    """

    list_of_urls = {}
    list_of_urls[url] = ""

    # While we have empty text as value in dict
    while "" in list_of_urls.values():

        # Scrap web page of urls without text in dict
        _scrap_webpage(list(list_of_urls.keys())[list(list_of_urls.values()).index("")], list_of_urls)

    return list_of_urls


def process_web_extraction(keyword):
    """

    :param keyword:
    :return:
    """
    # Get list of URLs to extract
    list_of_urls_to_scrap = get_list_of_urls_to_scrap(keyword)
    # list_of_urls_to_scrap = ['https://www.nist.gov/', 'https://www.cleanpng.com/png-national-institute-of-standards-and-technology-nis-5552763/', 'https://en.wikipedia.org/wiki/National_Institute_of_Standards_and_Technology', 'https://twitter.com/NIST?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor', 'https://www.time.gov/']

    # Extract text from each URLs
    dict_web_site = {}
    for url in list_of_urls_to_scrap:
        dict_web_site[url] = scrap_web_site(url)

    return dict_web_site
    # raw_result = []
    # for k, v in dict_web_site.items():
    #
    #     # full_text = '/n'.join(val for val in v.values())
    #     for index, key in enumerate(v):
    #         raw_result[k][index] = _call_stanfordnlp_server(v[key])

