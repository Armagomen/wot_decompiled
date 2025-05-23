# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/progress.py
import logging
import math
import operator
from collections import namedtuple
import typing
import BigWorld
import personal_missions
from battle_pass_common import BattlePassConsts, isPostProgressionChapter
from constants import EVENT_TYPE, NEW_PERK_SYSTEM as NPS
from dog_tags_common.components_config import componentConfigAdapter as cca
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import getC11nProgressionLinkBtnParams, getProgressionPostBattleInfo, parseEventID, getC11n2dProgressionLinkBtnParams
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import BattlePassTextBonusesPacker
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getEventPostBattleInfo, get2dProgressionStylePostBattleInfo
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.Scaleform.genConsts.PROGRESSIVEREWARD_CONSTANTS import PROGRESSIVEREWARD_CONSTANTS as prConst
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_results.components import base
from gui.battle_results.settings import PROGRESS_ACTION
from gui.dog_tag_composer import dogTagComposer
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardVO
from gui.impl.gen import R
from gui.prestige.prestige_helpers import mapGradeIDToUI, getCurrentGrade, getCurrentProgress, prestigePointsToXP, hasVehiclePrestige, MAX_GRADE_ID
from gui.server_events import formatters
from gui.server_events.awards_formatters import QuestsBonusComposer
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID
from gui.server_events.events_helpers import isC11nQuest, getDataByC11nQuest
from gui.shared.formatters import getItemPricesVO, getItemUnlockPricesVO, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman, getVehicleComponentsByType
from gui.shared.gui_items.Vehicle import getLevelIconPath
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from items import tankmen
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple
    from gui.battle_results.reusable import _ReusableInfo
    from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import BattlePassProgress
_POST_BATTLE_RES = R.strings.battle_pass.reward.postBattle
_MIN_BATTLES_TO_SHOW_PROGRESS = 5
_logger = logging.getLogger(__name__)

def isQuestCompleted(_, pPrev, pCur):
    return pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0


