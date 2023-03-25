from abc import ABC, abstractmethod
from util.constants import GEAR_TIER
import os
import json, math
from util.lookup import lookup_handler
from models.honing import Honing

class HoningStrategy(ABC):
    
    def calculate_num_taps_to_pity(self, targetLevel: str) -> int:
        totalBaseHoning = self.data[targetLevel]["baseSuccess"] + self.data[targetLevel]["strongHoldBuff"] + self.data[targetLevel]["globalBuff"]
        honingIncrement = self.data[targetLevel]["baseSuccess"]/10
        maxHoningProbability = totalBaseHoning + self.data[targetLevel]["baseSuccess"]
        artisanEnergy = 0
        maxHoningAttempts = 1
        while (artisanEnergy < 2.15):
            if (min(totalBaseHoning+honingIncrement*(maxHoningAttempts-1), maxHoningProbability) > 1.0):
                break
            else:
                artisanEnergy+=min(totalBaseHoning+honingIncrement*(maxHoningAttempts-1), maxHoningProbability)
                maxHoningAttempts+=1
        return maxHoningAttempts
    
    def calculate_expected_num_taps(self, targetLevel: int) -> float:
        maxHoningAttempts = self.calculate_num_taps_to_pity(targetLevel)
        totalBaseHoning = self.data[targetLevel]["baseSuccess"] + self.data[targetLevel]["strongHoldBuff"] + self.data[targetLevel]["globalBuff"]
        maxHoningProbability = totalBaseHoning + self.data[targetLevel]["baseSuccess"]
        honingIncrement = self.data[targetLevel]["baseSuccess"]/10
        expectedValue = 0
        for i in range(0, maxHoningAttempts):
            if (i == 0):
                expectedValue+=totalBaseHoning
            elif (i == maxHoningAttempts - 1):
                failedHoningSoFar = 1
                for j in range(0, i):
                    currentFailProbability = max(1-totalBaseHoning-(honingIncrement*j), 1 - maxHoningProbability)
                    failedHoningSoFar = failedHoningSoFar*currentFailProbability
                expectedValue+=failedHoningSoFar*(i+1)
                break
            else:
                failedHoningSoFar = 1
                for j in range(0, i):
                    currentFailProbability = max(1-totalBaseHoning-(honingIncrement*j), 1 - maxHoningProbability)
                    failedHoningSoFar = failedHoningSoFar*currentFailProbability
                currentSuccessProbability = min(totalBaseHoning+(honingIncrement*i), maxHoningProbability)
                test=failedHoningSoFar*currentSuccessProbability*(i+1)
                expectedValue+=test
        return expectedValue
    
    def convert_artisans_to_num_taps(self, targetLevel: str, artisansEnergy: float) -> int:
        totalBaseHoning = self.data[targetLevel]["baseSuccess"] + self.data[targetLevel]["strongHoldBuff"] + self.data[targetLevel]["globalBuff"]
        honingIncrement = self.data[targetLevel]["baseSuccess"]/10
        maxHoningProbability = totalBaseHoning + self.data[targetLevel]["baseSuccess"]
        attempts = 1
        base = 0
        while (base < artisansEnergy/100):
            base+=min(totalBaseHoning+honingIncrement*(attempts-1), maxHoningProbability)/2.15
            attempts+=1
        return attempts
    
    @abstractmethod
    def calculate_honing_materials_used(self, targetLevel: int, numberOfHones: int) -> dict:
        raise NotImplementedError
    
    # Used by specialized honing behaviors to calculate total gold value of honing given a honing object from DB, which will be used for graphing historic hones
    @abstractmethod
    def calculate_gold_value_of_materials_used(self, material_deviation_values: dict) -> int:
        raise NotImplementedError
    
    # Used to compose output of honing attempt to discord channel
    # Example: You lost 4 mhls, 171 blues, 432 shards, 2 fusions, and 216 raw gold by 14 tapping compared to the average scenario. With current market values, you lost a grand total of 529 gold
    @abstractmethod
    def compose_honing_message(self, materialsUsedDict: dict, numberOfHones: int) -> None:
        raise NotImplementedError
    
