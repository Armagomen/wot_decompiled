# File: b (Python 2.7)

import logging
from typing import TYPE_CHECKING
from battle_pass_common import CurrencyBP
from constants import PREMIUM_ENTITLEMENTS
from gui import GUI_NATIONS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.bonus_model import BonusModel, BonusRarity, VehicleType
from gui.lootbox_system.base.awards_manager import AwardsManager
from gui.lootbox_system.base.common import LOOTBOX_RANDOM_NATIONAL_BLUEPRINT, LOOTBOX_RANDOM_NATIONAL_BROCHURE, LOOTBOX_RANDOM_NATIONAL_CREW_BOOK, LOOTBOX_RANDOM_NATIONAL_GUIDE, LOOTBOX_COMPENSATION_BONUS
from gui.lootbox_system.base.utils import getSingleVehicleCDForCustomization
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN
from gui.server_events.bonuses import BlueprintsBonusSubtypes, LootBoxRandomNationalBonus, PlusPremiumDaysBonus, VehiclesBonus, _BONUSES, LootBoxTokensBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName, getUnicName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BaseBonusUIPacker, BlueprintBonusUIPacker, BonusUIPacker, CrewBookBonusUIPacker, CrewSkinBonusUIPacker, GoodiesBonusUIPacker, ItemBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap, getLocalizedBonusName, CurrenciesBonusUIPacker
from gui.shared.money import Currency, Money
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union
    from frameworks.wulf import Array
    from gui.impl.wrappers.user_list_model import UserListModel
    from gui.server_events.bonuses import CustomizationsBonus, SimpleBonus, TokensBonus
    BonusModelsList = Union[(Array[BonusModel], UserListModel[BonusModel])]
_logger = logging.getLogger(__name__)
VEH_COMP_R_ID = R.views.lobby.awards.tooltips.RewardCompensationTooltip()
_LOOTBOX_BONUS_NAME = 'lootBox'