class VehicleProgressHelper(object):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehTypeCompDescr):
        items = self.itemsCache.items
        stats = items.stats
        self.__unlocks = stats.unlocks
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__vehicle = items.getItemByCD(vehTypeCompDescr)
        self.__vehicleXp = stats.vehiclesXPs.get(self.__vehTypeCompDescr, 0)
        self.__avgVehicleXp = self.__getAvgVehicleXp(self.__vehTypeCompDescr)

    def clear(self):
        self.__unlocks = None
        self.__vehicle = None
        self.__vehicleXp = None
        self.__avgVehicleXp = None
        self.__vehTypeCompDescr = None
        return

    def getProgressList(self, vehicleBattleXp, pureCreditsReceived, tankmenXps):
        result = []
        ready2UnlockVehicles, ready2UnlockModules = self.getReady2UnlockItems(vehicleBattleXp)
        ready2BuyVehicles, ready2BuyModules = self.getReady2BuyItems(pureCreditsReceived)
        result.extend(ready2UnlockModules)
        result.extend(ready2BuyModules)
        result.extend(self.getNewSkilledTankmen(tankmenXps))
        result.extend(ready2UnlockVehicles)
        result.extend(ready2BuyVehicles)
        return result

    def __getAvgVehicleXp(self, vehTypeCompDescr):
        vehiclesStats = self.itemsCache.items.getAccountDossier().getRandomStats().getVehicles()
        vehicleStats = vehiclesStats.get(vehTypeCompDescr, None)
        if vehicleStats is not None:
            battlesCount, _, xp = vehicleStats
            if battlesCount:
                return xp / battlesCount
            return 0
        else:
            return 0

    def getReady2UnlockItems(self, vehicleBattleXp):
        ready2UnlockModules = []
        ready2UnlockVehicles = []
        possible2UnlockItems = g_techTreeDP.getAllPossibleItems2Unlock(self.__vehicle, self.__unlocks)
        getter = self.itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in possible2UnlockItems.iteritems():
            item = getter(itemTypeCD)
            if self.__vehicleXp - unlockProps.xpCost <= vehicleBattleXp and item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                avgBattles2Unlock = self.__getAvgBattles2Unlock(unlockProps)
                if not self.__vehicleXp > unlockProps.xpCost:
                    if 0 < avgBattles2Unlock <= _MIN_BATTLES_TO_SHOW_PROGRESS:
                        ready2UnlockVehicles.append(self.__makeUnlockVehicleVO(item, unlockProps, avgBattles2Unlock))
                elif self.__vehicleXp > unlockProps.xpCost:
                    ready2UnlockModules.append(self.__makeUnlockModuleVO(item, unlockProps))

        return (ready2UnlockVehicles, ready2UnlockModules)

    def getReady2BuyItems(self, pureCreditsReceived):
        ready2BuyModules = []
        ready2BuyVehicles = []
        creditsValue = self.itemsCache.items.stats.credits
        unlockedVehicleItems = g_techTreeDP.getUnlockedVehicleItems(self.__vehicle, self.__unlocks)
        getter = self.itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in unlockedVehicleItems.iteritems():
            item = getter(itemTypeCD)
            price = item.getBuyPrice(preferred=False).price
            if price.isCurrencyDefined(Currency.CREDITS) and not item.isInInventory:
                priceCredits = price.credits
                if creditsValue - priceCredits <= pureCreditsReceived and creditsValue > priceCredits:
                    if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                        ready2BuyVehicles.append(self.__makeVehiclePurchaseVO(item, unlockProps, price))
                    elif not item.isInstalled(self.__vehicle):
                        items = getVehicleComponentsByType(self.__vehicle, item.itemTypeID).values()
                        if items:
                            installedModule = max(items, key=lambda module: module.level)
                            if item.level > installedModule.level:
                                ready2BuyModules.append(self.__makeModulePurchaseVO(item, unlockProps, price))

        return (ready2BuyVehicles, ready2BuyModules)

    def getNewSkilledTankmen(self, tankmenXps):
        skilledTankmen = []
        for _, tman in self.__vehicle.crew:
            if tman is not None and tman.hasSkillToLearn():
                if not tman.isMaxRoleLevel:
                    continue
                tmanBattleXp = tankmenXps.get(tman.invID, 0)
                avgBattles2NewSkill = 0
                newSkillEarned = False
                bonusSkillsAmount = 0
                if tman.hasNewSkill(useCombinedRoles=True):
                    tmanDescr = tman.descriptor
                    lastSkillNumber = tmanDescr.lastSkillSeqNumber
                    wallet = tmanDescr.freeXP + tankmen.TankmanDescr.getXpCostForSkillsLevels(tmanDescr.lastSkillLevel if lastSkillNumber else 0, lastSkillNumber)
                    skillsCountBefore = min(tmanDescr.getSkillsCountFromXp(wallet - tmanBattleXp), NPS.MAX_MAJOR_PERKS)
                    skillsCount = min(tmanDescr.getSkillsCountFromXp(wallet), NPS.MAX_MAJOR_PERKS)
                    newSkillEarned, bonusSkillsAmount = self.__getBonusSkillsAmount(tman, skillsCountBefore, skillsCount)
                else:
                    tmanDossier = self.itemsCache.items.getTankmanDossier(tman.invID)
                    avgBattles2NewSkill = self.__getAvgBattles2NewSkill(tmanDossier.getAvgXP(), tman)
                    if 0 < avgBattles2NewSkill <= _MIN_BATTLES_TO_SHOW_PROGRESS:
                        newSkillEarned, bonusSkillsAmount = self.__getBonusSkillsAmount(tman, 1, 0)
                if newSkillEarned:
                    skilledTankmen.append(self.__makeTankmanVO(tman, newSkillEarned, bonusSkillsAmount, avgBattles2NewSkill))

        return skilledTankmen

    @staticmethod
    def __getBonusSkillsAmount(tmanToCheck, skillsCountBefore, skillsCountAfter):
        newSkillsCount = skillsCountAfter - skillsCountBefore
        if newSkillsCount > 0:
            bonusSkillsAmount = 0
            if (skillsCountBefore + tmanToCheck.freeSkillsCount) % 2 == 0:
                bonusSkillsAmount = newSkillsCount * (len(tmanToCheck.combinedRoles) - 1)
            return (True, bonusSkillsAmount)
        return (False, 0)

    def __getAvgBattles2Unlock(self, unlockProps):
        return int(math.ceil((unlockProps.xpCost - self.__vehicleXp) / float(self.__avgVehicleXp))) if self.__avgVehicleXp > 0 else 0

    def __getAvgBattles2NewSkill(self, avgTmanXp, tman):
        return max(1, math.ceil(tman.getNextSkillXpCost() / avgTmanXp)) if avgTmanXp > 0 else 0

    def __makeTankmanDescription(self, roleName, fullName):
        role = text_styles.main(roleName)
        name = text_styles.standard(fullName)
        return _ms(BATTLE_RESULTS.COMMON_CREWMEMBER_DESCRIPTION, name=name, role=role)

    def __makeVehicleDescription(self, vehicle):
        vehicleType = text_styles.standard(vehicle.typeUserName)
        vehicleName = text_styles.main(vehicle.userName)
        return _ms(BATTLE_RESULTS.COMMON_VEHICLE_DETAILS, vehicle=vehicleName, type=vehicleType)

    def __makeTankmanVO(self, tman, newSkillEarned, bonusSkillsAmount, avgBattles2NewSkill):
        prediction = ''
        if 0 < avgBattles2NewSkill <= _MIN_BATTLES_TO_SHOW_PROGRESS:
            prediction = _ms(BATTLE_RESULTS.COMMON_NEWSKILLPREDICTION, battles=backport.getIntegralFormat(avgBattles2NewSkill))
        data = {'linkId': tman.invID}
        if newSkillEarned:
            data.update({'title': _ms(BATTLE_RESULTS.COMMON_CREWMEMBER_NEWSKILL),
             'prediction': prediction,
             'linkEvent': PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE,
             'bonusSkillsAmount': bonusSkillsAmount})
        if tman.skinID != NO_CREW_SKIN_ID:
            skinItem = self.itemsCache.items.getCrewSkin(tman.skinID)
            data['tankmenIcon'] = Tankman.getCrewSkinIconBig(skinItem.getIconID())
            fullTankmanName = localizedFullName(skinItem)
        else:
            data['tankmenIcon'] = Tankman.getBarracksIconPath(tman.nationID, tman.descriptor.iconID)
            fullTankmanName = tman.fullUserName
        data['description'] = self.__makeTankmanDescription(tman.roleUserName, fullTankmanName)
        return data

    def __makeUnlockModuleVO(self, item, unlockProps):
        return {'title': _ms(BATTLE_RESULTS.COMMON_FITTING_RESEARCH),
         'description': text_styles.main(item.userName),
         'fittingType': item.getGUIEmblemID(),
         'lvlIcon': getLevelIconPath(item.level),
         'price': getItemUnlockPricesVO(unlockProps),
         'linkEvent': PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}

    def __makeUnlockVehicleVO(self, item, unlockProps, avgBattlesTillUnlock):
        prediction = ''
        if avgBattlesTillUnlock > 0:
            prediction = _ms(BATTLE_RESULTS.COMMON_RESEARCHPREDICTION, battles=avgBattlesTillUnlock)
        return {'title': _ms(BATTLE_RESULTS.COMMON_VEHICLE_RESEARCH),
         'description': self.__makeVehicleDescription(item),
         'vehicleIcon': item.iconSmall,
         'lvlIcon': getLevelIconPath(item.level),
         'prediction': prediction,
         'price': getItemUnlockPricesVO(unlockProps),
         'linkEvent': PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}

    def __makeVehiclePurchaseVO(self, item, unlockProps, price):
        return {'title': _ms(BATTLE_RESULTS.COMMON_VEHICLE_PURCHASE),
         'description': self.__makeVehicleDescription(item),
         'vehicleIcon': item.iconSmall,
         'lvlIcon': getLevelIconPath(item.level),
         'price': getItemPricesVO(ItemPrice(price=price, defPrice=price)),
         'linkEvent': PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}

    def __makeModulePurchaseVO(self, item, unlockProps, price):
        return {'title': _ms(BATTLE_RESULTS.COMMON_FITTING_PURCHASE),
         'description': text_styles.main(item.userName),
         'fittingType': item.itemTypeName,
         'lvlIcon': getLevelIconPath(item.level),
         'price': getItemPricesVO(ItemPrice(price=price, defPrice=price)),
         'linkEvent': PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}