class ArgosWeaponHoningStrategy(HoningStrategy):
    
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        file_path = os.path.join(absolute_path, "honing_values.json")
        f = open(file_path)
        self.data = json.load(f)["t3"]["1340"]["weapon"]
        self.lookup_handler = lookup_handler
        self.gear_tier = GEAR_TIER.argos
        self.WIN_STRING = "You saved {} ghls, {} crystallized destruction stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a total of {} gold"
        self.LOSS_STRING = "You lost {} ghls, {} crystallized destruction stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you lost a total of {} gold"
    
    def calculate_honing_materials_used(self, targetLevel: str, numberOfHones: int) -> dict:
        leaps = self.data[targetLevel]["leapstone"]
        reds = self.data[targetLevel]["red"]
        fusions = self.data[targetLevel]["fusion"]
        gold = self.data[targetLevel]["gold"]
        shards = self.data[targetLevel]["shard"]
        initialShards = self.data[targetLevel]["initialShard"]
        expectedNumTaps = self.calculate_expected_num_taps(targetLevel)
        
        expectedLeaps = math.ceil(expectedNumTaps*leaps)
        expectedReds = math.ceil(expectedNumTaps*reds)
        expectedFusions = math.ceil(expectedNumTaps*fusions)
        expectedGold = math.ceil(expectedNumTaps*gold)
        expectedShards = math.ceil(expectedNumTaps*shards) + initialShards
        
        actualLeaps = leaps*numberOfHones
        actualReds = reds*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        actualShards = shards*numberOfHones + initialShards
        
        material_deviation_from_mean = {
            "leaps": int(expectedLeaps - actualLeaps),
            "blues": 0,
            "reds": int(expectedReds - actualReds),
            "fusions": int(expectedFusions - actualFusions),
            "gold": int(expectedGold - actualGold),
            "shards": int(expectedShards - actualShards),
        }
        return material_deviation_from_mean
    
    def calculate_gold_value_of_materials_used(self, material_deviation_values: dict) -> int:
        leapstoneValue = self.lookup_handler.get_item_data("leapstone", "argos").json()[0]['avgPrice']
        blueValue = self.lookup_handler.get_item_data("blue", "argos").json()[0]['avgPrice'] / 10
        redValue = self.lookup_handler.get_item_data("red", "argos").json()[0]['avgPrice'] / 10
        fusionValue = self.lookup_handler.get_item_data("fusion", "argos").json()[0]['avgPrice']
        
        total = int(material_deviation_values["leaps"]*leapstoneValue + 
                    material_deviation_values["blues"]*blueValue + 
                    material_deviation_values["reds"]*redValue +
                    material_deviation_values["fusions"]*fusionValue + 
                    material_deviation_values["gold"])
        return total
    
    def compose_honing_message(self, material_deviation_values: dict, numberOfHones: int) -> None:
        if material_deviation_values["leaps"] >= 0:
            outputStr = self.WIN_STRING
        else:
            outputStr = self.LOSS_STRING
        return outputStr.format(
            abs(material_deviation_values["leaps"]),
            abs(material_deviation_values["reds"]),
            abs(material_deviation_values["shards"]),
            abs(material_deviation_values["fusions"]),
            abs(material_deviation_values["gold"]),
            numberOfHones,
            abs(self.calculate_gold_value_of_materials_used(material_deviation_values))
        )