def getLootBoxesBonusPacker(eventName):
    mapping = getDefaultBonusPackersMap()
    simplePacker = LootBoxSimpleBonusUIPacker()
    blueprintPacker = LootBoxBlueprintBonusUIPacker()
    specialRandomPacker = LootBoxSpecialRandomBonusUIPacker()
    lootBoxPackersMap = {
        'battleToken': LootBoxTokenBonusUIPacker,
        'blueprints': blueprintPacker,
        'blueprintsAny': blueprintPacker,
        'crewBooks': LootBoxCrewBookBonusUIPacker(),
        'crewSkins': LootBoxCrewSkinBonusUIPacker(),
        'customizations': LootBoxCustomizationsBonusUIPacker,
        'currencies': LootBoxCurrenciesBonusUIPacker(),
        'finalBlueprints': blueprintPacker,
        'goodies': LootBoxGoodiesBonusUIPacker(),
        'items': LootBoxItemBonusUIPacker(),
        'slots': LootBoxSlotsBonusUIPacker(),
        'tmanToken': LootBoxTmanTemplateBonusUIPacker(),
        'tokens': LootBoxTokenBonusUIPacker,
        'vehicles': LootBoxVehiclesBonusUIPacker(),
        Currency.FREE_XP: simplePacker,
        Currency.CREDITS: simplePacker,
        Currency.GOLD: simplePacker,
        Currency.EQUIP_COIN: simplePacker,
        Currency.CRYSTAL: simplePacker,
        Currency.BPCOIN: LootBoxBPCoinBonusUIPacker(),
        PREMIUM_ENTITLEMENTS.PLUS: LootBoxPremiumBonusUIPacker(),
        LOOTBOX_RANDOM_NATIONAL_BLUEPRINT: specialRandomPacker,
        LOOTBOX_RANDOM_NATIONAL_BROCHURE: specialRandomPacker,
        LOOTBOX_RANDOM_NATIONAL_GUIDE: specialRandomPacker,
        LOOTBOX_RANDOM_NATIONAL_CREW_BOOK: specialRandomPacker,
        _LOOTBOX_BONUS_NAME: LootBoxesLootBoxBonusUIPacker(),
        LOOTBOX_COMPENSATION_BONUS: LootBoxCompensationPacker() }
    for packer in lootBoxPackersMap.itervalues():
        packer.init(eventName)
    
    mapping.update(lootBoxPackersMap)
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipData(bonuses, bonusModelsList, eventName, tooltipData = None, merge = False, packer = None, showLootboxCompensation = False):
    if packer is None:
        packer = getLootBoxesBonusPacker(eventName)
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    bonusesList = bonuses
    if merge:
        bonusesList = mergeNeededBonuses(bonuses, eventName)
    bonusesList = processCompensationsWithLootbox(bonusesList, eventName, showLootboxCompensation)
    bonusesCount = 0
    for bonus in bonusesList:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for (bonusIndex, item) in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.addViewModel(item)
                bonusesCount += _getBonusCount(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    if bonusTooltipList:
                        tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                    bonusIndexTotal += 1
                    continue
                continue
            return bonusesCount


def mergeNeededBonuses(bonuses, eventName):
    finalBonuses = []
    mergeBonusNames = ('blueprints', 'brochure', 'guide', 'crewBook')
    bonusesForMerge = lambda .0: pass# WARNING: Decompyle incomplete
(mergeBonusNames)
    usedNations = lambda .0: pass# WARNING: Decompyle incomplete
(mergeBonusNames)
    value = lambda .0: pass# WARNING: Decompyle incomplete
(mergeBonusNames)
    getValue = {
        'blueprints': lambda b: (b.getCount(), None),
        'brochure': lambda b: max(lambda .0: continue(b.getItems()))
,
        'guide': lambda b: max(lambda .0: continue(b.getItems()))
,
        'crewBook': lambda b: max(lambda .0: continue(b.getItems()))
 }
    getNation = {
        'blueprints': lambda b: pass# WARNING: Decompyle incomplete
,
        'brochure': lambda b: lambda .0: pass# WARNING: Decompyle incomplete
(b.getItems())
,
        'guide': lambda b: lambda .0: pass# WARNING: Decompyle incomplete
(b.getItems())
,
        'crewBook': lambda b: lambda .0: pass# WARNING: Decompyle incomplete
(b.getItems())
 }
    checkBonus = {
        'blueprints': lambda b: if b.getName() == 'blueprints':
passb.getBlueprintName() == BlueprintsBonusSubtypes.NATION_FRAGMENT,
        'brochure': lambda b: if b.getName() == 'crewBooks':
passany(lambda .0: continue(b.getItems()))
,
        'guide': lambda b: if b.getName() == 'crewBooks':
passany(lambda .0: continue(b.getItems()))
,
        'crewBook': lambda b: if b.getName() == 'crewBooks':
passany(lambda .0: continue(b.getItems()))
 }
    bonusName = {
        'blueprints': LOOTBOX_RANDOM_NATIONAL_BLUEPRINT,
        'brochure': LOOTBOX_RANDOM_NATIONAL_BROCHURE,
        'guide': LOOTBOX_RANDOM_NATIONAL_GUIDE,
        'crewBook': LOOTBOX_RANDOM_NATIONAL_CREW_BOOK }
    totalVehicleBonus = 0
    vehicleSlotBonuses = []
    vehicleNames = set()
    for bonus in bonuses:
        wasMergedBonus = False
        for name in mergeBonusNames:
            if checkBonus[name](bonus):
                bonusesForMerge[name].append(bonus)
                usedNations[name].update(getNation[name](bonus))
                value[name].append(getValue[name](bonus))
                wasMergedBonus = True
                break
                continue
        if wasMergedBonus or isinstance(bonus, VehiclesBonus):
            if bonus.formatValue() in vehicleNames:
                continue
            totalVehicleBonus += 1
            vehicleNames.add(bonus.formatValue())
        if bonus.getName() == 'slots' and bonus.getCount() == 1:
            vehicleSlotBonuses.append(bonus)
        else:
            finalBonuses.append(bonus)
    
    finalBonuses += vehicleSlotBonuses[totalVehicleBonus:]
    for name in mergeBonusNames:
        pass
    
    return AwardsManager.sortBonuses(eventName, finalBonuses, True)


def processCompensationsWithLootbox(bonuses, eventName, showLootboxCompensation):
    if not showLootboxCompensation:
        for bonus in bonuses:
            if bonus.getName() != LOOTBOX_COMPENSATION_BONUS:
                continue
                return [][bonus]
            finalBonuses = []
            boxCompensations = { }
            for bonus in bonuses:
                if bonus.getName() == LOOTBOX_COMPENSATION_BONUS:
                    category = bonus.getCategory()
                    boxCompensations.setdefault(category, 0)
                    boxCompensations[category] += (sum,)(lambda .0: for b in .0:
if b.getName() == LOOTBOX_COMPENSATION_BONUS and b.getCategory() == category:
b.getCount()continueNone(bonuses))
                    continue
            for bonus in bonuses:
                if bonus.getName() == _LOOTBOX_BONUS_NAME:
                    box = bonus.getBox()
                    if box is not None:
                        pass
                    category = ''
                    if category in boxCompensations:
                        categoryCompensation = boxCompensations[category]
                        if categoryCompensation:
                            boxCount = bonus.getCount()
                            newBoxCount = max(0, boxCount - categoryCompensation)
                            boxCompensations[category] = max(0, categoryCompensation - boxCount)
                            if newBoxCount:
                                tokenData = first(bonus.getTokens().itervalues())
                                if tokenData is not None:
                                    finalBonuses.append(LootBoxTokensBonus({
                                        tokenData.id: {
                                            'count': newBoxCount,
                                            'expires': {
                                                'at': tokenData.expires } } }, bonus.isCompensation(), { }))
                                
                                continue
                            
                        
                finalBonuses.append(bonus)
            
    return AwardsManager.sortBonuses(eventName, finalBonuses)


def _getBonusCount(bonusModel):
    bonusName = bonusModel.getName()
    if bonusName in Currency.ALL or bonusName in ('vehicles', Currency.FREE_XP, PREMIUM_ENTITLEMENTS.PLUS, CurrencyBP.TALER.value):
        return 1
    count = None.getCount()
    if not count:
        return 1
    return None(count)


def _getVehicleUIData(vehicle):
    return {
        'vehicleName': vehicle.shortUserName,
        'vehicleType': getIconResourceName(vehicle.type),
        'isElite': vehicle.isElite,
        'vehicleLvl': int2roman(vehicle.level),
        'vehicleLvlNum': vehicle.level }


def _getPreparedBonusModel(bonus, eventName):
    model = BonusModel()
    model.setName(bonus.getName())
    model.setIsCompensation(bonus.isCompensation())
    if not AwardsManager.getRarity(eventName, bonus):
        pass
    model.setRarity(BonusRarity.COMMON)
    return model


def _injectSpecialRewardName(item, postfix = ''):
    if item.getRarity() in (BonusRarity.RARE, BonusRarity.EPIC):
        if postfix:
            pass
        1(item.getName())


class LootBoxSimpleBonusUIPacker(SimpleBonusUIPacker):
    _LootBoxSimpleBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxSimpleBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxSimpleBonusUIPacker__eventName)
        model.setValue(str(bonus.getValue()))
        model.setIcon(bonus.getName())
        model.setLabel(label)
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getToolTip(cls, bonus):
        if bonus.getName() == Currency.GOLD and bonus.isCompensation():
            return [
                createTooltipData(makeTooltip(header = backport.text(R.strings.tooltips.awardItem.gold.header()), body = backport.text(R.strings.tooltips.awardItem.gold.body()), note = backport.text(R.strings.tooltips.awardItem.gold.compensation())))]
        return None(LootBoxSimpleBonusUIPacker, cls)._getToolTip(bonus)

    _getToolTip = classmethod(_getToolTip)