class VehicleProgressBlock(base.StatsBlock):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        vo = super(VehicleProgressBlock, self).getVO()
        for item in vo:
            isNewEarnedSkill = item.get('linkEvent') == PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE
            if not isNewEarnedSkill:
                continue
            tankman = self._itemsCache.items.getTankman(item['linkId'])
            item['linkBtnEnabled'] = tankman.canLearnSkills()

        return vo

    def setRecord(self, result, reusable):
        xpEarnings = reusable.personal.xpProgress
        for intCD, data in reusable.personal.getVehicleCDsIterator(result):
            xpEarningsForVehicle = xpEarnings.get(intCD, {})
            vehicleBattleXp = xpEarningsForVehicle.get('xp', 0)
            tmenXps = dict(xpEarningsForVehicle.get('xpByTmen', []))
            pureCreditsReceived = data.get('pureCreditsReceived', 0)
            helper = VehicleProgressHelper(intCD)
            progress = helper.getProgressList(vehicleBattleXp, pureCreditsReceived, tmenXps)
            for item in progress:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', item))

            helper.clear()


PMComplete = namedtuple('PMComplete', ['isMainComplete', 'isAddComplete'])

class BattlePassProgressBlock(base.StatsBlock):
    __battlePass = dependency.descriptor(IBattlePassController)

    def setRecord(self, result, reusable):
        bpp = reusable.battlePassProgress
        if not bpp.hasProgress:
            return
        isNewPoints = bpp.pointsAux > 0 or bpp.questPoints > 0 or bpp.bonusCapPoints > 0 or bpp.bpTopPoints > 0
        if isNewPoints:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassPoints(bpp)))
        if bpp.previousChapterID:
            chapterID = bpp.previousChapterID
            for lvl in xrange(bpp.getPreviousLevel(chapterID), bpp.getCurrentLevel(chapterID)):
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, lvl, chapterID)))

        if bpp.previousChapterID != bpp.currentChapterID and bpp.currentChapterID:
            chapterID = bpp.currentChapterID
            for lvl in xrange(bpp.getPreviousLevel(chapterID), bpp.getCurrentLevel(chapterID)):
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, lvl, chapterID)))

        chapterID = bpp.currentChapterID
        levelProgressPresents = bpp.getCurrentLevelPoints(chapterID) and bpp.getCurrentLevelPoints(chapterID) != bpp.getMaxLevelPoints(chapterID)
        if bpp.pointsAux or levelProgressPresents:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, bpp.getCurrentLevel(chapterID), chapterID)))

    @classmethod
    def __formatBattlePassProgress(cls, progress, level, chapter):
        return ('', {'awards': cls.__makeProgressAwards(progress, chapter, level),
          'questInfo': cls.__makeProgressQuestInfo(progress, chapter, level),
          'questType': EVENT_TYPE.BATTLE_QUEST,
          'progressList': cls.__makeProgressList(progress, chapter, level),
          'questState': {'statusState': cls.__getMissionState(progress.isDone(chapterID=chapter))},
          'linkBtnTooltip': '' if progress.isApplied else backport.text(R.strings.battle_pass.progression.error()),
          'linkBtnEnabled': progress.isApplied})

    @classmethod
    def __formatBattlePassPoints(cls, progress):
        return ('', {'awards': [],
          'questInfo': cls.__makePointsInfo(progress),
          'questType': EVENT_TYPE.BATTLE_QUEST,
          'progressList': cls.__makePointsList(progress),
          'questState': {'statusState': MISSIONS_STATES.IN_PROGRESS},
          'linkBtnTooltip': '' if progress.isApplied else backport.text(R.strings.battle_pass.progression.error()),
          'linkBtnEnabled': progress.isApplied})

    @staticmethod
    def __makeProgressAwards(progress, chapter, level):
        nothing = []
        if level >= progress.getCurrentLevel(chapter):
            return nothing
        awards = progress.getLevelAwards(chapter, level + 1)
        if not awards:
            return nothing
        awardsList = QuestsBonusComposer(BattlePassTextBonusesPacker()).getPreformattedBonuses(awards)

        def makeUnavailableBlockData():
            return formatters.packTextBlock(text_styles.alert(backport.text(R.strings.quests.bonuses.notAvailable())))

        if awardsList:
            return [ award.getDict() for award in awardsList ]
        return [makeUnavailableBlockData().getDict()]

    @classmethod
    def __makeProgressQuestInfo(cls, progress, chapterID, level):
        isFreePoints = progress.pointsAux and not progress.isLevelMax(chapterID) or progress.isLevelMax(chapterID) and level == progress.getCurrentLevel(chapterID)
        isProgressDone = level < progress.getCurrentLevel(chapterID)
        if isFreePoints:
            title = backport.text(_POST_BATTLE_RES.title.free())
        elif not isPostProgressionChapter(chapterID):
            title = backport.text(_POST_BATTLE_RES.title(), level=level + 1, chapter=cls.__getChapterName(chapterID))
        else:
            level %= len(cls.__battlePass.getLevelsConfig(chapterID))
            title = backport.text(_POST_BATTLE_RES.title.postProgression(), level=level + 1)
        return {'status': cls.__getMissionState(isDone=isProgressDone),
         'questID': BattlePassConsts.FAKE_QUEST_ID,
         'rendererType': QUESTS_ALIASES.RENDERER_TYPE_QUEST,
         'eventType': EVENT_TYPE.BATTLE_QUEST,
         'maxProgrVal': progress.getMaxLevelPoints(chapterID),
         'tooltip': TOOLTIPS.QUESTS_RENDERER_LABEL,
         'description': title,
         'currentProgrVal': progress.getCurrentLevelPoints(chapterID),
         'tasksCount': -1,
         'progrBarType': cls.__getProgressBarType(not progress.isDone(chapterID)),
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS if chapterID and not cls.__battlePass.isChapterCompleted(chapterID) else TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS_SELECT}

    @classmethod
    def __makePointsInfo(cls, progress):
        chapterID = progress.previousChapterID
        return {'status': '',
         'questID': BattlePassConsts.FAKE_QUEST_ID,
         'eventType': EVENT_TYPE.BATTLE_QUEST,
         'description': backport.text(_POST_BATTLE_RES.progress.points()),
         'progrBarType': formatters.PROGRESS_BAR_TYPE.NONE,
         'tasksCount': -1,
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS if chapterID and not cls.__battlePass.isChapterCompleted(chapterID) else TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS_SELECT}

    @classmethod
    def __makeProgressList(cls, progress, chapter, level):
        isCurrentChapterLevel = level == progress.getCurrentLevel(chapter)
        isMaxChapterLevel = progress.isLevelMax(chapter)
        isFreePoints = progress.pointsAux and not isMaxChapterLevel or isMaxChapterLevel and isCurrentChapterLevel
        progressLevel = {'description': cls._getDescription(progress),
         'maxProgrVal': progress.getMaxLevelPoints(chapter),
         'progressDiff': '+ {}'.format(progress.getPointsDiff(chapter) if not isFreePoints else progress.pointsAux),
         'progressDiffTooltip': cls._getProgressDiffTooltip(progress, chapter),
         'currentProgrVal': progress.getCurrentLevelPoints(chapter),
         'progrBarType': cls.__getProgressBarType(not progress.pointsAux)}
        return [progressLevel] if not progress.isDone(chapter) or progress.pointsAux and not isMaxChapterLevel or isCurrentChapterLevel else []

    @classmethod
    def __makePointsList(cls, progress):
        progressList = []
        if progress.bpTopPoints > 0:
            description = backport.text(_POST_BATTLE_RES.progress.points.battle())
            tooltip = backport.text(_POST_BATTLE_RES.progress.battle.tooltip())
            points = progress.bpTopPoints
            progressList.append(cls.__getPointsInfo(description, tooltip, points))
        if progress.questPoints > 0:
            description = backport.text(_POST_BATTLE_RES.progress.points.quest())
            tooltip = backport.text(_POST_BATTLE_RES.progress.quests.tooltip())
            points = progress.questPoints
            progressList.append(cls.__getPointsInfo(description, tooltip, points))
        if progress.bonusCapPoints > 0:
            description = backport.text(_POST_BATTLE_RES.progress.points.bonus())
            tooltip = backport.text(_POST_BATTLE_RES.progress.bonus.tooltip())
            points = progress.bonusCapPoints
            progressList.append(cls.__getPointsInfo(description, tooltip, points))
        return progressList

    @staticmethod
    def __getPointsInfo(description, tooltip, points):
        pointsInfo = {'description': description,
         'maxProgrVal': 0,
         'progressDiff': '+ {}'.format(points),
         'progressDiffTooltip': tooltip,
         'currentProgrVal': 0,
         'progrBarType': formatters.PROGRESS_BAR_TYPE.NONE}
        return pointsInfo

    @classmethod
    def __getChapterName(cls, chapterID):
        return backport.text(R.strings.battle_pass.chapter.fullName.num(chapterID)()) if chapterID else ''

    @staticmethod
    def _getDescription(progress):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux())
        else:
            text = backport.text(_POST_BATTLE_RES.progress())
        return text

    @staticmethod
    def _getProgressDiffTooltip(progress, chapterID):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux.tooltip(), points=progress.pointsAux)
        else:
            text = backport.text(_POST_BATTLE_RES.progress.tooltip(), points=progress.getPointsDiff(chapterID))
        return text

    @staticmethod
    def __getMissionState(isDone):
        return MISSIONS_STATES.COMPLETED if isDone else MISSIONS_STATES.IN_PROGRESS

    @staticmethod
    def __getProgressBarType(needShow):
        return formatters.PROGRESS_BAR_TYPE.SIMPLE if needShow else formatters.PROGRESS_BAR_TYPE.NONE


