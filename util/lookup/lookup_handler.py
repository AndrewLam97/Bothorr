import requests

from util import constants


# Singular Item Lookup
def get_item_data(itemStr: str, honingTier: str):
    params = {'items' : item_translator(itemStr, honingTier)}

    response = requests.get(constants.NAW_URL, params)

    return response

# Translates shorthand item name into API-compliant item name
def item_translator(itemStr, honingTier):
    if (honingTier == "argos"):
        items = {
            "leapstone" : "great-honor-leapstone-2",
            "red" : "crystallized-destruction-stone-0",
            "blue" : "crystallized-guardian-stone-0",
            "fusion" : "oreha-fusion-material-2",
            "pouch" : "honor-shard-pouch-s-1",
        }
    elif (honingTier == "brel"):
        items = {
            "leapstone" : "marvelous-honor-leapstone-3",
            "red" : "obliteration-stone-1",
            "blue" : "protection-stone-1",
            "fusion" : "superior-oreha-fusion-material-3",
            "pouch" : "honor-shard-pouch-s-1",
        }
    return items[itemStr]

def get_item_lookup(itemStr):
    items = {
        "ghl" : "great-honor-leapstone-2",
        "mhl" : "marvelous-honor-leapstone-3",
        "rhl" : "radiant-honor-leapstone-3",
        "destruction" : "crystallized-destruction-stone-0",
        "guardian" : "crystallized-guardian-stone-0",
        "obl" : "obliteration-stone-1",
        "prot" : "protection-stone-1",
        "refObl" : "refined-obliteration-stone-0",
        "refProt" : "refined-protection-stone-0",
        "basic" : "oreha-fusion-material-2",
        "superior" : "superior-oreha-fusion-material-3",
        "prime" : "prime-oreha-fusion-material-4",
        "pouch" : "honor-shard-pouch-s-1",
        "bc" : "blue-crystal-0",
    }
    params = {'items' : items[itemStr]}
    response = requests.get(constants.NAW_URL, params)
    return response