class LootBoxSpecialRandomBonusUIPacker(SimpleBonusUIPacker):
    _LootBoxSpecialRandomBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxSpecialRandomBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        label = backport.text(R.strings.tooltips.awardItem.dyn(bonus.getName()).header())
        if label:
            pass
        return [
            label(1, '')]

    _pack = classmethod(_pack)
    
    def _packSingleBonus(cls, bonus, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxSpecialRandomBonusUIPacker__eventName)
        model.setCount(bonus.getCount())
        model.setIcon(bonus.getIconName())
        model.setLabel(label)
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getContentId(cls, bonus):
        return [
            R.views.lobby.lootbox_system.tooltips.RandomNationalBonusTooltipView()]

    _getContentId = classmethod(_getContentId)
    
    def _getToolTip(cls, bonus):
        return [
            TooltipData(tooltip = None, isSpecial = True, specialAlias = None, specialArgs = [
                bonus.getName(),
                bonus.getValue(),
                bonus.getIconName()])]

    _getToolTip = classmethod(_getToolTip)


class LootBoxSlotsBonusUIPacker(SimpleBonusUIPacker):
    _LootBoxSlotsBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxSlotsBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxSlotsBonusUIPacker__eventName)
        model.setCount(bonus.getCount())
        model.setIcon(bonus.getName())
        model.setLabel(backport.text(R.strings.tooltips.awardItem.slots.header()))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)


