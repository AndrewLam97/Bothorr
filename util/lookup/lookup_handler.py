import requests
from util import constants

# Singular Item Lookup
def get_item_data(itemStr):
    params = {'items' : item_translator(itemStr)}
  
    response = requests.get(constants.NAW_URL, params)

    return response

# Translates shorthand item name into API-compliant item name
def item_translator(itemStr):
    items = {
        "ghl" : "great-honor-leapstone-2",
        "red" : "crystallized-destruction-stone-0",
        "blue" : "crystallized-guardian-stone-0",
        "fusion" : "basic-oreha-fusion-material-2",
        "pouch" : "honor-shard-pouch-s-1",
        "bc" : "blue-crystal-0",
    }
    return items[itemStr]


