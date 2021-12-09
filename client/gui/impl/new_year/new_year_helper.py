# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_helper.py
import random
from constants import SECONDS_IN_DAY, LOOTBOX_TOKEN_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.tooltips.ny_discount_reward_tooltip import NyDiscountRewardTooltip
from helpers import dependency, time_utils, getLanguageCode, int2roman
from items import new_year
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.ny_constants import CurrentNYConstants
from shared_utils import first, inPercents
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import INewYearController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from gui.shared.gui_items.loot_box import NewYearLootBoxes
_ARABIC_NUMBERS_LANGUAGE_CODES = ('ko', 'no')
IS_ROMAN_NUMBERS_ALLOWED = getLanguageCode() not in _ARABIC_NUMBERS_LANGUAGE_CODES
BONUS_ICONS = {'xpFactor': R.images.gui.maps.icons.newYear.vehicles.icons.icon_battle_exp_main(),
 'freeXPFactor': R.images.gui.maps.icons.newYear.vehicles.icons.icon_free_exp_main_screen(),
 'tankmenXPFactor': R.images.gui.maps.icons.newYear.vehicles.icons.icon_crew_exp_main()}
_BONUSES_ORDER = ({'bonusName': 'tmanToken'},
 {'bonusName': CurrentNYConstants.FILLERS},
 {'bonusName': 'battleToken',
  'tagStartsWith': LOOTBOX_TOKEN_PREFIX},
 {'bonusName': 'entitlements'},
 {'bonusName': 'crewBooks',
  'tag': CREW_BOOK_RARITY.PERSONAL},
 {'bonusName': 'dossier',
  'tag': 'isPrefixBadge'},
 {'bonusName': 'customizations',
  'tag': 'style'},
 {'bonusName': 'customizations'},
 {'bonusName': 'dossier'},
 {'bonusName': 'vehicles'},
 {'bonusName': 'slots'},
 {'bonusNameStartsWith': 'BlueprintNation'},
 {'bonusNameStartsWith': 'Blueprint'},
 {'bonusName': 'goodies'},
 {'bonusName': CurrentNYConstants.TOY_FRAGMENTS},
 {'bonusName': 'crewBooks'})
_BONUSES_ORDER_GF = (CurrentNYConstants.FILLERS,
 'tmanToken',
 'newYearSlot',
 'newYearAlbumsAccess',
 'lootBox',
 'entitlements',
 'vehicles',
 'slots',
 CurrentNYConstants.TOY_FRAGMENTS,
 CREW_BOOK_RARITY.PERSONAL,
 'customizations_style',
 'customizations',
 'dossier',
 'BlueprintNationFragmentCongrats',
 'BlueprintUniversalFragmentCongrats',
 'goodies',
 'crewBooks')

def __getAdditionalNameBattleToken(bonus):
    return 'lootBox' if any((t.startswith(LOOTBOX_TOKEN_PREFIX) for t in bonus.getTokens())) else bonus.getName()


def __getAdditionalNameCustomizations(bonus):
    return 'customizations_style' if bonus.getC11nItem(first(bonus.getCustomizations())).itemTypeName == 'style' else bonus.getName()


def __getAdditionalNameCrewBooks(bonus):
    return CREW_BOOK_RARITY.PERSONAL if first(bonus.getItems())[0].getBookType() == CREW_BOOK_RARITY.PERSONAL else bonus.getName()


ADDITIONAL_BONUS_NAME_GETTERS = {'battleToken': __getAdditionalNameBattleToken,
 'blueprints': lambda b: b.getBlueprintName(),
 'customizations': __getAdditionalNameCustomizations,
 'crewBooks': __getAdditionalNameCrewBooks}
_BONUSES_ORDER_CACHE = {}

@dependency.replace_none_kwargs(nyController=INewYearController)
def fillBonusFormula(formulaViewModel, nyController=None):
    with formulaViewModel.transaction() as tx:
        tx.setCreditsBonus(inPercents(nyController.getActiveSettingBonusValue()))
        tx.setMultiplier(nyController.getActiveMultiplier())
        tx.setMegaBonus(inPercents(nyController.getActiveMegaToysBonus()))
        tx.setCollectionBonus(inPercents(nyController.getActiveCollectionsBonus()))


