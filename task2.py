#!/usr/bin/env python

import requests
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter


# task 1:
def get_turing_award_recipients():
    """
    Fetches a list of WikiData entities of humans who have won the ACM Turing Award.
    Uses the WikiData API and property P166 (award received) with the value Q185667 (ACM Turing Award).
    """
    # Query URL for WikiData
    url = "https://query.wikidata.org/sparql"

    # SPARQL Query
    query = """
    SELECT ?human ?humanLabel WHERE {
      ?human wdt:P166 wd:Q185667 .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    """

    # Headers for request
    headers = {
        "User-Agent": "Chrome",
        "Accept": "application/json"
    }

    # Sending the request
    response = requests.get(url, headers=headers, params={'query': query, 'format': 'json'})

    if response.status_code != 200:
        return "Failed to fetch data from WikiData"

    # Parsing the response
    data = response.json()
    recipients = [(result['human']['value'], result['humanLabel']['value']) for result in data['results']['bindings']]

    return recipients


# task 2:
def get_wikipedia_content(wikidata_id):
    """
    Fetches the content of the English Wikipedia page for a given Wikidata ID.

    :param wikidata_id: The Wikidata ID of the entity (e.g., "Q42" for Douglas Adams).
    :return: The content of the Wikipedia page if it exists, otherwise an error message.
    """
    # Constructing the URL for the WikiData API query
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={wikidata_id}&format=json"

    # Headers for the request
    headers = {"User-Agent": "Chrome"}

    # Fetching the data from WikiData
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to fetch data from WikiData"

    data = response.json()

    # Checking if the entity has a Wikipedia link
    entity_data = data['entities'][wikidata_id]
    if 'sitelinks' in entity_data and 'enwiki' in entity_data['sitelinks']:
        wikipedia_title = entity_data['sitelinks']['enwiki']['title']

        # Constructing the URL for the Wikipedia API
        wikipedia_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles={wikipedia_title}&format=json&explaintext"

        # Fetching the Wikipedia page content
        wikipedia_response = requests.get(wikipedia_url, headers=headers)
        if wikipedia_response.status_code != 200:
            return "Failed to fetch data from Wikipedia"

        wikipedia_data = wikipedia_response.json()
        page = next(iter(wikipedia_data['query']['pages'].values()))

        # Returning the content of the Wikipedia page
        return page['extract'] if 'extract' in page else "No content available"
    else:
        return "No English Wikipedia page found for this Wikidata ID"


def get_all_turing_award_recipients_wikipedia_content():
    """
    Fetches the Wikipedia page content for all Turing Award recipients.
    Utilizes the get_turing_award_recipients function to retrieve the list of recipients
    and the get_wikipedia_content function to fetch the Wikipedia page content.
    """
    # Fetch the Turing Award recipients
    turing_award_recipients = get_turing_award_recipients()

    # Dictionary to store the Wikipedia contents
    wikipedia_contents = {}

    for recipient in turing_award_recipients:
        wikidata_id = recipient[0].split('/')[-1]  # Extracting the Wikidata ID
        wikipedia_content = get_wikipedia_content(wikidata_id)
        wikipedia_contents[recipient[1]] = wikipedia_content

    return wikipedia_contents


# task 3:
def get_award_winner_details(wikidata_id):
    """
    Fetches detailed information for an award winner from Wikidata.
    Gathers details like name, gender, birthdate, birthplace, employer, and education.

    :param wikidata_id: The Wikidata ID of the award winner.
    :return: A dictionary with the award winner's details.
    """
    # Constructing the URL for the WikiData API query
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={wikidata_id}&format=json"

    # Headers for the request
    headers = {"User-Agent": "Chrome"}

    # Fetching the data from WikiData
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to fetch data from WikiData"

    data = response.json()

    # Parsing the data
    details = data['entities'][wikidata_id]['claims']
    winner_details = {}

    # Mapping properties
    properties = {
        'P21': 'gender',
        'P569': 'birth date',
        'P19': 'birth place',
        'P108': 'employer',
        'P69': 'educated at'
    }

    # Extracting information for each property
    for prop, label in properties.items():
        if prop in details:
            if len(details[prop]) > 1:
                # Multiple entries, storing as a list
                winner_details[label] = [item['mainsnak']['datavalue']['value'] for item in details[prop]]
            else:
                # Single entry
                winner_details[label] = details[prop][0]['mainsnak']['datavalue']['value']
        else:
            # No information available
            winner_details[label] = None

    # Adding Wikipedia intro
    intro = get_wikipedia_content(wikidata_id)
    winner_details['intro'] = intro if isinstance(intro, str) else None

    return winner_details


# task 4:
def print_award_winners_in_alphabetical_order():
    recipients = get_turing_award_recipients()
    names = [recipient[1] for recipient in recipients]  # Extracting names
    names.sort()  # Sorting the names alphabetically

    for name in names:
        print(name)


# task 5
nltk.download('punkt')
nltk.download('stopwords')
award_winners = get_all_turing_award_recipients_wikipedia_content()


def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    return [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]

award_winners_intro = pd.DataFrame(columns=['winner name', 'count words', 'count sentences', 'count paragraphs', 'common words', 'common words after preprocessing'])

for winner, intro in award_winners.items():
    words = word_tokenize(intro)
    sentences = sent_tokenize(intro)
    paragraphs = intro.count('\n') + 1
    common_words = [word for word, freq in Counter(words).most_common(10)]
    processed_words = preprocess_text(intro)
    common_words_processed = [word for word, freq in Counter(processed_words).most_common(10)]

    new_row = {
        'winner name': winner,
        'count words': len(words),
        'count sentences': len(sentences),
        'count paragraphs': paragraphs,
        'common words': common_words,
        'common words after preprocessing': common_words_processed
    }

    award_winners_intro = award_winners_intro.append(new_row, ignore_index=True)

print(award_winners_intro.head(10))