class LootBoxTmanTemplateBonusUIPacker(SimpleBonusUIPacker):
    _LootBoxTmanTemplateBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxTmanTemplateBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        result = []
        for (tokenID, tokenRecord) in bonus.getTokens().iteritems():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                count = tokenRecord.count
                packed = cls._LootBoxTmanTemplateBonusUIPacker__packTmanTemplateToken(tokenID, bonus, count)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)
        return result

    _pack = classmethod(_pack)
    
    def __packTmanTemplateToken(cls, tokenID, bonus, count):
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return None
        model = None(bonus, cls._LootBoxTmanTemplateBonusUIPacker__eventName)
        model.setCount(count)
        model.setIcon(cls._LootBoxTmanTemplateBonusUIPacker__getBonusImageName(recruit))
        model.setLabel(recruit.getFullUserName())
        model.setValue(recruit.getGroupName())
        groupName = recruit.getGroupName()
        if groupName in ('men1', 'women1'):
            pass
        1(groupName)
        _injectSpecialRewardName(model, recruit.getGroupName())
        return model

    _LootBoxTmanTemplateBonusUIPacker__packTmanTemplateToken = classmethod(__packTmanTemplateToken)
    
    def __getBonusImageName(cls, recruitInfo):
        if recruitInfo.isFemale():
            pass
        baseName = 1('')
        return baseName

    _LootBoxTmanTemplateBonusUIPacker__getBonusImageName = classmethod(__getBonusImageName)
    
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip = None, isSpecial = True, specialAlias = TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs = [
                    tokenID]))
                continue
        return tooltipData

    _getToolTip = classmethod(_getToolTip)
    
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)
                continue
        return result

    _getContentId = classmethod(_getContentId)


class LootBoxCustomizationsBonusUIPacker(BaseBonusUIPacker):
    _LootBoxCustomizationsBonusUIPacker__eventName = ''
    _LootBoxCustomizationsBonusUIPacker__itemsCache = dependency.descriptor(IItemsCache)
    
    def init(cls, eventName):
        cls._LootBoxCustomizationsBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        result = []
        for (item, data) in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None or cls._LootBoxCustomizationsBonusUIPacker__isLockedStyle(bonus, item):
                continue
            result.append(cls._packSingleBonus(bonus, item, data))
        
        return result

    _pack = classmethod(_pack)
    
    def _packSingleBonus(cls, bonus, item, data):
        model = _getPreparedBonusModel(bonus, cls._LootBoxCustomizationsBonusUIPacker__eventName)
        custItem = bonus.getC11nItem(item)
        itemName = custItem.itemTypeName
        description = custItem.userType
        if itemName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT]:
            model.setName(itemName)
            model.setIcon(custItem.name)
            model.setOverlayType(custItem.rarity)
        elif itemName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE]:
            description = backport.text(R.strings.lootbox_system.bonuses.description.style())
            vehicleCD = getSingleVehicleCDForCustomization(custItem)
            if vehicleCD is not None:
                pass
            model.setIsInHangar(custItem.fullInventoryCount() > 0)
            if custItem.is3D:
                itemName = 'style_3d'
                description = backport.text(R.strings.lootbox_system.bonuses.description.style3D())
                if vehicleCD is not None:
                    pass
                vehicle = None
                if vehicle is not None:
                    model.setIsElite(vehicle.isElite)
                    model.setLevel(vehicle.level)
                    model.setType(VehicleType(vehicle.type))
                    model.setVehicle3DStyleName(vehicle.userName)
                
            
        model.setIcon(itemName)
        model.setId(custItem.id)
        model.setCount(item.get('value', 0))
        model.setLabel(cls._getLabel(custItem))
        model.setDescription(description)
        _injectSpecialRewardName(model, str(custItem.id))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getToolTip(cls, bonus):
        tooltipData = []
        for (item, _) in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None:
                continue
            itemCustomization = bonus.getC11nItem(item)
            specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD
            specialArgs = CustomizationTooltipContext(itemCD = itemCustomization.intCD)
            if itemCustomization.itemTypeName in ('camouflage', 'style'):
                vehicle = getSingleVehicleCDForCustomization(itemCustomization)
                if vehicle is not None:
                    specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM
                    specialArgs = CustomizationTooltipContext(itemCD = itemCustomization.intCD, vehicleIntCD = vehicle)
                
            tooltipData.append(TooltipData(tooltip = None, isSpecial = True, specialAlias = specialAlias, specialArgs = specialArgs))
        
        return tooltipData

    _getToolTip = classmethod(_getToolTip)
    
    def _getContentId(cls, bonus):
        result = []
        for (item, _) in zip(bonus.getCustomizations(), bonus.getList()):
            if item is not None:
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)
                continue
        return result

    _getContentId = classmethod(_getContentId)
    
    def _getLabel(cls, customizationItem):
        return customizationItem.userName

    _getLabel = classmethod(_getLabel)
    
    def __isLockedStyle(cls, bonus, item):
        customizationItem = bonus.getC11nItem(item)
        if customizationItem.itemTypeName == 'style':
            pass
        return customizationItem.isLockedOnVehicle

    _LootBoxCustomizationsBonusUIPacker__isLockedStyle = classmethod(__isLockedStyle)


