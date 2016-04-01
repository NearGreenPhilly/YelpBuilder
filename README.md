Yelp builder - Used to create data files for businesses within a specific area
------------------------

To Install

Open a console, cd to this directory and:

$ pip install -r requirements.txt


Inputs

- Business types list: A comma delimited list of all the business categories you wish to search for. A relatively comprehensive list of retail business types is
included in the current
- Bounding box: The area to be searched, created from the SW and NE coordinates


Current Process Flow

- Input a list of all business types to query into Test.py
- Input the city and state FIPS code you want - need to add state Places dictionary from Census for each state
- Bounding box is computed from min / max extent of city
- If the Yelp API returns max results (= 20), split the bounding box into quadrants and iterate through the newly created quadrants






