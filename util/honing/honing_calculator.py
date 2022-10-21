import json
import os
import math
from util.lookup import lookup_handler
from db_connection import Session
from models.honing import Honing
from sqlalchemy.sql import func
from sqlalchemy import desc
import discord

absolute_path = os.path.dirname(__file__)
file_path = os.path.join(absolute_path, "honing_values.json")
f = open(file_path)
data = json.load(f)

winString = "You saved {} GHLs, {} {}, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a grand total of {} gold"
lossString = "You lost {} GHLs, {} {}, {} shards, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you lost a grand total of {} gold"

async def list_all_hones(message):
    with Session() as sess:
        honings = sess.query(Honing).filter(Honing.discordId == str(message.author.id)).order_by(desc(Honing.outputLevel), Honing.numberOfTaps).all()
    blues = 0
    reds = 0
    leaps = 0
    fusions = 0
    rawGold = 0
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
    embedVar = discord.Embed(title=f"{message.author.name}'s Hones", color=discord.Color.green())
    embedVar.add_field(name="Description", value="\n".join(list(honingDescriptionMap.keys())))
    embedVar.add_field(name="Number of times", value="\n".join(list(honingDescriptionMap.values())))
    await message.channel.send(embed=embedVar)
    await message.channel.send("Raw Gold Saved: {}, Blue Saved: {}, Red Saved: {}, Leaps Saved: {}, Fusions Saved: {}".format(rawGold, blues, reds, leaps, fusions))

#Calculate honing value wins
#TODO: Use this for honing Ls too
def calculate_honing(message, targetLevel: int, numberOfHones: int, honingPiece: str):
    if honingPiece == "armor":
        ghls = data["t3"][honingPiece][str(targetLevel)]["ghl"]
        blues = data["t3"][honingPiece][str(targetLevel)]["blue"]
        fusions = data["t3"][honingPiece][str(targetLevel)]["fusion"]
        gold = data["t3"][honingPiece][str(targetLevel)]["gold"]
        shards = data["t3"][honingPiece][str(targetLevel)]["shard"]
        initialShards = data["t3"][honingPiece][str(targetLevel)]["initialShard"]
        
        expectedGhls = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], ghls)
        expectedBlues = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], blues)
        expectedFusions = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], fusions)
        expectedGold = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], gold)
        expectedShards = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], shards) + initialShards
        
        actualGhls = ghls*numberOfHones
        actualBlues = blues*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        actualShards = shards*numberOfHones + initialShards
        
        endGhls = abs(int(expectedGhls - actualGhls))
        endBlues = abs(int(expectedBlues - actualBlues))
        endFusions = abs(int(expectedFusions - actualFusions))
        endGold = abs(int(expectedGold - actualGold))
        endShards= abs(int(expectedShards - actualShards))
        endReds = 0
        
        ghlValue = lookup_handler.get_item_data("ghl").json()[0]['avgPrice']
        blueValue = lookup_handler.get_item_data("blue").json()[0]['avgPrice'] / 10
        fusionValue = lookup_handler.get_item_data("fusion").json()[0]['avgPrice']
        
        total = endGhls*ghlValue + endBlues*blueValue + endFusions*fusionValue + endGold
        outputStr = winString if expectedGhls > actualGhls else lossString
        msg = outputStr.format(
            str(endGhls), str(endBlues), "blues", str(endShards), str(endFusions), str(endGold), str(numberOfHones), str(int(total))
        )
    elif honingPiece == "weapon":
        ghls = data["t3"][honingPiece][str(targetLevel)]["ghl"]
        reds = data["t3"][honingPiece][str(targetLevel)]["red"]
        fusions = data["t3"][honingPiece][str(targetLevel)]["fusion"]
        gold = data["t3"][honingPiece][str(targetLevel)]["gold"]
        initialShards = data["t3"][honingPiece][str(targetLevel)]["initialShard"]
        shards = data["t3"][honingPiece][str(targetLevel)]["shard"]
        
        expectedGhls = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], ghls)
        expectedReds = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], reds)
        expectedFusions = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], fusions)
        expectedGold = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], gold)
        expectedShards = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], shards) + initialShards
        
        actualGhls = ghls*numberOfHones
        actualReds = reds*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        actualShards = shards*numberOfHones + initialShards
        
        endGhls = abs(int(expectedGhls - actualGhls))
        endReds = abs(int(expectedReds - actualReds))
        endFusions = abs(int(expectedFusions - actualFusions))
        endGold = abs(int(expectedGold - actualGold))
        endShards= abs(int(expectedShards - actualShards))
        endBlues = 0
        
        ghlValue = lookup_handler.get_item_data("ghl").json()[0]['avgPrice']
        redValue = lookup_handler.get_item_data("red").json()[0]['avgPrice'] / 10
        fusionValue = lookup_handler.get_item_data("fusion").json()[0]['avgPrice']
        
        total = endGhls*ghlValue + endReds*redValue + endFusions*fusionValue + endGold
        outputStr = winString if expectedGhls > actualGhls else lossString
        msg = outputStr.format(
            str(endGhls), str(endReds), "reds", str(endShards), str(endFusions), str(endGold), str(numberOfHones), str(int(total))
        )
    else:
        pass
    
    with Session() as sess:
        newHone = Honing(
            discordId=message.author.id,
            discordUsername=message.author.name,
            tierBaseItemLevel=1340,
            itemType=honingPiece,
            numberOfTaps=numberOfHones,
            outputLevel=targetLevel,
            goldUsedFromAvg=endGold if outputStr == winString else -endGold,
            shardsUsedFromAvg=endShards if outputStr == winString else -endShards,
            leapstonesUsedFromAvg=endGhls if outputStr == winString else -endGhls,
            blueStonesUsedFromAvg=endBlues if outputStr == winString else -endBlues,
            redStonesUsedFromAvg=endReds if outputStr == winString else -endReds,
            fusionsUsedFromAvg=endFusions if outputStr == winString else -endFusions,
        )
        sess.add(newHone)
        sess.commit()
    return msg