class QuestsProgressBlock(base.StatsBlock):
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def getVO(self):
        vo = super(QuestsProgressBlock, self).getVO()
        return vo

    def setRecord(self, result, reusable):
        commonQuests = []
        c11nQuests = []
        personalMissions = {}
        allCommonQuests = self.eventsCache.getQuests()
        allCommonQuests.update(self.eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
        battleMattersProgressData = []
        questsProgress = reusable.personal.getQuestsProgress()
        if questsProgress:
            for qID, qProgress in questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = isQuestCompleted(pGroupBy, pPrev, pCur)
                if isC11nQuest(qID):
                    quest = allCommonQuests.get(qID)
                    if quest is not None:
                        c11nQuests.append((quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isCompleted))
                if qID.startswith(BATTLE_MATTERS_QUEST_ID):
                    data = self.__packQuestProgressData(qID, allCommonQuests, qProgress, isCompleted)
                    if data:
                        battleMattersProgressData.append(data)
                if qID in allCommonQuests:
                    data = self.__packQuestProgressData(qID, allCommonQuests, qProgress, isCompleted)
                    if data:
                        commonQuests.append(data)
                if personal_missions.g_cache.isPersonalMission(qID):
                    pqID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
                    questsCache = self.eventsCache.getPersonalMissions()
                    quest = questsCache.getAllQuests()[pqID]
                    progress = personalMissions.setdefault(quest, {})
                    progress.update({qID: isCompleted})

        for e, pCur, pPrev, reset, complete in battleMattersProgressData:
            info = getEventPostBattleInfo(e, allCommonQuests, pCur, pPrev, reset, complete)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        pm2Progress = reusable.personal.getPM2Progress()
        if pm2Progress:
            quests = self.eventsCache.getPersonalMissions().getAllQuests()
            for qID, data in pm2Progress.iteritems():
                quest = quests[qID]
                if quest in personalMissions:
                    personalMissions[quest].update(data)
                progress = personalMissions.setdefault(quest, {})
                progress.update(data)

        for quest, data in sorted(personalMissions.items(), key=operator.itemgetter(0), cmp=self.__sortPersonalMissions):
            if data.get(quest.getAddQuestID(), False):
                complete = PMComplete(True, True)
            elif data.get(quest.getMainQuestID(), False):
                complete = PMComplete(True, False)
            else:
                complete = PMComplete(False, False)
            info = getEventPostBattleInfo(quest, None, None, None, False, complete, progressData=data)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for vehicleIntCD, c11nProgression in reusable.personal.getC11nProgress().iteritems():
            for intCD, progressionData in sorted(c11nProgression.iteritems(), key=lambda (_, d): -d.get('level', 0)):
                info = getProgressionPostBattleInfo(intCD, vehicleIntCD, progressionData)
                if info is not None:
                    self.addComponent(self.getNextComponentIndex(), ProgressiveCustomizationVO('', info))

        questsByStyle = {}
        for e, pCur, pPrev, complete in c11nQuests:
            progressData = getDataByC11nQuest(e)
            styleID = progressData.styleID
            if styleID <= 0:
                continue
            quests = questsByStyle.setdefault(styleID, list())
            quests.append((e,
             pCur,
             pPrev,
             complete))

        for styleID, quests in questsByStyle.items():
            info = get2dProgressionStylePostBattleInfo(styleID, quests)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), QuestProgressiveCustomizationVO('', info))

        for e, pCur, pPrev, reset, complete in sorted(commonQuests, cmp=self.__sortCommonQuestsFunc):
            info = getEventPostBattleInfo(e, allCommonQuests, pCur, pPrev, reset, complete)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        return

    @staticmethod
    def __packQuestProgressData(qID, allCommonQuests, qProgress, isCompleted):
        pGroupBy, pPrev, pCur = qProgress
        quest = allCommonQuests.get(qID)
        data = None
        if quest is not None:
            isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
            if pPrev or max(pCur.itervalues()) != 0:
                data = (quest,
                 {pGroupBy: pCur},
                 {pGroupBy: pPrev},
                 isProgressReset,
                 isCompleted)
        return data

    @staticmethod
    def __sortPersonalMissions(a, b):
        aFullCompleted, bFullCompleted = a.isFullCompleted(), b.isFullCompleted()
        if aFullCompleted != bFullCompleted:
            return bFullCompleted - aFullCompleted
        aCompleted, bCompleted = a.isCompleted(), b.isCompleted()
        return bCompleted - aCompleted if aCompleted != bCompleted else b.getCampaignID() - a.getCampaignID()

    @staticmethod
    def __sortCommonQuestsFunc(aData, bData):
        aQuest, aCurProg, aPrevProg, _, _ = aData
        bQuest, bCurProg, bPrevProg, _, _ = bData
        res = cmp(aQuest.isCompleted(aCurProg), bQuest.isCompleted(bCurProg))
        if res:
            return -res
        if aQuest.isCompleted() and bQuest.isCompleted(bCurProg):
            res = aQuest.getBonusCount(aCurProg) - aPrevProg.get('bonusCount', 0) - (bQuest.getBonusCount(bCurProg) - bPrevProg.get('bonusCount', 0))
            if not res:
                return res
        return cmp(aQuest.getID(), bQuest.getID())