class LootBoxGoodiesBonusUIPacker(GoodiesBonusUIPacker):
    _LootBoxGoodiesBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxGoodiesBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        return cls._packIconBonusModel(bonus, booster.getFullNameForResource(), count, backport.text(R.strings.menu.booster.label.dyn(booster.boosterGuiType)(), effectValue = booster.getFormattedValue()), description = backport.text(R.strings.lootbox_system.bonuses.description.booster()))

    _packSingleBoosterBonus = classmethod(_packSingleBoosterBonus)
    
    def _packIconBonusModel(cls, bonus, icon, count, label, description = ''):
        model = _getPreparedBonusModel(bonus, cls._LootBoxGoodiesBonusUIPacker__eventName)
        model.setCount(count)
        model.setIcon(icon)
        model.setLabel(label)
        model.setDescription(description)
        return model

    _packIconBonusModel = classmethod(_packIconBonusModel)


class LootBoxBlueprintBonusUIPacker(BlueprintBonusUIPacker):
    _LootBoxBlueprintBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxBlueprintBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        model = _getPreparedBonusModel(bonus, cls._LootBoxBlueprintBonusUIPacker__eventName)
        label = bonus.getBlueprintTooltipName()
        blueprintName = bonus.getBlueprintName()
        if blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            label = backport.text(R.strings.lootbox_system.bonuses.label.blueprints.nationalFragment(), nation = backport.text(R.strings.blueprints.nations.dyn(bonus.getImageCategory())()))
        elif blueprintName == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
            label = backport.text(R.strings.lootbox_system.bonuses.label.blueprints.universalFragment())
        model.setIcon(bonus.getImageCategory())
        model.setLabel(label)
        model.setCount(bonus.getCount())
        return [
            model]

    _pack = classmethod(_pack)
    
    def getTooltip(bonuses):
        continue
        fragmentCDs = [ bonus.getBlueprintSpecialArgs() for bonus in bonuses ]
        continue
        specialAlias = [ bonus.getBlueprintSpecialAlias() for bonus in bonuses ]
        return TooltipData(tooltip = None, isSpecial = True, specialAlias = specialAlias, specialArgs = [
            fragmentCDs])

    getTooltip = staticmethod(getTooltip)


class LootBoxItemBonusUIPacker(ItemBonusUIPacker):
    _LootBoxItemBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxItemBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, item, count):
        model = _getPreparedBonusModel(bonus, cls._LootBoxItemBonusUIPacker__eventName)
        model.setCount(count)
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            pass
        (icon, overlay) = (item.getGUIEmblemID(), item.getOverlayType())
        model.setIcon(icon)
        model.setOverlayType(overlay)
        model.setLabel(item.userName)
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            model.setDescription(backport.text(R.strings.lootbox_system.bonuses.description.battle_booster()))
        elif item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isRegular:
            model.setDescription(backport.text(R.strings.lootbox_system.bonuses.description.standard_equipment()))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)


