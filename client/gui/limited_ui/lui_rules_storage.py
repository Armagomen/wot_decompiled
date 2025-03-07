# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/limited_ui/lui_rules_storage.py
import logging
from collections import namedtuple, defaultdict
from enumerations import Enumeration, EnumItem
import typing
import BigWorld
from account_helpers import AccountSettings
from expressions import parseExpression
from helpers import dependency
from ids_generators import SequenceIDGenerator
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Set, List, Tuple, Iterable
_logger = logging.getLogger(__name__)

class LuiRuleTypes(CONST_CONTAINER):
    PERMANENT = 'permanent'
    COMMON = 'common'
    VERSIONED = 'versioned'
    NOVICE = (COMMON, VERSIONED)


LUI_RULES = Enumeration('Limited UI rules', ['store',
 'profile',
 'profileHof',
 'profileTechniquePage',
 'sessionStats',
 'blueprintsButton',
 'missions',
 'MissionsMarathonView',
 'PersonalMissionOperations',
 'referralButtonCounter',
 'CustomizationBtnBubble',
 'TechTreeEvent',
 'DogTagHangarHint',
 'ModeSelectorWidgetsBtnHint',
 'PersonalReservesHangarHint',
 'ModernizedSetupTabHint',
 'OfferBannerWindow',
 'BattlePassEntry',
 'ProgressiveItemsReward',
 'DailyMissions',
 'CraftMachineEntryPoint',
 'MapboxEntryPoint',
 'BattleMissions',
 'HeroTank',
 'BattleMattersFlag',
 'PersonalMissions',
 'sysMsgCollectionStartBattlePass',
 'sysMsgCollectionsUpdatedEntry',
 'storage',
 'PersonalReservesHangarButton',
 'StrongholdEntryPoint',
 'BREntryPoint',
 'WDRNewbieReward',
 'LiveOpsWebEventsEntryPoint',
 'AdvancedAchievements',
 'EasyTankEquipEntryPoint'])
_POSTPONED_RULES_DELAY = 5.0
_SERVER_SETTINGS_BLOCK_BITS = 32

