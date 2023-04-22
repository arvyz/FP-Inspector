import json
import pandas as pd
import requests
from urllib.parse import urlparse

import codecs

# Load the JSON file
with open('fingerprinting_domains.json') as f:
    data = json.load(f)

# Define the headers to send with the request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}


def append_df(items, k, s, t, c, d):
    items.append({
        'hash': k,
        'script_url': s,
        'top_url': t,
        'response_code': c,
        'has_toDataURL': d
    })


with codecs.open('output.csv', 'a', encoding='utf-8') as f:
    # Check if the file is empty
    empty_file = f.tell() == 0

    # Create a dictionary to store the response status code and has_toDataURL values for visited URLs
    visited_url_responses = {}

    # Create an empty list to hold the data items
    items = []

    # Create a set to keep track of the unique script URLs
    visited_urls = set()

    count = 0
    # Loop through each hash in the data dictionary - what are the hashes? Not sure...
    for key, values in data.items():

        # Loop through each unique script url in the list of values.  If multiple sites are using the
        # Same 3rd party script, then assume that the truth for the first result will hold for all
        for value in values:

            # Prepare the script URL to be visited and resulting values captured
            script_url = value['script_url'].split('?')[0]  # Keep only the part before the '?'
            parsed_url = urlparse(script_url)
            url_without_protocol = parsed_url.netloc + parsed_url.path  # Remove the protocol (http/https)
            top_url = value['top_url']

            # Only visit script urls that haven't been visited before
            if url_without_protocol not in visited_urls:
                visited_urls.add(url_without_protocol)
                try:
                    response = requests.get(script_url, headers, timeout=3)
                    script_text = response.text

                    # Search for the string fragment in the script
                    if '.toDataURL()' in script_text:
                        has_toDataURL = True
                    else:
                        has_toDataURL = False

                    append_df(items, key, script_url, top_url, response.status_code, has_toDataURL)
                    visited_url_responses[url_without_protocol] = (response.status_code, has_toDataURL)
                    count += 1
                except (
                requests.exceptions.Timeout, requests.exceptions.HTTPError, requests.exceptions.RequestException,
                requests.exceptions.ConnectionError) as error:
                    # Since the data is >2-year-old, some scripts may not be around anymore
                    # Also some cloud providers like akamai provide defense against bots;
                    # Don't wait round too long for response
                    append_df(items, key, script_url, top_url, 500, False)
                    visited_url_responses[url_without_protocol] = (500, False)

            # if the script url has already been visited, fill in the captured valued
            # for the current script / top site combo
            else:
                r_code, data_url = visited_url_responses[url_without_protocol]
                append_df(items, key, script_url, top_url, r_code, data_url)

            # Write the DataFrame to the file and flush it to disk
            # We are doing this so that we can build the file as we go along
            # Don't want to have a large file built and then have to interrupt out and
            # lose everything.
            if len(items) >= 100:
                df = pd.DataFrame(items)
                df.to_csv(f, header=f.tell() == 0, index=False)
                f.flush()
                items = []

    # Write any remaining items to the file and flush it to disk
    if len(items) > 0:
        df = pd.DataFrame(items)
        df.to_csv(f, header=f.tell() == 0, index=False)
        f.flush()
