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
        "mhl" : "marvelous-honor-leapstone-3",
        "destruction" : "crystallized-destruction-stone-0",
        "guardian" : "crystallized-guardian-stone-0",
        "obliteration" : "obliteration-stone-1",
        "protection" : "protection-stone-1",
        "basic" : "basic-oreha-fusion-material-2",
        "superior" : "superior-oreha-fusion-material-4",
        "pouch" : "honor-shard-pouch-s-1",
        "bc" : "blue-crystal-0",
    }
    return items[itemStr]