# Calculate how many hones to reach pity and then succeed
def calculate_max_attempts(totalBaseHoning, honingIncrement, maxHoningProbability) -> int:
    artisanEnergy = 0
    maxHoningAttempts = 1
    while (artisanEnergy < 2.15):
        if (min(totalBaseHoning+honingIncrement*(maxHoningAttempts-1), maxHoningProbability) > 1.0):
            break
        else:
            artisanEnergy+=min(totalBaseHoning+honingIncrement*(maxHoningAttempts-1), maxHoningProbability)
            maxHoningAttempts+=1
    return maxHoningAttempts

def calculate_attempts_from_artisans(artisansEnergy, targetLvl, gearType) -> int:
    totalBaseHoning = data["t3"][gearType][str(targetLvl)]["baseSuccess"] + data["t3"][gearType][str(targetLvl)]["strongHoldBuff"] + data["t3"][gearType][str(targetLvl)]["globalBuff"]
    honingIncrement = data["t3"][gearType][str(targetLvl)]["baseSuccess"]/10
    maxHoningProbability = data["t3"][gearType][str(targetLvl)]["baseSuccess"]*2
    attempts = 1
    base = 0
    while (base < artisansEnergy/100):
        base+=min(totalBaseHoning+honingIncrement*(attempts-1), maxHoningProbability)/2.15
        attempts+=1
    return attempts


#Calculate the expected number of material used, based on the input material
def calculate_expected_value_honing(honingValues: dict, materialUsedPerHone: int):
    baseHoning = honingValues["baseSuccess"]
    strongHoldBuff = honingValues["strongHoldBuff"]
    globalBuff = honingValues["globalBuff"]
    honingIncrement = baseHoning/10
    totalBaseHoning = baseHoning + strongHoldBuff + globalBuff
    maxHoningProbability = totalBaseHoning + baseHoning
    maxHoningAttempts = calculate_max_attempts(totalBaseHoning, honingIncrement, maxHoningProbability)
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