from util.honing.honing_strategies import *
from util.constants import GEAR_TIER, GEAR_TYPE
from db_connection import Session
from models.honing import Honing
from sqlalchemy import desc
from util.lookup import lookup_handler

class HoningDataManipulator:
    
    def __init__(self):
        self.honing_strategy = None
        self.lookup_handler = lookup_handler
        
    def set_honing_strategy(self, gearTier: GEAR_TIER, gearType: GEAR_TYPE):
        if gearTier.name == "brel" and gearType.name == "weapon":
            self.honing_strategy = BrelWeaponHoningStrategy()
        elif gearTier.name == "brel" and gearType.name == "armor":
            self.honing_strategy = BrelArmorHoningStrategy()
        elif gearTier.name == "argos" and gearType.name == "weapon":
            self.honing_strategy = ArgosWeaponHoningStrategy()
        elif gearTier.name == "argos" and gearType.name == "armor":
            self.honing_strategy = ArgosArmorHoningStrategy()
        else:
            pass
        
    def commit_honing_to_db(self, message, targetLevel: str, numberOfHones: int, gearTier: GEAR_TIER, gearType: GEAR_TYPE):
        self.set_honing_strategy(gearTier, gearType)
        material_deviation_values = self.honing_strategy.calculate_honing_materials_used(targetLevel, numberOfHones)
        
        with Session() as sess:
            newHone = Honing(
                discordId=message.author.id,
                discordUsername=message.author.name,
                tierBaseItemLevel=1340 if gearTier == GEAR_TIER.argos.name else 1390,
                itemType=gearType.name,
                numberOfTaps=numberOfHones,
                outputLevel=targetLevel,
                goldUsedFromAvg=material_deviation_values["gold"],
                shardsUsedFromAvg=material_deviation_values["shards"],
                leapstonesUsedFromAvg=material_deviation_values["leaps"],
                blueStonesUsedFromAvg=material_deviation_values["blues"],
                redStonesUsedFromAvg=material_deviation_values["reds"],
                fusionsUsedFromAvg=material_deviation_values["fusions"],
            )
            sess.add(newHone)
            sess.commit()
        return material_deviation_values
        
    def delete_last_hone(self, id):
        with Session() as sess:
            lastHone = sess.query(Honing).filter(Honing.discordId == str(id)).order_by(desc(Honing.id)).first()
            targetLevel, numTaps, gearType = lastHone.outputLevel, lastHone.numberOfTaps, lastHone.itemType
            sess.delete(lastHone)
            sess.commit()
        return targetLevel, numTaps, gearType
    
    def calculate_honing_historic(self, message):
        with Session() as sess:
            honings = reversed(sess.query(Honing).filter(Honing.discordId == str(message.author.id)).order_by(desc(Honing.id), Honing.numberOfTaps).all())

        count = 0
        total = 0
        ordered_honings = {}

        argosBlueValue = self.lookup_handler.get_item_data("blue", "argos").json()[0]['avgPrice'] / 10
        argosRedValue = self.lookup_handler.get_item_data("red", "argos").json()[0]['avgPrice'] / 10
        ghlValue = self.lookup_handler.get_item_data("leapstone", "argos").json()[0]['avgPrice']
        argosFusionValue = self.lookup_handler.get_item_data("fusion", "argos").json()[0]['avgPrice']
        brelBlueValue = self.lookup_handler.get_item_data("blue", "brel").json()[0]['avgPrice'] / 10
        brelRedValue = self.lookup_handler.get_item_data("red", "brel").json()[0]['avgPrice'] / 10
        mhlValue = self.lookup_handler.get_item_data("leapstone", "brel").json()[0]['avgPrice']
        brelFusionValue = self.lookup_handler.get_item_data("fusion", "brel").json()[0]['avgPrice']
        
        for honing in honings:
            if honing.tierBaseItemLevel == 1340:
                subtotal = int(honing.leapstonesUsedFromAvg * ghlValue 
                               + honing.blueStonesUsedFromAvg * argosBlueValue
                               + honing.redStonesUsedFromAvg * argosRedValue
                               + honing.fusionsUsedFromAvg * argosFusionValue
                               + honing.goldUsedFromAvg
                               )
            elif honing.tierBaseItemLevel == 1390:
                subtotal = int(honing.leapstonesUsedFromAvg * mhlValue 
                               + honing.blueStonesUsedFromAvg * brelBlueValue
                               + honing.redStonesUsedFromAvg * brelRedValue
                               + honing.fusionsUsedFromAvg * brelFusionValue
                               + honing.goldUsedFromAvg
                               )
            else:
                raise Exception("Invalid tier of gear with base ilvl {}".format(honing.tierBaseItemLevel))
            total+=subtotal
            ordered_honings[count] = [subtotal, total]
            count+=1
        return ordered_honings
            
    