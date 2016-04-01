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
from SpatialExtent import splitBounds, resplitBounds

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

def requery1(btype, boundingarea, city, state, bizlist):
    boxes = splitBounds(boundingarea, city, state)
    finalresults = bizlist
    for a in boxes:
        thisbox = boxes[a]
        bound = "{0}|{1}".format(thisbox['sw_bound'], thisbox['ne_bound'])
        results = search2(btype,bound)['businesses']
        processedyelpresults = processResults(results)
        # pprint(processedyelpresults)
        if len(processedyelpresults) == 20:
            newboxes = resplitBounds(thisbox)
            for b in newboxes:
                abox = newboxes[b]
                nbound = "{0}|{1}".format(abox['sw_bound'], abox['ne_bound'])
                results = search2(btype,nbound)['businesses']
                processedyelpresults = processResults(results)
                if len(processedyelpresults) == 20:
                    newboxes2 = resplitBounds(abox)
                    for b2 in newboxes2:
                        bbox = newboxes2[b2]
                        nbound = "{0}|{1}".format(bbox['sw_bound'], bbox['ne_bound'])
                        results = search2(btype,nbound)['businesses']
                        processedyelpresults = processResults(results)
                        for f in processedyelpresults:
                            # pprint (f)
                            inList = False
                            if len(bizlist) > 0:
                                for res in bizlist:
                                    if f['name'] == res['name'] and f['address'] == res['address']:
                                        # print ("YAAA")
                                        inList = True
                                if inList == False:
                                    # print("F2")
                                    finalresults.append(f)
                            else:
                                # print(f)
                                # print("F")
                                finalresults.append(f)
                for f in processedyelpresults:
                    # pprint (f)
                    inList = False
                    if len(bizlist) > 0:
                        for res in bizlist:
                            if f['name'] == res['name'] and f['address'] == res['address']:
                                # print ("YAAA")
                                inList = True
                        if inList == False:
                            # print("F2")
                            finalresults.append(f)
                    else:
                        # print(f)
                        # print("F")
                        finalresults.append(f)
        elif len(processedyelpresults) < 20:
            for r in processedyelpresults:
                inList = False
                if len(bizlist) > 0:
                    for res in bizlist:
                        if r['name'] == res['name'] and r['address'] == res['address']:
                            inList = True
                    if inList == False:
                        # print("R2")
                        finalresults.append(r)
                else:
                    # print(r)
                    # print("R")
                    finalresults.append(r)

    # pprint(finalresults)
    return finalresults


def calcBusinessList(businessTypes, boundingarea, city, state):
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
    usednames = []
    usedaddresses = []
    # btype = str(businessTypes[0])
    for bee in businessTypes:
        btype = str(bee)
    # if len(businessTypes) > 1:
    #     btype = ",".join(businessTypes)
        yelpresults = search2(btype,boundingarea)['businesses']
        if len(yelpresults) == 20:
            yelpresults = requery1(btype, boundingarea, city, state, bizlist)
        else:
            yelpresults = processResults(yelpresults)
        # pprint(processedyelpresults)
        # print len(processedyelpresults)
        for result in yelpresults:
            inList = False
            # pprint(bizlist)
            for biz in bizlist:
                # print(result)
                # print(biz)
                if result['name'] == biz['name'] and result['address'] == biz['address']:
                    inList = True
            if inList == False:
                bizlist.append(result)

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
    # restaurantDict = {}
    restaurantList = []
    for result in results:
        rdict = {}
        name = result['name'].encode('ascii', 'ignore')
        location = result['location']
        rdict['name'] = name.encode('ascii', 'ignore')
        rdict['url'] = result['mobile_url'].encode('ascii', 'ignore')
        rdict['Biz Type'] = result['categories'][0][0]
        rdict['closed'] = result['is_closed']
        rdict['address'] = location['display_address'][0].encode('ascii', 'ignore')
        if 'neighborhoods' in location:
            rdict['neighborhood'] = location['neighborhoods'][0].encode('ascii', 'ignore')
        else:
            rdict['neighborhood'] = 'N/A'
        if 'display_phone' in result:
            rdict['phone'] = result['display_phone']
        rdict['city'] = str(location['city']) + ", " + str(location['state_code'])
        rdict['rating'] = str(result['rating'])

        if ('coordinate' in result['location']):
            rdict['coords'] = [result['location']['coordinate']['latitude'], result['location']['coordinate']['longitude']]
            if rdict['city'] != rdict['address']:
                # restaurantDict[name] = rdict
                restaurantList.append(rdict)

    # return restaurantDict
    return restaurantList


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