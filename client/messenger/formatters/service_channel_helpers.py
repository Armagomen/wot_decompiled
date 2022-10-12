# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel_helpers.py
import logging
import typing
from collections import namedtuple

from helpers import dependency
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationNamesToTypes
from messenger import g_settings
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.shared import IItemsCache

_logger = logging.getLogger(__name__)
EOL = '\n'
DEFAULT_MESSAGE = 'defaultMessage'
if typing.TYPE_CHECKING:
    pass
MessageData = namedtuple('MessageData', 'data, settings')

def getRewardsForBoxes(message, boxIDs):
    data = message.data or {}
    resultRewards = {}
    for boxID in boxIDs:
        mergeRewards(resultRewards, data[boxID]['rewards'])

    return resultRewards


def getRewardsForQuests(message, questIDs):
    data = message.data or {}
    detailRewards = data.get('detailedRewards', {})
    resultRewards = {}
    for questID, rewards in detailRewards.items():
        if questID in questIDs:
            mergeRewards(resultRewards, rewards)

    return resultRewards


def mergeRewards(resultRewards, rewards):
    for bonusName, bonusValue in rewards.items():
        if bonusName in BONUS_MERGERS:
            BONUS_MERGERS[bonusName](resultRewards, bonusName, bonusValue, False, 1, None)
        if bonusName == 'selectableCrewbook':
            _mergeSelectableCrewbook(resultRewards, bonusName, bonusValue)
        _logger.warning('BONUS_MERGERS has not bonus %s', bonusName)

    return


def _mergeSelectableCrewbook(resultRewards, bonusName, bonusValue):
    selectablesTotal = resultRewards.setdefault(bonusName, {})
    for item in bonusValue:
        selectablesTotal[item['itemName']] = item['count']


def getCustomizationItem(itemId, customizationName):
    itemsCache = dependency.instance(IItemsCache)
    customizationType = CustomizationNamesToTypes.get(customizationName.upper())
    if customizationType is None:
        _logger.warning('Wrong customization name: %s', customizationName)
    compactDescr = makeIntCompactDescrByID('customizationItem', customizationType, itemId)
    return itemsCache.items.getItemByCD(compactDescr)


def getCustomizationItemData(itemId, customizationName):
    item = getCustomizationItem(itemId, customizationName)
    itemName = item.userName
    itemTypeName = item.itemFullTypeName
    return _CustomizationItemData(itemTypeName, itemName)


_CustomizationItemData = namedtuple('_CustomizationItemData', ('guiItemType', 'userName'))

def getDefaultMessage(normal='', bold=''):
    return g_settings.msgTemplates.format(DEFAULT_MESSAGE, {'normal': normal,
     'bold': bold})
