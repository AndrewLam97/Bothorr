WEAPON_CONSTANT = "weapon"
class WeaponHoningCalculator:
    def __init__(self):
        pass
    
    def calculate(self, targetLevel: int, numberOfHones: int, honingTier: str, data: object, calculate_expected_value_honing) -> dict:
        weaponTierIlvl = "1340" if honingTier == "argos" else "1390"
        weaponHoningData = data["t3"][weaponTierIlvl][WEAPON_CONSTANT]
        leaps = weaponHoningData[str(targetLevel)]["leapstone"]
        reds = weaponHoningData[str(targetLevel)]["red"]
        fusions = weaponHoningData[str(targetLevel)]["fusion"]
        gold = weaponHoningData[str(targetLevel)]["gold"]
        shards = weaponHoningData[str(targetLevel)]["shard"]
        initialShards = weaponHoningData[str(targetLevel)]["initialShard"]
        
        expectedLeaps = calculate_expected_value_honing(weaponHoningData[str(targetLevel)], leaps)
        expectedReds = calculate_expected_value_honing(weaponHoningData[str(targetLevel)], reds)
        expectedFusions = calculate_expected_value_honing(weaponHoningData[str(targetLevel)], fusions)
        expectedGold = calculate_expected_value_honing(weaponHoningData[str(targetLevel)], gold)
        expectedShards = calculate_expected_value_honing(weaponHoningData[str(targetLevel)], shards) + initialShards
        
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