class ArgosArmorHoningStrategy(HoningStrategy):
    
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        file_path = os.path.join(absolute_path, "honing_values.json")
        f = open(file_path)
        self.data = json.load(f)["t3"]["1340"]["armor"]
        self.lookup_handler = lookup_handler
        self.gear_tier = GEAR_TIER.argos
        self.WIN_STRING = "You saved {} ghls, {} crystallized guardian stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a total of {} gold"
        self.LOSS_STRING = "You lost {} ghls, {} crystallized guardian stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you lost a total of {} gold"
    
    def calculate_honing_materials_used(self, targetLevel: str, numberOfHones: int) -> dict:
        leaps = self.data[targetLevel]["leapstone"]
        blues = self.data[targetLevel]["blue"]
        fusions = self.data[targetLevel]["fusion"]
        gold = self.data[targetLevel]["gold"]
        shards = self.data[targetLevel]["shard"]
        initialShards = self.data[targetLevel]["initialShard"]
        expectedNumTaps = self.calculate_expected_num_taps(targetLevel)
        
        expectedLeaps = math.ceil(expectedNumTaps*leaps)
        expectedBlues = math.ceil(expectedNumTaps*blues)
        expectedFusions = math.ceil(expectedNumTaps*fusions)
        expectedGold = math.ceil(expectedNumTaps*gold)
        expectedShards = math.ceil(expectedNumTaps*shards) + initialShards
        
        actualLeaps = leaps*numberOfHones
        actualBlues = blues*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        actualShards = shards*numberOfHones + initialShards
        
        material_deviation_from_mean = {
            "leaps": int(expectedLeaps - actualLeaps),
            "blues": int(expectedBlues - actualBlues),
            "reds": 0,
            "fusions": int(expectedFusions - actualFusions),
            "gold": int(expectedGold - actualGold),
            "shards": int(expectedShards - actualShards),
        }
        return material_deviation_from_mean
    
    def calculate_gold_value_of_materials_used(self, material_deviation_values) -> int:
        leapstoneValue = self.lookup_handler.get_item_data("leapstone", "argos").json()[0]['avgPrice']
        blueValue = self.lookup_handler.get_item_data("blue", "argos").json()[0]['avgPrice'] / 10
        redValue = self.lookup_handler.get_item_data("red", "argos").json()[0]['avgPrice'] / 10
        fusionValue = self.lookup_handler.get_item_data("fusion", "argos").json()[0]['avgPrice']
        
        total = int(material_deviation_values["leaps"]*leapstoneValue + 
                    material_deviation_values["blues"]*blueValue + 
                    material_deviation_values["reds"]*redValue +
                    material_deviation_values["fusions"]*fusionValue + 
                    material_deviation_values["gold"])
        return total
    
    def compose_honing_message(self, material_deviation_values: dict, numberOfHones: int) -> None:
        if material_deviation_values["leaps"] >= 0:
            outputStr = self.WIN_STRING
        else:
            outputStr = self.LOSS_STRING
        return outputStr.format(
            abs(material_deviation_values["leaps"]),
            abs(material_deviation_values["blues"]),
            abs(material_deviation_values["shards"]),
            abs(material_deviation_values["fusions"]),
            abs(material_deviation_values["gold"]),
            numberOfHones,
            abs(self.calculate_gold_value_of_materials_used(material_deviation_values))
        )

class BrelWeaponHoningStrategy(HoningStrategy):
    
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        file_path = os.path.join(absolute_path, "honing_values.json")
        f = open(file_path)
        self.data = json.load(f)["t3"]["1390"]["weapon"]
        self.lookup_handler = lookup_handler
        self.gear_tier = GEAR_TIER.brel
        self.WIN_STRING = "You saved {} mhls, {} obliteration stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a total of {} gold"
        self.LOSS_STRING = "You lost {} mhls, {} obliteration stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you lost a total of {} gold"
    
    def calculate_honing_materials_used(self, targetLevel: str, numberOfHones: int) -> dict:
        leaps = self.data[targetLevel]["leapstone"]
        reds = self.data[targetLevel]["red"]
        fusions = self.data[targetLevel]["fusion"]
        gold = self.data[targetLevel]["gold"]
        shards = self.data[targetLevel]["shard"]
        initialShards = self.data[targetLevel]["initialShard"]
        expectedNumTaps = self.calculate_expected_num_taps(targetLevel)
        
        expectedLeaps = math.ceil(expectedNumTaps*leaps)
        expectedReds = math.ceil(expectedNumTaps*reds)
        expectedFusions = math.ceil(expectedNumTaps*fusions)
        expectedGold = math.ceil(expectedNumTaps*gold)
        expectedShards = math.ceil(expectedNumTaps*shards) + initialShards
        
        actualLeaps = leaps*numberOfHones
        actualReds = reds*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        actualShards = shards*numberOfHones + initialShards
        
        material_deviation_from_mean = {
            "leaps": int(expectedLeaps - actualLeaps),
            "blues": 0,
            "reds": int(expectedReds - actualReds),
            "fusions": int(expectedFusions - actualFusions),
            "gold": int(expectedGold - actualGold),
            "shards": int(expectedShards - actualShards),
        }
        return material_deviation_from_mean
    
    def calculate_gold_value_of_materials_used(self, material_deviation_values) -> int:
        leapstoneValue = self.lookup_handler.get_item_data("leapstone", "brel").json()[0]['avgPrice']
        blueValue = self.lookup_handler.get_item_data("blue", "brel").json()[0]['avgPrice'] / 10
        redValue = self.lookup_handler.get_item_data("red", "brel").json()[0]['avgPrice'] / 10
        fusionValue = self.lookup_handler.get_item_data("fusion", "brel").json()[0]['avgPrice']
        
        total = int(material_deviation_values["leaps"]*leapstoneValue + 
                    material_deviation_values["blues"]*blueValue + 
                    material_deviation_values["reds"]*redValue +
                    material_deviation_values["fusions"]*fusionValue + 
                    material_deviation_values["gold"])
        return total
    
    def compose_honing_message(self, material_deviation_values: dict, numberOfHones: int) -> None:
        if material_deviation_values["leaps"] >= 0:
            outputStr = self.WIN_STRING
        else:
            outputStr = self.LOSS_STRING
        return outputStr.format(
            abs(material_deviation_values["leaps"]),
            abs(material_deviation_values["reds"]),
            abs(material_deviation_values["shards"]),
            abs(material_deviation_values["fusions"]),
            abs(material_deviation_values["gold"]),
            numberOfHones,
            abs(self.calculate_gold_value_of_materials_used(material_deviation_values))
        )

