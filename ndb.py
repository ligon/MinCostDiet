
from urllib.request import Request, urlopen
import pandas as pd
import json
import warnings
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError
ureg = UnitRegistry()
ureg.load_definitions('./Data/food_units.txt') 
import numpy as np

#%matplotlib inline

import requests

def ndb_search(apikey, term, url = 'https://api.nal.usda.gov/ndb/search'):
    """
    Search Nutrition DataBase, using apikey and string "term" as search criterion.

    Returns a pd.DataFrame of results.
    """
    parms = (('format', 'json'),('q', term),('api_key', apikey))
    r = requests.get(url, params = parms)
    if 'list' in r.json():
        l = r.json()['list']['item']
    else: 
        return []

    return pd.DataFrame(l)

def ndb_report(apikey, ndbno, url = 'https://api.nal.usda.gov/ndb/V2/reports'):
    """Construct a food report for food with given ndbno.  

    Nutrients are given per 100 g or 100 ml of the food.
    """
    params = (('ndbno', ndbno),('type', 'b'),('format', 'json'),('api_key', apikey))

    try:
        r = requests.get(url, params = params)
        L = r.json()['foods'][0]['food']['nutrients']
    except KeyError:
        warnings.warn("Couldn't find NDB=%s." % ndbno)
        return None

    v = {}
    u = {}
    for l in L:
        v[l['name']] = l['value']  # Quantity
        u[l['name']] = l['unit']  # Units

    #print(l)
    N = pd.DataFrame({'Quantity':v,'Units':u})

    return N

def ndb_units(q,u,ureg=ureg):
    """Convert quantity q of units u to 100g or 100ml."""
    try:
        x = ureg.Quantity(float(q),u)
    except UndefinedUnitError:
        return ureg.Quantity(np.NaN,'ml')

    try:
        return x.to(ureg.hectogram)
    except DimensionalityError:
        return x.to(ureg.deciliter)
