from typing import Final
from enum import Enum

# NAW URL
NAW_URL: Final = "https://www.lostarkmarket.online/api/export-market-live/North America West"

SUPPORTED_ITEMS = ["ghl", "mhl", "rhl", "destruction", "guardian", "obl", "prot", "refObl", "refProt","basic", "superior", "prime", "pouch", "bc"]

ID_MAPPING = {
    179710669761937408: "ZerO_0",
    100391590270357504: "Wangaroo",
    431999222628352000: "Ikpn",
    332419378861834240: "coolguy1002??",
    89487931223322624: "LucidiT"
}

class GEAR_TIER(Enum):
    argos = "argos"
    brel = "brel"

class GEAR_TYPE(Enum):
    weapon = "weapon"
    armor = "armor"