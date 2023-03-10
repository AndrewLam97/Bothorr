import json
import math
import os

import discord
from sqlalchemy import desc
from sqlalchemy.sql import func

from db_connection import Session
from models.honing import Honing
from util.lookup import lookup_handler
from util.honing import weapon_honing_calculator, armor_honing_calculator

WIN_STRING = "You saved {} {}, {} {}, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a grand total of {} gold"
LOSS_STRING = "You lost {} {}, {} {}, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you lost a grand total of {} gold"
class HoningCalculator:
    def __init__(self):
        absolute_path = os.path.dirname(__file__)
        file_path = os.path.join(absolute_path, "honing_values.json")
        f = open(file_path)
        self.data = json.load(f)
        self.lookup_handler = lookup_handler
        self.weapon_honing_calculator = weapon_honing_calculator.WeaponHoningCalculator()
        self.armor_honing_calculator = armor_honing_calculator.ArmorHoningCalculator()
        self.weapon_honing_calculator_methods = [f for f in dir(weapon_honing_calculator.WeaponHoningCalculator) if not f.startswith("_")]
        self.armor_honing_calculator_methods = [f for f in dir(armor_honing_calculator.ArmorHoningCalculator) if not f.startswith("_")]
        
    def __getattr__(self, func):
        def method(*args):
            *usedArgs, honingPiece = args
            if (args[-1] == "weapon" and func in self.weapon_honing_calculator_methods):
                return getattr(self.weapon_honing_calculator, func)(*usedArgs)
            elif (args[-1] == "armor" and func in self.armor_honing_calculator_methods):
                
                return getattr(self.armor_honing_calculator, func)(*usedArgs)
            else:
                raise AttributeError
        return method
    
    # Calculate how many hones to reach pity and then succeed
    def calculate_max_attempts(self, totalBaseHoning, honingIncrement, maxHoningProbability) -> int:
        artisanEnergy = 0
        maxHoningAttempts = 1
        while (artisanEnergy < 2.15):
            if (min(totalBaseHoning+honingIncrement*(maxHoningAttempts-1), maxHoningProbability) > 1.0):
                break
            else:
                artisanEnergy+=min(totalBaseHoning+honingIncrement*(maxHoningAttempts-1), maxHoningProbability)
                maxHoningAttempts+=1
        return maxHoningAttempts
    
    def calculateGoldTotal(self, material_deviation_values: dict, honingTier: str) -> int:
        leapstoneValue = self.lookup_handler.get_item_data("leapstone", honingTier).json()[0]['avgPrice']
        blueValue = self.lookup_handler.get_item_data("blue", honingTier).json()[0]['avgPrice'] / 10
        redValue = self.lookup_handler.get_item_data("red", honingTier).json()[0]['avgPrice'] / 10
        fusionValue = self.lookup_handler.get_item_data("fusion", honingTier).json()[0]['avgPrice']
        
        total = int(material_deviation_values["leaps"]*leapstoneValue + 
                    material_deviation_values["blues"]*blueValue + 
                    material_deviation_values["reds"]*redValue +
                    material_deviation_values["fusions"]*fusionValue + 
                    material_deviation_values["gold"])
        return total
    
    def saveAndOutputCalculatedValues(self, targetLevel: int, numberOfHones: int, honingTier: str, message: any, honingPiece: str):
        # Deviation is calculated as expected - actual
        # Positive means expected materials is greater than actual materials used, aka a win
        material_deviation_values = self.calculate(targetLevel, numberOfHones, honingTier, self.data, self.calculate_expected_value_honing, honingPiece)
        outputStr = WIN_STRING if material_deviation_values["leaps"] > 0 else LOSS_STRING
        
        # Commit mats used to db
        with Session() as sess:
            newHone = Honing(
                discordId=message.author.id,
                discordUsername=message.author.name,
                tierBaseItemLevel=1340 if honingTier == "argos" else 1390,
                itemType=honingPiece,
                numberOfTaps=numberOfHones,
                outputLevel=targetLevel,
                goldUsedFromAvg=material_deviation_values["gold"],
                shardsUsedFromAvg=material_deviation_values["shards"],
                leapstonesUsedFromAvg=material_deviation_values["leaps"],
                blueStonesUsedFromAvg=material_deviation_values["blues"],
                redStonesUsedFromAvg=material_deviation_values["reds"],
                fusionsUsedFromAvg=material_deviation_values["fusions"],
            )
            print(newHone)
            sess.add(newHone)
            sess.commit()
        msg = outputStr.format(
            str(abs(material_deviation_values["leaps"])),
            "mhls" if honingTier == "brel" else "ghls",
            str(abs(material_deviation_values["blues"])) if honingPiece == "armor" else str(abs(material_deviation_values["reds"])),
            "blues" if honingPiece == "armor" else "reds", 
            str(abs(material_deviation_values["shards"])), str(abs(material_deviation_values["fusions"])), str(abs(material_deviation_values["gold"])),
            str(numberOfHones), str(abs(self.calculateGoldTotal(material_deviation_values, honingTier)))
        )
        return msg
        
        
    def calculate_honing_historic(self, message):
        with Session() as sess:
            argos_honings = reversed(sess.query(Honing).filter(Honing.discordId == str(message.author.id) and Honing.tierBaseItemLevel == 1340).order_by(desc(Honing.id), Honing.numberOfTaps).all())
            brel_honings = reversed(sess.query(Honing).filter(Honing.discordId == str(message.author.id) and Honing.tierBaseItemLevel == 1390).order_by(desc(Honing.id), Honing.numberOfTaps).all())

        argosBlueValue = lookup_handler.get_item_data("blue", "argos").json()[0]['avgPrice'] / 10
        argosRedValue = lookup_handler.get_item_data("red", "argos").json()[0]['avgPrice'] / 10
        ghlValue = lookup_handler.get_item_data("leapstone", "argos").json()[0]['avgPrice']
        argosFusionValue = lookup_handler.get_item_data("fusion", "argos").json()[0]['avgPrice']
        brelBlueValue = lookup_handler.get_item_data("blue", "brel").json()[0]['avgPrice'] / 10
        brelRedValue = lookup_handler.get_item_data("red", "brel").json()[0]['avgPrice'] / 10
        mhlValue = lookup_handler.get_item_data("leapstone", "brel").json()[0]['avgPrice']
        brelFusionValue = lookup_handler.get_item_data("fusion", "brel").json()[0]['avgPrice']
        count = 0
        total = 0
        ordered_honings = {}

        for honing in argos_honings:
            subtotal = ghlValue*honing.leapstonesUsedFromAvg + argosRedValue*honing.redStonesUsedFromAvg + argosFusionValue*honing.fusionsUsedFromAvg + argosBlueValue*honing.blueStonesUsedFromAvg + honing.goldUsedFromAvg
            total += subtotal
            # if __debug__:
            #     print("ID:", honing.id, "-- Subtotal:", subtotal)
            ordered_honings[count] = [subtotal, total]
            count+=1
            
        for honing in brel_honings:
            subtotal = mhlValue*honing.leapstonesUsedFromAvg + brelRedValue*honing.redStonesUsedFromAvg + brelFusionValue*honing.fusionsUsedFromAvg + brelBlueValue*honing.blueStonesUsedFromAvg + honing.goldUsedFromAvg
            total += subtotal
            # if __debug__:
            #     print("ID:", honing.id, "-- Subtotal:", subtotal)
            ordered_honings[count] = [subtotal, total]
            count+=1

        return ordered_honings
    
    #Calculate the expected number of material used, based on the input material
    def calculate_expected_value_honing(self, honingValues: dict, materialUsedPerHone: int):
        baseHoning = honingValues["baseSuccess"]
        strongHoldBuff = honingValues["strongHoldBuff"]
        globalBuff = honingValues["globalBuff"]
        honingIncrement = baseHoning/10
        totalBaseHoning = baseHoning + strongHoldBuff + globalBuff
        maxHoningProbability = totalBaseHoning + baseHoning
        maxHoningAttempts = self.calculate_max_attempts(totalBaseHoning, honingIncrement, maxHoningProbability)
        expectedValue = 0
        for i in range(0, maxHoningAttempts):
            if (i == 0):
                expectedValue+=materialUsedPerHone*totalBaseHoning
            elif (i == maxHoningAttempts - 1):
                failedHoningSoFar = 1
                for j in range(0, i):
                    currentFailProbability = max(1-totalBaseHoning-(honingIncrement*j), 1 - maxHoningProbability)
                    failedHoningSoFar = failedHoningSoFar*currentFailProbability
                expectedValue+=failedHoningSoFar*materialUsedPerHone*(i+1)
                break
            else:
                failedHoningSoFar = 1
                for j in range(0, i):
                    currentFailProbability = max(1-totalBaseHoning-(honingIncrement*j), 1 - maxHoningProbability)
                    failedHoningSoFar = failedHoningSoFar*currentFailProbability
                currentSuccessProbability = min(totalBaseHoning+(honingIncrement*i), maxHoningProbability)
                test=failedHoningSoFar*currentSuccessProbability*materialUsedPerHone*(i+1)
                expectedValue+=test
        return math.ceil(expectedValue)
    
    def calculate_attempts_from_artisans(self, artisansEnergy, targetLvl, gearType, honingTier) -> int:
        tierIlvl = "1340" if honingTier == "argos" else "1390"
        totalBaseHoning = self.data["t3"][tierIlvl][gearType][str(targetLvl)]["baseSuccess"] + self.data["t3"][tierIlvl][gearType][str(targetLvl)]["strongHoldBuff"] + self.data["t3"][tierIlvl][gearType][str(targetLvl)]["globalBuff"]
        honingIncrement = self.data["t3"][tierIlvl][gearType][str(targetLvl)]["baseSuccess"]/10
        maxHoningProbability = self.data["t3"][tierIlvl][gearType][str(targetLvl)]["baseSuccess"]*2
        attempts = 1
        base = 0
        while (base < artisansEnergy/100):
            base+=min(totalBaseHoning+honingIncrement*(attempts-1), maxHoningProbability)/2.15
            attempts+=1
        return attempts

