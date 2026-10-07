import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def author_name(soup,author_index):
    """
    Extract an individual author's full name by index from a parsed PubMed page.

    Parameters:
    ----------
    soup : BeautifulSoup
        Parsed HTML soup of a PubMed page.
    author_index : int
        index of the author in the 'authors-list-item' collection.

    Returns:
    -------
    bs4.element.NavigableString or str
        The extracted author name.
    """
    affiliation = soup.find_all('span', class_='authors-list-item')
    sub_layer1 = list(affiliation)[author_index]
    sub_layer2 = list(sub_layer1.children)
    author = list(sub_layer2[0].children)[0]
    return author

# Author Name List
def name_full_list(soup,num_author):
    """
    Extract all author names from a parsed PubMed page up to a specified count.

    Parameters:
    ----------
    soup : BeautifulSoup
        Parsed HTML soup of a PubMed article.
    num_author : int
        Total number of authors to extract.

    Returns:
    -------
    list of str
        List containing full author names in their listed publication order.
    """
    name = []
    for i in range(num_author):
        name.append(author_name(soup,i))
    return name


def drop_footnote(str):
    """
    Remove footnote notation containing brackets (e.g., ']') from an affiliation string.

    Parameters:
    ----------
    str : str
        The raw affiliation string containing potential footnote tags.

    Returns:
    -------
    str
        Cleaned text string with footnote tokens removed.
    """
    str_ls = str.split(" ")
    for i in str_ls:
        if "]" in i:
            str_ls.remove(i)
    str_new = ' '.join(str_ls)
    return str_new


def affiliation(soup,num_author):
    """
    Extract the affiliation string for a specific author from a PubMed page.

    Parses the author's affiliation link tag, extracts text from the title attribute,
    and strips out inline email addresses or footnote markers.

    Parameters:
    ----------
    soup : BeautifulSoup
        Parsed HTML soup of a PubMed article.
    num_author : int
        Zero-based index of the target author in the authors list.

    Returns:
    -------
    str
        Cleaned affiliation text string, or an empty string if no affiliation link exists.
    """
    affiliation = soup.find_all('span',class_='authors-list-item')
    if 'affiliation-link' in str(affiliation[num_author]):
        af1 = list(affiliation[num_author].children)[1]
        if len(af1) < 2:
            return ''
        else:
            af2 = list(af1.children)[1]
            rule_aff = '''title=['"\w\d\s,\D]*.['"]'''
            search_rs = re.findall(rule_aff, str(af2))
            affiliation = search_rs[0].split("=")
            search_character = "@"
            match_index = re.search(search_character, affiliation[1])
            rule = "[a-zA-Z0-9+_.-]*@[a-zA-Z0-9+_.-]*\w"
            if match_index:
                affiliation = re.sub(rule, '', affiliation[1])
                affiliation = str(affiliation)
                return affiliation
            else:
                affiliation = drop_footnote(affiliation[1])
                return affiliation
    else:
        return ""



# Email New version
def email(soup,author_index,affiliation):
    """
    Extract an author's email address from their PubMed affiliation tag.

    Inspects the author's element in the parsed HTML structure and uses regular
    expression matching to locate an email address within the title attribute.

    Parameters:
    ----------
    soup : BeautifulSoup
        Parsed HTML soup of a PubMed article.
    author_index : int
        Zero-based index of the author in the authors list.
    affiliation : str
        Extracted affiliation string for validation (if empty, search is skipped).

    Returns:
    -------
    str
        Extracted email address as a string, or '[]' if no email is found.
    """
    email = soup.find_all('span', class_='authors-list-item')
    if affiliation == "":
        return '[]'
    elif '@' in str(email):
        e1 = list(email[author_index].children)[1]
        e2 = list(e1.children)[1]

        rule_aff = '''title=['"\w\d\s,\D]*.['"]'''
        search_rs = re.findall(rule_aff, str(e2))
        affiliation_text = search_rs[0].split("=")
        search_character = "@"
        match_index = re.search(search_character, affiliation_text[1])
        rule = "[a-zA-Z0-9+_.-]*@[a-zA-Z0-9+_.-]*\w"
        if match_index:
            address = re.findall(rule, affiliation_text[1])
            return str(address[0])
        else:
            return '[]'
    else:
        return '[]'

#Email New version Alternation
def email_alter(affiliation):
    """
    Extract an email address directly from an affiliation text string using regular expressions.

    Acts as a fallback method when standard DOM structure extraction does not capture an email.

    Parameters:
    ----------
    affiliation : str or object
        Affiliation text containing a potential email address.

    Returns:
    -------
    str
        Extracted email address string, or '[]' if no email pattern is found.
    """
    aff=str(affiliation)
    if  aff == "":
        return '[]'
    elif '@' in aff:
        search_character="@"
        match_index=re.search(search_character,aff)
        rule = "[a-zA-Z0-9+_.-]*\s*@\s*[a-zA-Z0-9+_.-]*\w"
        if match_index:
            address = re.findall(rule, aff)
            return str(address[0])
        else:
            return '[]'
    else:
        return '[]'