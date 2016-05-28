'''
Test.py contains methods for
querying the methods created in Yelp.py
to get and write results. The variables are inputted in this file
'''

__author__ = 'kdenny'

from yelp import calcBusinessList, writeResults
from yelpstring import calcBusinessListA
from SpatialExtent import search, getMax, getMin, calcBound

import oauth2 as oauth
import simplejson as json
import requests
from pprint import pprint



# Ithaca coordinates
# sw_coord = "42.413013,-76.535798"
# ne_coord = "42.461155,-76.472283"
#
# # # Bound format: SW Latitude, SW Longitude|
# bound = "{0}|{1}".format(sw_coord, ne_coord)


# # The list of all of the types of businesses to search for
# businessTypes = ['deptstores',
#                  # 'discountstore',
#                  # 'drugstores',
#                  'homeandgarden',
#                  'officeequipment',
#                  # 'shoppingcenters',
#                  'sportgoods',
#                  'tobaccoshops',
#                  'usedbooks',
#                  'toys',
#                  'vitaminssupplements',
#                  # 'mobilephones',
#                  'headshops',
#                  'flowers',
#                  'fashion',
#                  'electronics',
#                  'media',
#                  'artsandcrafts',
#                  # 'antiques',
#                  'wholesale_stores'
#                  ]

# Input variables
floc = "/Users/kevindenny/Documents/YelpBuilder/Results/" # Where to save file

# What to search for
searchstring = ['Rent A Center']
city = 'New York'
state = '36'

# Get City bounds
bound = calcBound(city, state)
print(bound)



# Calculate the list of businesses
bizresults = calcBusinessListA(searchstring,bound,city,state)


# Save the result
fname = "{0}rentacenter.csv".format(city)
writeResults(floc, fname, bizresults)