class _LimitedUIRule(namedtuple('_LimitedUIRule', ('idx', 'expression', 'tokens', 'message', 'ruleType'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(idx=0, expression=None, tokens=set(), message=None, ruleType=None)
        dataToUpdate = {k:v for k, v in kwargs.items() if k in cls._fields}
        defaults.update(dataToUpdate)
        return super(_LimitedUIRule, cls).__new__(cls, **defaults)


class _LimitedUIRules(object):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, rules):
        super(_LimitedUIRules, self).__init__()
        self.__isInited = False
        self.__rules = rules or {}
        self.__postponedRulesCallbackID = None
        self.__postponedCompletedRules = defaultdict(set)
        if rules is not None:
            self.__clearStoredVersionedRules()
        return

    def getRule(self, ruleID):
        return self.__rules.get(ruleID, None)

    def getRulesIDs(self):
        return set(self.__rules.keys())

    def getRulesIDsByTypes(self, ruleTypes):
        return set((ruleID for ruleID, rule in self.__rules.items() if rule.ruleType in ruleTypes))

    def hasRule(self, ruleID):
        return ruleID in self.__rules

    def hasRules(self):
        return bool(self.__rules)

    def hasRulesByTypes(self, ruleTypes):
        return bool(self.getRulesIDsByTypes(ruleTypes))

    def getTokens(self, ruleID):
        return self.getRule(ruleID).tokens if self.hasRule(ruleID) else set()

    def getSysMessage(self, ruleID):
        return self.getRule(ruleID).message if self.hasRule(ruleID) else None

    def clear(self):
        self.__rules.clear()
        self.__postponedCompletedRules = None
        return

    def isCompleted(self, ruleID):
        rule = self.getRule(ruleID)
        if rule is None or ruleID in self.__postponedCompletedRules[rule.ruleType]:
            return True
        else:
            return self.__isClientRuleCompleted(ruleID) if rule.ruleType == LuiRuleTypes.VERSIONED else self.__isServerRuleCompleted(rule)

    def completeRule(self, ruleID):
        rule = self.getRule(ruleID)
        if rule is None:
            _logger.warning("Couldn't complete rule, ruleID was not found: %s", ruleID.name())
            return
        else:
            self.clearPostponedRulesCallback()
            self.__postponedCompletedRules[rule.ruleType].add(ruleID)
            self.__postponedRulesCallbackID = BigWorld.callback(_POSTPONED_RULES_DELAY, self.__storePostponedRulesByDelay)
            return

    def completeRules(self, ruleIDs):
        self.clearPostponedRulesCallback()
        for ruleID in ruleIDs:
            rule = self.getRule(ruleID)
            if rule is None:
                _logger.warning("Couldn't complete rule, ruleID was not found: %s", ruleID.name())
                continue
            self.__postponedCompletedRules[rule.ruleType].add(ruleID)

        self.__postponedRulesCallbackID = BigWorld.callback(_POSTPONED_RULES_DELAY, self.__storePostponedRulesByDelay)
        return

    def storePostponedRules(self):
        if not self.__hasPostponedRules():
            return
        else:
            serverRules = defaultdict(list)
            for ruleType, ruleIDs in self.__postponedCompletedRules.items():
                if ruleType == LuiRuleTypes.VERSIONED:
                    AccountSettings.completeVersionedRules([ ruleID.name() for ruleID in ruleIDs ])
                    del self.__postponedCompletedRules[ruleType]
                for ruleID in ruleIDs:
                    rule = self.getRule(ruleID)
                    if rule is None:
                        _logger.warning("Couldn't complete postponed rule, ruleID was not found: %s", ruleID.name())
                        continue
                    storage, offset = self.__getServerRuleStorageInfo(rule)
                    serverRules[storage, ruleType].append(offset)

            if serverRules and self.__settingsCore.serverSettings.setLimitedUIGroupProgress(serverRules):
                self.__postponedCompletedRules.clear()
            else:
                self.clearPostponedRulesCallback()
                self.__postponedRulesCallbackID = BigWorld.callback(_POSTPONED_RULES_DELAY, self.__storePostponedRulesByDelay)
            return

    def clearPostponedRulesCallback(self):
        if self.__postponedRulesCallbackID is not None:
            BigWorld.cancelCallback(self.__postponedRulesCallbackID)
            self.__postponedRulesCallbackID = None
        return

    def updateRules(self, rules):
        self.__rules = rules
        if not self.__isInited:
            self.__postponedCompletedRules.clear()
            self.__clearStoredVersionedRules()
            self.clearPostponedRulesCallback()
        else:
            hasPostponedCallback = self.__hasPostponedRules() and self.__postponedRulesCallbackID is not None
            self.clearPostponedRulesCallback()
            if hasPostponedCallback:
                self.__postponedRulesCallbackID = BigWorld.callback(_POSTPONED_RULES_DELAY, self.__storePostponedRulesByDelay)
        return

    def __storePostponedRulesByDelay(self):
        self.__postponedRulesCallbackID = None
        self.storePostponedRules()
        return

    @staticmethod
    def __isClientRuleCompleted(ruleID):
        return AccountSettings.isVersionedRuleCompleted(ruleID.name())

    def __isServerRuleCompleted(self, rule):
        storage, offset = self.__getServerRuleStorageInfo(rule)
        return bool(self.__settingsCore.serverSettings.getLimitedUIProgress(storage, offset, rule.ruleType))

    def __clearStoredVersionedRules(self):
        versionedRules = AccountSettings.getCompletedVersionedRules()
        if versionedRules:
            AccountSettings.clearVersionedRules(set(versionedRules) - {ruleID.name() for ruleID in self.getRulesIDsByTypes([LuiRuleTypes.VERSIONED])})
        self.__isInited = True

    @staticmethod
    def __getServerRuleStorageInfo(rule):
        index = rule.idx
        storageIdx = index / _SERVER_SETTINGS_BLOCK_BITS
        offset = index % _SERVER_SETTINGS_BLOCK_BITS
        return (storageIdx, offset)

    def __hasPostponedRules(self):
        return any(self.__postponedCompletedRules.values())


class RulesStorageMaker(object):

    @classmethod
    def makeStorage(cls, rawRulesData=None):
        rules = None
        if rawRulesData is not None:
            rules = cls.__makeRules(rawRulesData)
        return _LimitedUIRules(rules)

    @classmethod
    def updateStorage(cls, storage, rawRulesData):
        storage.updateRules(cls.__makeRules(rawRulesData))

    @classmethod
    def __makeRules(cls, rawRulesData):
        data = dict()
        idGen = SequenceIDGenerator(lowBound=-1)
        for ruleType, rulesData in rawRulesData.items():
            data.update(cls.__makeRulesData(ruleType, rulesData, idGen))

        rulesIDs = set(data.keys())
        for item in data.values():
            cls.__normalizeRuleItem(data, rulesIDs, item)

        return {LUI_RULES.lookup(ruleID):_LimitedUIRule(**value) for ruleID, value in data.items() if LUI_RULES.lookup(ruleID) is not None}

    @classmethod
    def __makeRulesData(cls, ruleType, rules, idGen):
        idGen.clear()
        return {ruleID:cls.__makeRuleData(idGen, expressionStr, message, ruleType) for ruleID, expressionStr, message in rules}

    @staticmethod
    def __makeRuleData(idGen, expressionStr, message, ruleType):
        expression, tokens = parseExpression(expressionStr)
        return {'idx': idGen.next(),
         'expressionStr': expressionStr,
         'expression': expression,
         'tokens': tokens,
         'message': message,
         'ruleType': ruleType}

    @classmethod
    def __normalizeRuleItem(cls, data, rulesIDs, item):
        tokens = item['tokens']
        expressionStr = item['expressionStr']
        ruleDependencies = tokens & rulesIDs
        if ruleDependencies:
            while ruleDependencies:
                ruleDependency = ruleDependencies.pop()
                dependsItem = data[ruleDependency]
                dependencyExpression = cls.__normalizeRuleItem(data, rulesIDs, dependsItem)
                expressionStr = expressionStr.replace(ruleDependency, '({})'.format(dependencyExpression))

            expression, tokens = parseExpression(expressionStr)
            item['expressionStr'] = expressionStr
            item['expression'] = expression
            item['tokens'] = tokens
        return expressionStr
