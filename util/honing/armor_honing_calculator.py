ARMOR_CONSTANT = "armor"

class ArmorHoningCalculator:
    def __init__(self):
        pass
    
    def calculate(self, targetLevel: int, numberOfHones: int, honingTier: str, data: object, calculate_expected_value_honing) -> dict:
        armorTierIlvl = "1340" if honingTier == "argos" else "1390"
        armorHoningData = data["t3"][armorTierIlvl][ARMOR_CONSTANT]
        leaps = armorHoningData[str(targetLevel)]["leapstone"]
        blues = armorHoningData[str(targetLevel)]["blue"]
        fusions = armorHoningData[str(targetLevel)]["fusion"]
        gold = armorHoningData[str(targetLevel)]["gold"]
        shards = armorHoningData[str(targetLevel)]["shard"]
        initialShards = armorHoningData[str(targetLevel)]["initialShard"]
        
        expectedLeaps = calculate_expected_value_honing(armorHoningData[str(targetLevel)], leaps)
        expectedBlues = calculate_expected_value_honing(armorHoningData[str(targetLevel)], blues)
        expectedFusions = calculate_expected_value_honing(armorHoningData[str(targetLevel)], fusions)
        expectedGold = calculate_expected_value_honing(armorHoningData[str(targetLevel)], gold)
        expectedShards = calculate_expected_value_honing(armorHoningData[str(targetLevel)], shards) + initialShards
        
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