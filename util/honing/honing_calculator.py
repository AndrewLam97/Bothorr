import json
import os
import math
from util.lookup import lookup_handler


absolute_path = os.path.dirname(__file__)
file_path = os.path.join(absolute_path, "honing_values.json")
f = open(file_path)
data = json.load(f)

#Calculate honing value wins
#TODO: Use this for honing Ls too
def calculate_honing_win(targetLevel: int, numberOfHones: int, honingPiece: str):
    if honingPiece == "armor":
        ghls = data["t3"][honingPiece][str(targetLevel)]["ghl"]
        blues = data["t3"][honingPiece][str(targetLevel)]["blue"]
        fusions = data["t3"][honingPiece][str(targetLevel)]["fusion"]
        gold = data["t3"][honingPiece][str(targetLevel)]["gold"]
        
        expectedGhls = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], ghls)
        expectedBlues = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], blues)
        expectedFusions = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], fusions)
        expectedGold = calculate_expected_value_honing(data["t3"][honingPiece][str(targetLevel)], gold)
        
        actualGhls = ghls*numberOfHones
        actualBlues = blues*numberOfHones
        actualFusions = fusions*numberOfHones
        actualGold = gold*numberOfHones
        
        savedGhls = int(expectedGhls - actualGhls)
        savedBlues = int(expectedBlues - actualBlues)
        savedFusions = int(expectedFusions - actualFusions)
        savedGold = int(expectedGold - actualGold)
        
        ghlValue = lookup_handler.get_item_data("ghl").json()[0]['avgPrice']
        blueValue = lookup_handler.get_item_data("blue").json()[0]['avgPrice']
        fusionValue = lookup_handler.get_item_data("fusion").json()[0]['avgPrice']
        
        totalSaved = savedGhls*ghlValue + savedBlues*blueValue + savedFusions*fusionValue + savedGold
        msg = "You saved {} GHLs, {} blues, {} fusions, and {} raw gold by {} tapping compared to the average scenario. With current market values, you saved a grand total of {} gold".format(
            str(savedGhls), str(savedBlues), str(savedFusions), str(savedGold), str(numberOfHones), str(int(totalSaved))
        )
        return msg
    else:
        pass

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