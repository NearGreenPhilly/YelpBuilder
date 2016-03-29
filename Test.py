'''
Test.py contains methods for
querying the methods created in Yelp.py
to get and write results. The variables are inputted in this file
'''

__author__ = 'kdenny'

from yelp import calcBusinessList, writeResults

import oauth2 as oauth
import simplejson as json
import requests
from pprint import pprint

# Philly Pizza Example
# sw_coord = "39.945412,-75.244219"
# ne_coord = "39.971893,-75.159397"
# businessTypes = ['pizza']

# Ithaca coordinates
sw_coord = "42.413013,-76.535798"
ne_coord = "42.461155,-76.472283"

# The list of all of the types of businesses to search for
businessTypes = ['deptstores','discountstore','drugstores','homeandgarden','officeequipment','shoppingcenters',
                 'sportgoods','tobaccoshops','usedbooks','toys','vitaminssupplements','mobilephones','headshops','flowers',
                 'fashion','electronics','media','artsandcrafts','antiques','wholesale_stores']

# Where to save the file at
floc = "C:/Users/kdenny/Documents/YelpBuilder/Results/"

fname = "Ithaca.csv"

# Bound format: SW Latitude, SW Longitude|
bound = "{0}|{1}".format(sw_coord, ne_coord)


# Calculate the list of businesses
bizresults = calcBusinessList(businessTypes,bound)


# Save the result
writeResults(floc, fname, bizresults)