class LootBoxCrewBookBonusUIPacker(CrewBookBonusUIPacker):
    _LootBoxCrewBookBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxCrewBookBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, book, count):
        model = _getPreparedBonusModel(bonus, cls._LootBoxCrewBookBonusUIPacker__eventName)
        model.setCount(count)
        model.setLabel(book.userName)
        model.setIcon(book.getBonusIconName())
        return model

    _packSingleBonus = classmethod(_packSingleBonus)


class LootBoxCrewSkinBonusUIPacker(CrewSkinBonusUIPacker):
    _LootBoxCrewSkinBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxCrewSkinBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, crewSkin, count, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxCrewSkinBonusUIPacker__eventName)
        model.setCount(count)
        model.setIcon(str(crewSkin.itemTypeName + str(crewSkin.getRarity())))
        model.setLabel(label)
        model.setDescription(backport.text(R.strings.lootbox_system.bonuses.description.crewSkin()))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)


class LootBoxesLootBoxBonusUIPacker(SimpleBonusUIPacker):
    _LootBoxesLootBoxBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxesLootBoxBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        return [
            cls._packSingleBonus(bonus)]

    _pack = classmethod(_pack)
    
    def _packSingleBonus(cls, bonus):
        model = _getPreparedBonusModel(bonus, cls._LootBoxesLootBoxBonusUIPacker__eventName)
        box = bonus.getBox()
        model.setId(bonus.lootBoxID)
        if box:
            pass
        1(bonus.getName())
        model.setCount(bonus.getCount())
        if box:
            pass
        1('')
        _injectSpecialRewardName(model, str(bonus.lootBoxID))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getContentId(cls, _):
        return [
            R.views.lobby.lootbox_system.tooltips.BoxTooltip()]

    _getContentId = classmethod(_getContentId)


class LootBoxTokenBonusUIPacker(TokenBonusUIPacker):
    _LootBoxTokenBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxTokenBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packToken(cls, bonusPacker, bonus, *args):
        model = _getPreparedBonusModel(bonus, cls._LootBoxTokenBonusUIPacker__eventName)
        return bonusPacker(model, bonus, *args)

    _packToken = classmethod(_packToken)
    
    def _getTokenBonusPackers(cls):
        return {
            BATTLE_BONUS_X5_TOKEN: cls._LootBoxTokenBonusUIPacker__packBattleBonusX5Token,
            CREW_BONUS_X3_TOKEN: cls._LootBoxTokenBonusUIPacker__packCrewBonusX3Token }

    _getTokenBonusPackers = classmethod(_getTokenBonusPackers)
    
    def _getTooltipsPackers(cls):
        packers = super(LootBoxTokenBonusUIPacker, cls)._getTooltipsPackers()
        return {
            BATTLE_BONUS_X5_TOKEN: packers[BATTLE_BONUS_X5_TOKEN],
            CREW_BONUS_X3_TOKEN: packers[CREW_BONUS_X3_TOKEN] }

    _getTooltipsPackers = classmethod(_getTooltipsPackers)
    
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setCount(bonus.getCount())
        model.setLabel(backport.text(R.strings.tooltips.quests.bonuses.token.battle_bonus_x5.label()))
        model.setIcon(BATTLE_BONUS_X5_TOKEN)
        return model

    _LootBoxTokenBonusUIPacker__packBattleBonusX5Token = classmethod(__packBattleBonusX5Token)
    
    def __packCrewBonusX3Token(cls, model, bonus, *args):
        model.setCount(bonus.getCount())
        model.setLabel(backport.text(R.strings.tooltips.quests.bonuses.token.crew_bonus_x3.label()))
        model.setIcon(CREW_BONUS_X3_TOKEN)
        return model

    _LootBoxTokenBonusUIPacker__packCrewBonusX3Token = classmethod(__packCrewBonusX3Token)


class LootBoxPremiumBonusUIPacker(BaseBonusUIPacker):
    _LootBoxPremiumBonusUIPacker__eventName = ''
    _ICONS_AVAILABLE = (1, 2, 3, 7, 14, 30, 90, 180, 360)
    
    def init(cls, eventName):
        cls._LootBoxPremiumBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        return [
            cls._packSingleBonus(bonus)]

    _pack = classmethod(_pack)
    
    def _packSingleBonus(cls, bonus):
        model = _getPreparedBonusModel(bonus, cls._LootBoxPremiumBonusUIPacker__eventName)
        icon = 'premium_plus_universal'
        days = bonus.getValue()
        if days in cls._ICONS_AVAILABLE:
            icon = '{}_{}'.format(bonus.getName(), str(days))
        model.setName(bonus.getName())
        model.setIcon(icon)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(days))
        model.setLabel(backport.text(R.strings.tooltips.awardItem.premium_plus.header()))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)


class LootBoxVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    _LootBoxVehiclesBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxVehiclesBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packVehicles(cls, bonus, vehicles):
        continue
        return [ cls._packVehicle(bonus, vehInfo, vehicle) for (vehicle, vehInfo) in vehicles ]

    _packVehicles = classmethod(_packVehicles)
    
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = _getPreparedBonusModel(bonus, cls._LootBoxVehiclesBonusUIPacker__eventName)
        styleID = vehInfo.get('customization', { }).get('styleId')
        if styleID is not None and vehicle.isOutfitLocked:
            model.setStyleID(styleID)
        model.setName(bonus.getName())
        model.setIsRent(isRent)
        compensation = cls._LootBoxVehiclesBonusUIPacker__getCompensation(bonus, vehInfo)
        model.setIsCompensation(bool(compensation))
        if compensation:
            for bonusComp in compensation:
                model.compensation.setName(bonusComp.getName())
                model.compensation.setValue(str(bonusComp.getValue()))
                model.compensation.setIcon(bonusComp.getName())
                model.compensation.setLabel(getLocalizedBonusName(bonusComp.getName()))
            
        cls._LootBoxVehiclesBonusUIPacker__fillVehicleInfo(model, vehicle)
        _injectSpecialRewardName(model, str(vehicle.intCD))
        return model

    _packVehicleBonusModel = classmethod(_packVehicleBonusModel)
    
    def __fillVehicleInfo(cls, model, vehicle):
        model.setIsInHangar(vehicle.isInInventory)
        model.setId(vehicle.intCD)
        model.setLabel(vehicle.userName)
        model.setVehicleShortName(vehicle.shortUserName)
        model.setType(VehicleType(vehicle.type))
        model.setLevel(vehicle.level)
        model.setIsElite(vehicle.isElite)
        model.setIcon(getUnicName(vehicle.name))

    _LootBoxVehiclesBonusUIPacker__fillVehicleInfo = classmethod(__fillVehicleInfo)
    
    def _packTooltips(cls, bonus, vehicles):
        packedTooltips = []
        for (vehicle, vehInfo) in vehicles:
            compensation = cls._LootBoxVehiclesBonusUIPacker__getCompensation(bonus, vehInfo)
            if compensation:
                for bonusComp in compensation:
                    packedTooltips.extend(cls._packCompensationTooltip(bonusComp, vehicle))
                
            packedTooltips.append(cls._packTooltip(bonus, vehicle, vehInfo))
        
        return packedTooltips

    _packTooltips = classmethod(_packTooltips)
    
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        compensation = cls._LootBoxVehiclesBonusUIPacker__getCompensation(bonus, vehInfo)
        if compensation:
            return first(cls._packCompensationTooltip(first(compensation), vehicle))
        return None(LootBoxVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)

    _packTooltip = classmethod(_packTooltip)
    
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(LootBoxVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        continue
        return [ cls._LootBoxVehiclesBonusUIPacker__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    _packCompensationTooltip = classmethod(_packCompensationTooltip)
    
    def _getContentId(cls, bonus):
        outcome = []
        for (_, vehInfo) in bonus.getVehicles():
            compensation = cls._LootBoxVehiclesBonusUIPacker__getCompensation(bonus, vehInfo)
            if compensation:
                outcome.append(VEH_COMP_R_ID)
                continue
            outcome.append(BACKPORT_TOOLTIP_CONTENT_ID)
        
        return outcome

    _getContentId = classmethod(_getContentId)
    
    def __convertCompensationTooltip(cls, bonusComp, vehicle, tooltipData):
        iconAfterRes = R.images.gui.maps.icons.quests.bonuses.big.dyn(bonusComp.getName())
        if not iconAfterRes.exists():
            iconAfterRes = R.images.gui.maps.icons.quests.bonuses.big.gold
        specialArgs = {
            'labelBefore': '',
            'iconAfter': backport.image(iconAfterRes()),
            'labelAfter': bonusComp.getIconLabel(),
            'bonusName': bonusComp.getName() }
        uiData = _getVehicleUIData(vehicle)
        formattedTypeName = uiData['vehicleType']
        isElite = vehicle.isElite
        if isElite:
            pass
        uiData['vehicleType'] = formattedTypeName
        specialArgs.update(uiData)
        vehicleName = getNationLessName(vehicle.name)
        vehIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(vehicleName)()
        if vehIcon < 1:
            vehicleName = vehicleName.replace('-', '_')
            vehIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(vehicleName)()
        if vehIcon > 0:
            pass
        specialArgs['iconBefore'] = ''
        return createTooltipData(tooltip = tooltipData.tooltip, specialAlias = VEH_COMP_R_ID, specialArgs = specialArgs)

    _LootBoxVehiclesBonusUIPacker__convertCompensationTooltip = classmethod(__convertCompensationTooltip)
    
    def __getCompensation(cls, bonus, vehInfo):
        compBonuses = []
        compensatedNumber = vehInfo.get('compensatedNumber', 0)
        compensation = vehInfo.get('customCompensation')
        if compensatedNumber and compensation is not None:
            money = Money(*compensation)
            for (currency, value) in money.iteritems():
                if value:
                    bonusClass = _BONUSES.get(currency)
                    compBonuses.append(bonusClass(currency, value, isCompensation = True, compensationReason = bonus))
                    continue
        return compBonuses

    _LootBoxVehiclesBonusUIPacker__getCompensation = classmethod(__getCompensation)


class LootBoxCurrenciesBonusUIPacker(CurrenciesBonusUIPacker):
    _LootBoxCurrenciesBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxCurrenciesBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxCurrenciesBonusUIPacker__eventName)
        model.setName(bonus.getCode())
        model.setValue(str(bonus.getValue()))
        model.setIcon(bonus.getCode())
        model.setLabel(label)
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getContentId(cls, bonus):
        if bonus.getCode() == CurrencyBP.TALER.value:
            return [
                R.views.lobby.battle_pass.tooltips.BattlePassTalerTooltip()]
        return None(LootBoxCurrenciesBonusUIPacker, cls)._getContentId(bonus)

    _getContentId = classmethod(_getContentId)


class LootBoxBPCoinBonusUIPacker(SimpleBonusUIPacker):
    _LootBoxBPCoinBonusUIPacker__eventName = ''
    
    def init(cls, eventName):
        cls._LootBoxBPCoinBonusUIPacker__eventName = eventName

    init = classmethod(init)
    
    def _packSingleBonus(cls, bonus, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxBPCoinBonusUIPacker__eventName)
        model.setValue(str(bonus.getValue()))
        model.setIcon(bonus.getName())
        model.setLabel(backport.text(R.strings.lootbox_system.bonuses.label.bpcoin()))
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getContentId(cls, bonus):
        return [
            R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView()]

    _getContentId = classmethod(_getContentId)


class LootBoxCompensationPacker(SimpleBonusUIPacker):
    _LootBoxCompensationPacker__eventName = ''
    _LootBoxCompensationPacker__VEHICLE_BONUS_NAME = 'vehicles'
    
    def init(cls, eventName):
        cls._LootBoxCompensationPacker__eventName = eventName

    init = classmethod(init)
    
    def _pack(cls, bonus):
        return [
            cls._packSingleBonus(bonus, label = '')]

    _pack = classmethod(_pack)
    
    def _packSingleBonus(cls, bonus, label):
        model = _getPreparedBonusModel(bonus, cls._LootBoxCompensationPacker__eventName)
        model.setIcon(cls._LootBoxCompensationPacker__VEHICLE_BONUS_NAME)
        model.setLabel('')
        model.compensation.setName(_LOOTBOX_BONUS_NAME)
        box = bonus.getBox()
        if box is not None:
            pass
        1('')
        if box is not None:
            pass
        1('')
        return model

    _packSingleBonus = classmethod(_packSingleBonus)
    
    def _getContentId(cls, bonus):
        return [
            R.views.lobby.lootbox_system.tooltips.BoxCompensationTooltip()]

    _getContentId = classmethod(_getContentId)
    
    def _getToolTip(cls, bonus):
        return [
            TooltipData(tooltip = None, isSpecial = True, specialAlias = None, specialArgs = [
                bonus.getCategory(),
                cls._LootBoxCompensationPacker__eventName])]

    _getToolTip = classmethod(_getToolTip)