class BrelArmorHoningStrategy(HoningStrategy):
    
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        file_path = os.path.join(absolute_path, "honing_values.json")
        f = open(file_path)
        self.data = json.load(f)["t3"]["1390"]["armor"]
        self.lookup_handler = lookup_handler
        self.gear_tier = GEAR_TIER.brel
        self.WIN_STRING = "You saved {} mhls, {} protection stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a total of {} gold"
        self.LOSS_STRING = "You lost {} mhls, {} protection stones, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you lost a total of {} gold"
    
    def calculate_honing_materials_used(self, targetLevel: str, numberOfHones: int) -> dict:
        leaps = self.data[targetLevel]["leapstone"]
        blues = self.data[targetLevel]["blue"]
        fusions = self.data[targetLevel]["fusion"]
        gold = self.data[targetLevel]["gold"]
        shards = self.data[targetLevel]["shard"]
        initialShards = self.data[targetLevel]["initialShard"]
        expectedNumTaps = self.calculate_expected_num_taps(targetLevel)
        
        expectedLeaps = math.ceil(expectedNumTaps*leaps)
        expectedBlues = math.ceil(expectedNumTaps*blues)
        expectedFusions = math.ceil(expectedNumTaps*fusions)
        expectedGold = math.ceil(expectedNumTaps*gold)
        expectedShards = math.ceil(expectedNumTaps*shards) + initialShards
        
        actualLeaps = leaps*numberOfHones
        actualBlues = blues*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        actualShards = shards*numberOfHones + initialShards
        
        material_deviation_from_mean = {
            "leaps": int(expectedLeaps - actualLeaps),
            "blues": int(expectedBlues - actualBlues),
            "reds": 0,
            "fusions": int(expectedFusions - actualFusions),
            "gold": int(expectedGold - actualGold),
            "shards": int(expectedShards - actualShards),
        }
        return material_deviation_from_mean
    
    def calculate_gold_value_of_materials_used(self, material_deviation_values) -> int:
        leapstoneValue = self.lookup_handler.get_item_data("leapstone", "brel").json()[0]['avgPrice']
        blueValue = self.lookup_handler.get_item_data("blue", "brel").json()[0]['avgPrice'] / 10
        redValue = self.lookup_handler.get_item_data("red", "brel").json()[0]['avgPrice'] / 10
        fusionValue = self.lookup_handler.get_item_data("fusion", "brel").json()[0]['avgPrice']
        
        total = int(material_deviation_values["leaps"]*leapstoneValue + 
                    material_deviation_values["blues"]*blueValue + 
                    material_deviation_values["reds"]*redValue +
                    material_deviation_values["fusions"]*fusionValue + 
                    material_deviation_values["gold"])
        return total
    
    def compose_honing_message(self, material_deviation_values: dict, numberOfHones: int) -> None:
        if material_deviation_values["leaps"] >= 0:
            outputStr = self.WIN_STRING
        else:
            outputStr = self.LOSS_STRING
        return outputStr.format(
            abs(material_deviation_values["leaps"]),
            abs(material_deviation_values["blues"]),
            abs(material_deviation_values["shards"]),
            abs(material_deviation_values["fusions"]),
            abs(material_deviation_values["gold"]),
            numberOfHones,
            abs(self.calculate_gold_value_of_materials_used(material_deviation_values))
        )
