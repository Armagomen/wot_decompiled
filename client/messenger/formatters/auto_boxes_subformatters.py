# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/auto_boxes_subformatters.py
import typing
import BigWorld
from adisp import adisp_async, adisp_process
from dossiers2.ui.achievements import BADGES_BLOCK
from gui.impl import backport
from gui.impl.gen import R
from gui.lootbox_system.base.awards import preformatRewardsInfo
from gui.lootbox_system.base.common import TEXT_RESOURCE_PREFIX, NotificationPathPart, getTextResource, DEFAULT_EVENT_NAME
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.formatters import text_styles
from gui.shared.gui_items.dossier import getAchievementFactory
from gui.shared.gui_items.loot_box import ALL_LUNAR_NY_LOOT_BOX_TYPES, WTLootBoxes, NewYearLootBoxes
from gui.shared.notifications import NotificationGroup, NotificationPriorityLevel
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import LootBoxAchievesFormatter, QuestAchievesFormatter, ServiceChannelFormatter, WaitItemsSyncFormatter
from messenger.formatters.service_channel_helpers import MessageData, getCustomizationItemData, getRewardsForBoxes
from skeletons.gui.shared import IItemsCache

class IAutoLootBoxSubFormatter(object):

    @classmethod
    def getBoxesOfThisGroup(cls, data):
        pass

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        pass

    @classmethod
    def _isBoxOfRequiredTypes(cls, boxID, boxTypes):
        pass


class AutoLootBoxSubFormatter(IAutoLootBoxSubFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getBoxesOfThisGroup(cls, data):
        return set((boxID for boxID in data.iterkeys() if cls._isBoxOfThisGroup(boxID)))

    @classmethod
    def _isBoxOfRequiredTypes(cls, boxID, boxTypes):
        box = cls.__itemsCache.items.tokens.getLootBoxByID(boxID)
        return box is not None and box.getType() in boxTypes


class AsyncAutoLootBoxSubFormatter(WaitItemsSyncFormatter, AutoLootBoxSubFormatter):

    def __init__(self):
        super(AsyncAutoLootBoxSubFormatter, self).__init__()
        self._achievesFormatter = LootBoxAchievesFormatter()


class SyncAutoLootBoxSubFormatter(ServiceChannelFormatter, AutoLootBoxSubFormatter):

    def __init__(self):
        super(SyncAutoLootBoxSubFormatter, self).__init__()
        self._achievesFormatter = LootBoxAchievesFormatter()


class EventBoxesFormatter(AsyncAutoLootBoxSubFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data)
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            fmtBoxes = self.__getFormattedBoxes(message, openedBoxesIDs)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processTokens=False)
            ctx = {'boxes': fmtBoxes,
             'rewards': backport.text(self._getTextResPath().rewards(), rewards=fmt)}
            formatted = g_settings.msgTemplates.format(self._getMessageTemplate(), ctx=ctx)
            settings = self._getGuiSettings(message, self._getMessageTemplate())
            callback([MessageData(formatted, settings)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, WTLootBoxes.ALL())

    @staticmethod
    def _getMessageTemplate():
        pass

    @staticmethod
    def _getTextResPath():
        return R.strings.messenger.serviceChannelMessages.lootBoxesAutoOpen.event

    def __getFormattedBoxes(self, message, openedBoxesIDs):
        boxes = []
        for boxID in openedBoxesIDs:
            box = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
            boxes.append(backport.text(self._getTextResPath().counter(), boxName=box.getUserName(), count=message.data[boxID]['count']))

        return ', '.join(boxes)


class NYPostEventBoxesFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'LootBoxesAutoOpenMessage'
    __REWARDS_TEMPLATE = 'LootBoxRewardsSysMessage'
    __REQUIERED_BOX_TYPES = {NewYearLootBoxes.COMMON, NewYearLootBoxes.PREMIUM, NewYearLootBoxes.SPECIAL}

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data)
            callback([self.__getMainMessage(message, openedBoxesIDs), self.__getRewardsMessage(message, openedBoxesIDs)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, cls.__REQUIERED_BOX_TYPES)

    def __getMainMessage(self, message, openedBoxesIDs):
        count = backport.text(R.strings.messenger.serviceChannelMessages.lootBoxesAutoOpen.counter(), count=sum((message.data[boxId]['count'] for boxId in openedBoxesIDs)))
        oldStyleCount = {bID:message.data[bID]['count'] for bID in openedBoxesIDs}
        rewards = getRewardsForBoxes(message, openedBoxesIDs)
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'count': count}, data={'savedData': {'rewards': rewards,
                       'boxIDs': oldStyleCount}})
        settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
        settings.groupID = NotificationGroup.OFFER
        settings.showAt = BigWorld.time()
        return MessageData(formatted, settings)

    def __getRewardsMessage(self, message, openedBoxesIDs):
        allRewards = getRewardsForBoxes(message, openedBoxesIDs)
        fmt = self._achievesFormatter.formatQuestAchieves(allRewards, asBattleFormatter=False, processTokens=False)
        formattedRewards = g_settings.msgTemplates.format(self.__REWARDS_TEMPLATE, ctx={'text': fmt})
        settingsRewards = self._getGuiSettings(message, self.__REWARDS_TEMPLATE)
        settingsRewards.showAt = BigWorld.time()
        return MessageData(formattedRewards, settingsRewards)


class NYGiftSystemSurpriseFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'NYSpecialLootBoxesAutoOpenMessage'
    __REQUIERED_BOX_TYPES = {NewYearLootBoxes.SPECIAL_AUTO}

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data)
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processTokens=False)
            formattedData = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'achieves': fmt})
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            settings.showAt = BigWorld.time()
            callback([MessageData(formattedData, settings)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, cls.__REQUIERED_BOX_TYPES)


class LunarNYEnvelopeAutoOpenFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'LunarBoxesAutoOpenMessage'
    _DECAL_TYPE_NAME = 'projection_decal'

    def __init__(self):
        super(LunarNYEnvelopeAutoOpenFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data)
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            if 'charms' in rewards:
                rewards.pop('charms')
            if 'customizationSum' in rewards:
                rewards.pop('customizationSum')
            fmt = self.formatAchieves(rewards, self._achievesFormatter)
            formattedRewards = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'rewards': fmt})
            settingsRewards = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            settingsRewards.showAt = BigWorld.time()
            callback([MessageData(formattedRewards, settingsRewards)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def formatAchieves(cls, rewards, formatter):
        result = []
        items = getMergedBonusesFromDicts((rewards,))
        formatedItems = formatter.formatQuestAchieves(items, False, processCustomizations=False)
        if formatedItems:
            result.append(formatedItems)
        if 'customizations' in rewards:
            customizations = rewards.get('customizations')
            decalsStr = cls.__makeDecalsString(customizations)
            if decalsStr:
                result.append(decalsStr)
        achievementsNames = cls.__extractAchievements(items)
        if achievementsNames:
            result.append(cls.__makeAchieve('dossiersAccruedInvoiceReceived', dossiers=', '.join(achievementsNames)))
        return '<br/>'.join(result)

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, ALL_LUNAR_NY_LOOT_BOX_TYPES)

    @classmethod
    def __makeAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)

    @staticmethod
    def __extractAchievements(data):
        result = set()
        for block in data.get('dossier', {}).values():
            if isinstance(block, dict):
                for record in block.keys():
                    if record[0] == BADGES_BLOCK:
                        continue
                    factory = getAchievementFactory(record)
                    if factory is not None:
                        a = factory.create()
                        if a is not None:
                            result.add(a.getUserName())

        return result

    @classmethod
    def __makeDecalsString(cls, customizations):
        decals = []
        for customization in customizations:
            custType = customization.get('custType', None)
            custValue = customization.get('value', 0)
            if custType == cls._DECAL_TYPE_NAME and custValue > 0:
                _, itemUserName = getCustomizationItemData(customization['id'], custType)
                decals.append(itemUserName)

        if len(decals) > 1:
            decalsTitle = backport.text(R.strings.messenger.serviceChannelMessages.lunarBoxesAutoOpen.many.projection_decal())
            return decalsTitle + ' '.join(decals)
        elif decals:
            decalsTitle = backport.text(R.strings.messenger.serviceChannelMessages.lunarBoxesAutoOpen.projection_decal())
            return ''.join((decalsTitle, decals[0]))
        else:
            return ''


class LootBoxSystemAutoOpenFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'LootBoxSystemAutoOpenMessage'
    __BREAK = R.strings.lootbox_system.helpers.doubleBreakLine()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data)
            openedEventsBoxes = self.__getEventNames(message.data) if openedBoxesIDs else {}
            messages = []
            for name in openedEventsBoxes.keys():
                if R.strings.dyn(TEXT_RESOURCE_PREFIX + name).isValid():
                    eventBoxes = openedEventsBoxes.pop(name)
                    messages.append(self.__getMessage(message, eventBoxes, name))
                    openedBoxesIDs -= eventBoxes

            if openedBoxesIDs:
                messages.append(self.__getMessage(message, openedBoxesIDs, DEFAULT_EVENT_NAME))
            callback(messages)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def getBoxesOfThisGroup(cls, data):
        return {boxId for boxId, info in data.iteritems() if info.get('relatedFeature') == DEFAULT_EVENT_NAME}

    def __getEventNames(self, data):
        eventsBoxes = {}
        for id, info in data.iteritems():
            eventName = info.get('type')
            eventsBoxes.setdefault(eventName, set()).add(id)

        return eventsBoxes

    def __getMessage(self, message, openedBoxes, eventName):
        textPathParts = [NotificationPathPart.MAIN, NotificationPathPart.AUTOOPEN]
        header = backport.text(getTextResource(textPathParts + [NotificationPathPart.HEADER], eventName)())
        description = backport.text(getTextResource(textPathParts + [NotificationPathPart.TEXT], eventName)())
        countRes = getTextResource(textPathParts + [NotificationPathPart.COUNT], eventName)
        boxes = sum((message.data[boxId]['count'] for boxId in openedBoxes))
        count = backport.text(self.__BREAK) + backport.text(countRes(), boxes=text_styles.credits(boxes)) if countRes.exists() else ''
        boxesCounts = {bID:message.data[bID]['count'] for bID in openedBoxes}
        rewards = getRewardsForBoxes(message, openedBoxes)
        preformatRewardsInfo(rewards)
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'header': header,
         'description': description,
         'count': count}, data={'savedData': {'eventName': eventName,
                       'rewards': rewards,
                       'boxIDs': boxesCounts}})
        settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE, priorityLevel=NotificationPriorityLevel.HIGH)
        settings.showAt = BigWorld.time()
        return MessageData(formatted, settings)
