'''
Yelp.py contains methods for
authenticating the user and
retrieving data from Yelp's API.
'''

import simplejson as json
import oauth2
import requests
import argparse
from pprint import pprint
import sys
import urllib
import urllib2
import oauth2
import os

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = 'EXMisJNWez_PuR5pr06hyQ'
CONSUMER_SECRET = 'VCK-4cDjtQ9Ra4HC5ltClNiJFXs'
TOKEN = 'AWYVs7Vim7mwYyT1BLJA2xhNTs_vXLYS'
TOKEN_SECRET = 'Rv4GrlYxYGhxUs14s0VBfk7JLJY'

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'pizza'
DEFAULT_LOCATION = 'Washington, DC'
SEARCH_LIMIT = 20
SORT = 0
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'


def getRestaurantAddresses(restaurants):
    """Calculates the list of all restaurant addresses

    Args:
        restaurants (list of dicts)
        cuisines (list): The list of all cuisines to search for.
        distance (int): The distance to search around each intermediate point

    Returns:
        restlist (list of dicts): The list of all restaurant results, containing dictionaries with the processed yelp results

    """
    addresslist = []
    for rest in restaurants:
        if 'address' in rest:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            addresslist.append(addressstring)

    # pprint.pprint(addresslist)
    return addresslist

def getRestaurantAddressDict(restaurants):
    """Creates a dictionary for identifying restaurants based on their address, to be used in distance matrix calculations.

    Args:
        restaurants (list of dicts) : processed data about the Yelp API

    Returns:
        addressdict (dict): The dictionary for identifying the restaurant at each point

    """
    addressdict = {}
    for rest in restaurants:
        if 'address' in rest:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            addressdict[addressstring] = rest['name']

    return addressdict


def calcBusinessList(businessTypes, boundingarea):
    """Calls the Yelp API to search around each intermediate route point the function to process the
    yelp results, and adds all new restaurants to a list.

    Args:
        latlngs (list): The list of the lat / long pairs of all intermediate route points.
        cuisines (list): The list of all cuisines to search for.
        distance (int): The distance to search around each intermediate point

    Returns:
        restlist (list of dicts): The list of all restaurant results, containing dictionaries with the processed yelp results

    """
    bizlist = []
    used = []
    # btype = str(businessTypes[0])
    for bee in businessTypes:
        btype = str(bee)
    # if len(businessTypes) > 1:
    #     btype = ",".join(businessTypes)
        yelpresults = search2(btype,boundingarea)['businesses']
        processedyelpresults = processResults(yelpresults)
        for result in processedyelpresults:
            if (result not in used):
                bizlist.append(processedyelpresults[result])
                used.append(result)

    return bizlist


def search2(term, boundarea):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        distance (int): The search distance to query from each route point.

    Returns:
        dict: The JSON response from the request.
    """

    print boundarea

    metradius = 1600
    url_params = {
        'category_filter': term.replace(' ', '+'),
        # 'radius_filter': metradius,
        # 'll': location.replace(' ', '+'),
        'sort' : SORT,
        'bounds': boundarea,
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(
        method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(
        oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def processResults(results):
    """Parses the results of the Yelp API query into a more logical and easy to use structure.

    Args:
        results (dict): The JSON response from the API.

    Returns:
        restaurantDict: The processed results into an easier to use format

    """
    restaurantDict = {}
    for result in results:
        rdict = {}
        name = result['name']
        location = result['location']
        rdict['name'] = name
        rdict['url'] = result['mobile_url']
        rdict['Biz Type'] = result['categories']
        rdict['closed'] = result['is_closed']
        rdict['address'] = location['display_address'][0]
        if 'neighborhoods' in location:
            rdict['neighborhood'] = location['neighborhoods'][0]
        else:
            rdict['neighborhood'] = 'N/A'
        if 'display_phone' in result:
            rdict['phone'] = result['display_phone']
        rdict['city'] = str(location['city']) + ", " + str(location['state_code'])
        rdict['rating'] = str(result['rating'])

        if ('coordinate' in result['location']):
            rdict['coords'] = [result['location']['coordinate']['latitude'], result['location']['coordinate']['longitude']]
            if rdict['city'] != rdict['address']:
                restaurantDict[name] = rdict

    return restaurantDict


def writeResults(floc, fname, fr):
    import csv
    if not os.path.exists(floc):
        os.makedirs(floc)
    filea = floc + fname
    with open(filea, 'wb') as b:
        # fieldnames2 = ["VMLoc","Connecting Node","Track","Orig/Dest","Link"]
        resultsfields = ["OID","name","address","city","neighborhood","Biz Type","rating","url","lat","lng"]

        writer = csv.DictWriter(b, fieldnames=resultsfields)
        writer.writeheader()

        count = 1
        for row in fr:
            rowa = {}
            rowa["OID"] = count
            rowa['lat'] = row['coords'][0]
            rowa['lng'] = row['coords'][1]
            for resultsfield in resultsfields:
                if resultsfield != 'OID' and resultsfield != 'lat' and resultsfield != 'lng':
                    rowa[resultsfield] = row[resultsfield]
            writer.writerow(rowa)
            count += 1

        b.close()