class DogTagsProgressBlock(base.StatsBlock):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def getVO(self):
        vo = super(DogTagsProgressBlock, self).getVO()
        return vo

    @staticmethod
    def createDogTagInfo(componentId, dogTagType):
        compGrade = BigWorld.player().dogTags.getComponentProgress(componentId).grade
        return {'title': DogTagsProgressBlock.__getInfoTitle(componentId, compGrade, dogTagType),
         'description': DogTagsProgressBlock.__getInfoDescription(componentId, dogTagType),
         'dogTagType': dogTagType,
         'componentId': componentId,
         'imageSrc': dogTagComposer.getComponentImage(componentId, compGrade),
         'unlockType': cca.getComponentById(componentId).viewType.value.lower()}

    @staticmethod
    def __getInfoTitle(componentId, grade, dogTagType):
        compTitle = dogTagComposer.getComponentTitle(componentId)
        viewType = cca.getComponentById(componentId).viewType.value.lower()
        strSource = R.strings.dogtags.postbattle.dyn(dogTagType).dyn(viewType).title()
        return backport.text(strSource).format(title=compTitle, level=grade + 1)

    @staticmethod
    def __getInfoDescription(componentId, dogTagType):
        viewType = cca.getComponentById(componentId).viewType.value.lower()
        strSource = R.strings.dogtags.postbattle.dyn(dogTagType).dyn(viewType).description()
        return backport.text(strSource)

    def setRecord(self, result, reusable):
        if not self.lobbyContext.getServerSettings().isDogTagInPostBattleEnabled():
            return
        dogTags = reusable.personal.getDogTagsProgress()
        for compId in dogTags.get('unlockedComps', []):
            info = self.createDogTagInfo(compId, 'unlock')
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for compId in dogTags.get('upgradedComps', []):
            info = self.createDogTagInfo(compId, 'upgrade')
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))