def nyBonusSortOrder(preformattedBonus):
    bonusName, tags = preformattedBonus.bonusName, preformattedBonus.postProcessTags
    if isinstance(tags, tuple):
        tags = '' if not tags else tags[0]
    primaryKey = (bonusName, tags)
    if primaryKey in _BONUSES_ORDER_CACHE:
        return _BONUSES_ORDER_CACHE[primaryKey]
    result = len(_BONUSES_ORDER)
    for index, criteria in enumerate(_BONUSES_ORDER):
        if 'bonusName' in criteria and bonusName != criteria['bonusName']:
            continue
        if 'bonusNameStartsWith' in criteria and not bonusName.startswith(criteria['bonusNameStartsWith']):
            continue
        if 'tag' in criteria and criteria['tag'] not in tags:
            continue
        if 'tagStartsWith' in criteria and not tags.startswith(criteria['tagStartsWith']):
            continue
        result = index
        break

    _BONUSES_ORDER_CACHE[primaryKey] = result
    return result


def nyBonusGFSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return _BONUSES_ORDER_GF.index(bonusName) if bonusName in _BONUSES_ORDER_GF else len(_BONUSES_ORDER_GF)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getNYLootboxCount(itemsCache=None, lobbyContext=None):
    totalCount = 0
    if lobbyContext.getServerSettings().isLootBoxesEnabled():
        itemsByType = itemsCache.items.tokens.getLootBoxesCountByType()
        totalCount = 0
        for boxType in (NewYearLootBoxes.COMMON, NewYearLootBoxes.PREMIUM):
            categories = itemsByType.get(boxType, {})
            totalCount += categories.get(TOTAL_KEY, 0)

    return totalCount


def nyCreateToolTipContentDecorator(func):

    def wrapper(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyDiscountRewardTooltip():
            variadicID, discount = event.getArgument('variadicID'), event.getArgument('discount')
            return NyDiscountRewardTooltip(variadicID, discount)
        if contentID == R.views.lobby.new_year.tooltips.ny_tank_extra_slot_tooltip.NYTankExtraSlotTooltipContent():
            from gui.impl.new_year.tooltips.ny_tank_extra_slot_tooltip import NYTankExtraSlotTooltipContent
            return NYTankExtraSlotTooltipContent()
        return func(self, event, contentID)

    return wrapper


def backportTooltipDecorator(tooltipItemsName='_tooltips'):

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = _getTooltipDataByEvent(event, getattr(self, tooltipItemsName, {}))
                if tooltipData is None:
                    return
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def _getTooltipDataByEvent(event, tooltipItems):
    tooltipId = event.getArgument('tooltipId')
    return None if tooltipId is None else tooltipItems.get(tooltipId, None)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getNextGameTime(lobbyContext=None):
    gameDayStartingTime = lobbyContext.getServerSettings().regionals.getGameDayStartingTime()
    currentTime = time_utils.getCurrentTimestamp()
    newGameDayStartTime = (int((currentTime - gameDayStartingTime) // SECONDS_IN_DAY) + 1) * SECONDS_IN_DAY
    return newGameDayStartTime + gameDayStartingTime


def formatRomanNumber(number):
    return int2roman(number) if IS_ROMAN_NUMBERS_ALLOWED else str(number)


def getGiftSystemCongratulationText(messageID):
    return backport.text(R.strings.ny.giftSystem.messages.num(messageID, default=R.strings.ny.giftSystem.messages.default)())


def getGiftSystemCongratulationResource(messageID):
    resource = R.strings.ny.giftSystem.messages.num(messageID)
    return resource if resource.exists() else R.strings.ny.giftSystem.messages.default


def getGiftSystemRandomCongratulationID(excludeID=0):
    congratIDs = set(xrange(1, R.strings.ny.giftSystem.messages.length())) - {excludeID}
    return random.choice(list(congratIDs))


def extractCompletedCollectionQuests(quests):
    completedCollectionQuests = [ questID for questID in quests.get('completedQuestIDs', set()) if questID in new_year.g_cache.collectionRewardsByCollectionID ]
    return completedCollectionQuests


def extractCollectionsRewards(completedCollectionQuests):
    eventsCache = dependency.instance(IEventsCache)
    for collectionQuest in completedCollectionQuests:
        collectionStrID = new_year.g_cache.collectionRewardsByCollectionID[collectionQuest]
        quest = eventsCache.getQuestByID(collectionQuest)
        if quest:
            yield {collectionStrID: quest.getBonuses()}