async def list_all_hones(message):
    with Session() as sess:
        honings = sess.query(Honing).filter(Honing.discordId == str(message.author.id)).order_by(desc(Honing.outputLevel), Honing.numberOfTaps).all()

    blues = 0
    reds = 0
    leaps = 0
    fusions = 0
    rawGold = 0
    blueValue = lookup_handler.get_item_data("guardian").json()[0]['avgPrice'] / 10
    redValue = lookup_handler.get_item_data("destruction").json()[0]['avgPrice'] / 10
    ghlValue = lookup_handler.get_item_data("ghl").json()[0]['avgPrice']
    fusionValue = lookup_handler.get_item_data("basic").json()[0]['avgPrice']
    honingDescriptionMap = {}

    for honing in honings:
        blues+=honing.blueStonesUsedFromAvg
        reds+=honing.redStonesUsedFromAvg
        leaps+=honing.leapstonesUsedFromAvg
        fusions+=honing.fusionsUsedFromAvg
        rawGold+=honing.goldUsedFromAvg
        # Example: 19 tap 20 armor
        key = "{} tap {} {}".format(str(honing.numberOfTaps), str(honing.outputLevel), str(honing.itemType.value))
        if key in honingDescriptionMap:
            honingDescriptionMap[key] = str(int(honingDescriptionMap[key]) + 1)
        else:
            honingDescriptionMap[key] = "1"
    
    total = ghlValue*leaps + redValue*reds + fusionValue*fusions + blueValue*blues + rawGold 
    print(ghlValue, redValue, fusionValue, blueValue)
    embedVar = discord.Embed(title=f"{message.author.name}'s Hones", color=(discord.Color.green() if rawGold > 0 else discord.Color.red()))
    if (len("\n".join(list(honingDescriptionMap.keys()))) <= 1024):
        embedVar.add_field(name="Description", value="\n".join(list(honingDescriptionMap.keys())))
        embedVar.add_field(name="Number of times", value="\n".join(list(honingDescriptionMap.values())))
    embedVar.add_field(name="Summary of mats saved", inline=False, value="Raw Gold Saved: {}, Blue Saved: {}, Red Saved: {}, Leaps Saved: {}, Fusions Saved: {}".format(rawGold, blues, reds, leaps, fusions))
    embedVar.add_field(name="TOTAL GOLD SAVED", inline=False, value=str(int(total)))
    await message.channel.send("Too many hones, sending a summary for now")
    await message.channel.send(embed=embedVar)