class ProgressiveRewardVO(base.StatsItem):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def _convert(self, record, reusable):
        progressiveReward = reusable.personal.getProgressiveReward()
        if progressiveReward is None:
            return
        else:
            progressiveConfig = self.lobbyContext.getServerSettings().getProgressiveRewardConfig()
            maxSteps = progressiveConfig.maxLevel
            hasCompleted, currentStep, probability = progressiveReward
            if currentStep >= maxSteps:
                _logger.warning('Current step more than max step in progressive reward')
                return
            if hasCompleted:
                currentStep = currentStep - 1 if currentStep else maxSteps - 1
            descText = text_styles.standard(backport.text(R.strings.battle_results.progressiveReward.descr()))
            return getProgressiveRewardVO(currentStep=currentStep, probability=probability, maxSteps=maxSteps, showBg=True, align=prConst.WIDGET_LAYOUT_H, isHighTitle=True, hasCompleted=hasCompleted, descText=descText)


class ProgressiveCustomizationVO(base.DirectStatsItem):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        questInfo = self._value.get('questInfo', {})
        questID = questInfo.get('questID', None)
        if questInfo and questID is not None:
            _, vehicleIntCD = parseEventID(questID)
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            linkBtnEnabled, linkBtnTooltip = getC11nProgressionLinkBtnParams(vehicle)
            self._value['linkBtnEnabled'] = linkBtnEnabled
            self._value['linkBtnTooltip'] = backport.text(linkBtnTooltip)
        return self._value


