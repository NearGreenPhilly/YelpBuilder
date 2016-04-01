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

# http://census.ire.org/geo/1.0/boundary-set/states/17

API_HOST = 'census.ire.org'
SEARCH_PATH = '/geo/1.0/boundary-set/places/'

def calcBound(city, state):

    gj = search(state, city)['simple_shape']['coordinates']
    maxc = getMax(gj)
    minc = getMin(gj)

    sw_coord = "{0},{1}".format(minc[0], minc[1])
    ne_coord = "{0},{1}".format(maxc[0], maxc[1])

    bound = "{0}|{1}".format(sw_coord, ne_coord)

    return bound

def splitBounds(boundingarea, city, state):

    gj = search(state, city)['simple_shape']['coordinates']
    maxc = getMax(gj)
    minc = getMin(gj)
    boxes = []
    xextent = float(maxc[0]) - float(minc[0])
    yextent = float(maxc[1]) - float(minc[1])

    deltax = xextent / 2
    deltay = xextent / 2
    boxes = {}
    bounds = {}

    box1 = {}
    box1['min'] = [(minc[0]), (minc[1])]
    box1['max'] = [(minc[0] + deltax), (minc[1] + deltay)]
    box1['sw_bound'] = "{0},{1}".format(box1['min'][0], box1['min'][1])
    box1['ne_bound'] = "{0},{1}".format(box1['max'][0], box1['max'][1])
    boxes[1] = box1

    box2 = {}
    box2['min'] = [(minc[0] + deltax), (minc[1])]
    box2['max'] = [(maxc[0]), (minc[1] + deltay)]
    box2['sw_bound'] = "{0},{1}".format(box2['min'][0], box2['min'][1])
    box2['ne_bound'] = "{0},{1}".format(box2['max'][0], box2['max'][1])
    boxes[2] = box2

    box3 = {}
    box3['min'] = [(minc[0]), (minc[1] + deltay)]
    box3['max'] = [(minc[0] + deltax), (maxc[1])]
    box3['sw_bound'] = "{0},{1}".format(box3['min'][0], box3['min'][1])
    box3['ne_bound'] = "{0},{1}".format(box3['max'][0], box3['max'][1])
    boxes[3] = box3

    box4 = {}
    box4['min'] = [(minc[0] + deltax), (minc[1] + deltay)]
    box4['max'] = [(maxc[0]), (maxc[1])]
    box4['sw_bound'] = "{0},{1}".format(box4['min'][0], box4['min'][1])
    box4['ne_bound'] = "{0},{1}".format(box4['max'][0], box4['max'][1])
    boxes[4] = box4



    return boxes

def resplitBounds(box):


    maxc = box['max']
    minc = box['min']
    boxes = []
    xextent = float(maxc[0]) - float(minc[0])
    yextent = float(maxc[1]) - float(minc[1])

    deltax = xextent / 2
    deltay = xextent / 2
    boxes = {}
    bounds = {}

    box1 = {}
    box1['min'] = [(minc[0]), (minc[1])]
    box1['max'] = [(minc[0] + deltax), (minc[1] + deltay)]
    box1['sw_bound'] = "{0},{1}".format(box1['min'][0], box1['min'][1])
    box1['ne_bound'] = "{0},{1}".format(box1['max'][0], box1['max'][1])
    boxes[1] = box1

    box2 = {}
    box2['min'] = [(minc[0] + deltax), (minc[1])]
    box2['max'] = [(maxc[0]), (minc[1] + deltay)]
    box2['sw_bound'] = "{0},{1}".format(box2['min'][0], box2['min'][1])
    box2['ne_bound'] = "{0},{1}".format(box2['max'][0], box2['max'][1])
    boxes[2] = box2

    box3 = {}
    box3['min'] = [(minc[0]), (minc[1] + deltay)]
    box3['max'] = [(minc[0] + deltax), (maxc[1])]
    box3['sw_bound'] = "{0},{1}".format(box3['min'][0], box3['min'][1])
    box3['ne_bound'] = "{0},{1}".format(box3['max'][0], box3['max'][1])
    boxes[3] = box3

    box4 = {}
    box4['min'] = [(minc[0] + deltax), (minc[1] + deltay)]
    box4['max'] = [(maxc[0]), (maxc[1])]
    box4['sw_bound'] = "{0},{1}".format(box4['min'][0], box4['min'][1])
    box4['ne_bound'] = "{0},{1}".format(box4['max'][0], box4['max'][1])
    boxes[4] = box4



    return boxes

def cityToFips(city, state):
    import csv
    records = []

    # Found at https://www.census.gov/popest/data/cities/totals/2012/files/SUB-EST2012_36.csv
    floc = "/Users/kevindenny/Documents/YelpBuilder/SUB-EST2012_{0}.csv".format(state)

    with open(floc, 'rU') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # print (row.keys())
            # print(row['SUMLEV'])
            if row['SUMLEV'] == '162':
                if city in str(row['NAME']):
                    print row
                    geoid = state.zfill(2) + str(row['PLACE']).zfill(5)

    print geoid
    return geoid


def search(state, city):
    """Query the Census API to get a GeoJSON file for a state

    Args:
        term (str): The search term passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    print city
    print state

    geoid = str(cityToFips(city, state))

    # geoid = '1714000'
    # geoid = '24' + '30325'

    return request(API_HOST, SEARCH_PATH, geoid)

def request(host, path, geoid):
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
    # url_params = url_params or {}
    # url = 'https://{0}{1}{2}'.format(host, urllib.quote(path.encode('utf8')))
    url = 'http://{0}{1}{2}'.format(host, path, geoid)
    print(url)


    # consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    # oauth_request = oauth2.Request(
    #     method="GET", url=url, parameters=url_params)
    #
    # oauth_request.update(
    #     {
    #         'oauth_nonce': oauth2.generate_nonce(),
    #         'oauth_timestamp': oauth2.generate_timestamp(),
    #         'oauth_token': TOKEN,
    #         'oauth_consumer_key': CONSUMER_KEY
    #     }
    # )
    # token = oauth2.Token(TOKEN, TOKEN_SECRET)
    # oauth_request.sign_request(
    #     oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    # signed_url = oauth_request.to_url()
    #
    # print u'Querying {0} ...'.format(url)

    # conn = urllib2.urlopen(signed_url, None)

    conn = urllib2.urlopen(url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    # pprint(response)
    return response


def getMax(coordslist):
    maxa = dict()
    maxa['lng'] = -180
    maxa['lat'] = 0
    for co in coordslist:
        if type(co) is list:
            for co1 in co:
                if type(co1) is list:
                    for co2 in co1:

                        if type(co2) is list:
                            for co3 in co2:

                                if type(co3) is list:
                                    for co4 in co3:
                                        print co4
                                elif type(co3) is float:
                                    if co2[0] > maxa['lng']:
                                        maxa['lng'] = co2[0]
                                    if co2[1] > maxa['lat']:
                                        maxa['lat'] = co2[1]


                        elif type(co2) is float:
                            if co1[0] > maxa['lng']:
                                maxa['lng'] = co1[0]
                            if co1[1] > maxa['lat']:
                                maxa['lat'] = co1[1]

                elif type(co1) is float:
                    if co[0] > maxa['lng']:
                        maxa['lng'] = co[0]
                    if co[1] > maxa['lat']:
                        maxa['lat'] = co[1]

        # elif type(co) is float:
        #     if co[0] > maxa['lng']:
        #         maxa['lng'] = co[0]
        #     if co[1] > maxa['lat']:
        #         maxa['lat'] = co[1]

    maxc = [maxa['lat'], maxa['lng']]
    return maxc

def getMin(coordslist):
    mina = dict()
    mina['lng'] = 0
    mina['lat'] = 90
    for co in coordslist:
        if type(co) is list:
            for co1 in co:
                if type(co1) is list:
                    for co2 in co1:

                        if type(co2) is list:
                            for co3 in co2:

                                if type(co3) is list:
                                    for co4 in co3:
                                        print co4
                                elif type(co3) is float:
                                    if co2[0] < mina['lng']:
                                        mina['lng'] = co2[0]
                                    if co2[1] < mina['lat']:
                                        mina['lat'] = co2[1]


                        elif type(co2) is float:
                            if co1[0] < mina['lng']:
                                mina['lng'] = co1[0]
                            if co1[1] < mina['lat']:
                                mina['lat'] = co1[1]

                elif type(co1) is float:
                    if co[0] < mina['lng']:
                        mina['lng'] = co[0]
                    if co[1] < mina['lat']:
                        mina['lat'] = co[1]

        # elif type(co) is float:
        #     if co[0] > maxa['lng']:
        #         maxa['lng'] = co[0]
        #     if co[1] > maxa['lat']:
        #         maxa['lat'] = co[1]

    minc = [mina['lat'], mina['lng']]
    return minc