class QuestProgressiveCustomizationVO(base.DirectStatsItem):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        questInfo = self._value.get('questInfo', {})
        questID = questInfo.get('questID', None)
        if questInfo and questID is not None:
            linkBtnEnabled, linkBtnTooltip = getC11n2dProgressionLinkBtnParams()
            self._value['linkBtnEnabled'] = linkBtnEnabled
            self._value['linkBtnTooltip'] = backport.text(linkBtnTooltip)
        return self._value


class PrestigeProgressVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        prestigeResults = reusable.personal.getPrestigeResults()
        data = first(prestigeResults.items())
        if not data:
            return None
        else:
            vehCD, prestigeData = data
            if not hasVehiclePrestige(vehCD, checkElite=True):
                return None
            return None if not prestigeData or prestigeData['oldLevel'] <= 0 or prestigeData['newLevel'] <= 0 else self.createPrestigeInfo(vehCD, prestigeData)

    @classmethod
    def createPrestigeInfo(cls, vehCD, prestigeData):
        oldLvl = prestigeData['oldLevel']
        gainedPoints = prestigeData['gainedPoints']
        if getCurrentGrade(oldLvl, vehCD) == MAX_GRADE_ID or gainedPoints == 0:
            return None
        else:
            newLvl = prestigeData['newLevel']
            newPoints = prestigeData['newPoints']
            gradeType, grade = mapGradeIDToUI(getCurrentGrade(newLvl, vehCD))
            currentXP, nextLvlXP = getCurrentProgress(vehCD, newLvl, newPoints)
            gainedXP = prestigePointsToXP(gainedPoints)
            return {'vehCD': vehCD,
             'gradeType': gradeType.value,
             'grade': str(grade),
             'lvl': str(newLvl),
             'currentXP': currentXP,
             'nextLvlXP': nextLvlXP,
             'gainedXP': '+ {}'.format(backport.getIntegralFormat(gainedXP)),
             'isLvlUp': oldLvl < newLvl}
