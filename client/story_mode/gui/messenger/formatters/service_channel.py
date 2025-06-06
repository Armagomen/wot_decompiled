# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/messenger/formatters/service_channel.py
from adisp import adisp_async, adisp_process
from constants import SCENARIO_RESULT
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import getItemTypeID
from gui.shared.gui_items.Vehicle import getUserName
from helpers import time_utils, dependency
from items import vehicles as vehicles_core
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.shared import IItemsCache
from story_mode_common.story_mode_constants import FIRST_MISSION_ID
from story_mode.gui.shared.utils import getRewardList, getTasksCount
from story_mode.skeletons.story_mode_controller import IStoryModeController
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattlePassController

class StoryModeResultsFormatter(BattleResultsFormatter):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _battleResultsService = dependency.descriptor(IBattleResultsService)
    _customizationService = dependency.descriptor(ICustomizationService)
    _battlePass = dependency.descriptor(IBattlePassController)
    _itemsCache = dependency.descriptor(IItemsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isForceOnboarding = message.data.get('isForceOnboarding', False)
        if isForceOnboarding:
            callback([])
        else:
            messages = yield super(StoryModeResultsFormatter, self).format(message)
            callback(messages)

    def _prepareFormatData(self, message):
        missionId = message.data.get('missionId', FIRST_MISSION_ID)
        isOnboarding = self._storyModeCtrl.missions.isOnboarding(missionId)
        if isOnboarding:
            self._battleResultKeys = {SCENARIO_RESULT.LOSE: 'storyModeOnboardingBattleDefeatResult',
             SCENARIO_RESULT.PARTIAL: 'storyModeOnboardingBattleDefeatResult',
             SCENARIO_RESULT.WIN: 'storyModeOnboardingBattleVictoryResult'}
        else:
            self._battleResultKeys = {SCENARIO_RESULT.LOSE: 'storyModeRegularBattleDefeatResult',
             SCENARIO_RESULT.PARTIAL: 'storyModeRegularBattleDefeatResult',
             SCENARIO_RESULT.WIN: 'storyModeRegularBattleVictoryResult'}
        templateName, ctx = super(StoryModeResultsFormatter, self)._prepareFormatData(message)
        ctx['scenarioName'] = backport.text(R.strings.sm_battle.prebattle.mission.title.num(missionId)())
        if isOnboarding:
            return (templateName, ctx)
        ctx['missionsStr'] = ''
        ctx['xpStr'] = ''
        ctx['bpPointsStr'] = ''
        ctx['crystalStr'] = ''
        ctx['creditsStr'] = ''
        ctx['rewardsStr'] = ''
        progressionInfo = message.data.get('progressionInfo', {})
        rewardList = getRewardList(progressionInfo, self._battlePass.isActive())
        completedTasksCount, tasksToCompleteCount = getTasksCount(progressionInfo)
        if tasksToCompleteCount:
            ctx['missionsStr'] = g_settings.htmlTemplates.format('missionCompleted', {'completedTasksCount': completedTasksCount,
             'tasksToCompleteCount': tasksToCompleteCount})
        freeXP = 0
        credits = 0
        bpPoints = 0
        crystal = 0
        customizations = []
        premium = 0
        items = {}
        vehicles = []
        slots = 0
        for reward in rewardList:
            credits += reward.get('credits', 0)
            freeXP += reward.get('freeXP', 0)
            bpPoints += sum((points for points in reward.get('battlePassPoints', {}).get('vehicles', {}).itervalues()))
            crystal += reward.get('crystal', 0)
            customizations += reward.get('customizations', [])
            premium += reward.get('premium_plus', 0)
            slots += reward.get('slots', 0)
            if 'items' in reward:
                for itemKey, amount in reward['items'].iteritems():
                    items[itemKey] = items.get(itemKey, 0) + amount

            vehicles += reward.get('vehicles', [])

        if freeXP:
            ctx['xpStr'] = g_settings.htmlTemplates.format('xpEarned', {'freeXP': freeXP})
        if bpPoints:
            ctx['bpPointsStr'] = g_settings.htmlTemplates.format('bpPointsEarned', {'bpPoints': bpPoints})
        if crystal:
            ctx['crystalStr'] = g_settings.htmlTemplates.format('crystalEarned', {'crystal': crystal})
        if credits:
            ctx['creditsStr'] = g_settings.htmlTemplates.format('creditEarned', {'credits': credits})
        haveRewardsStr = bool(premium or vehicles or items or customizations)
        if haveRewardsStr:
            rewardsStr = g_settings.htmlTemplates.format('rewardsStr', {'rewardsStr': backport.text(R.strings.sm_messenger.result.reward()) + '<br/>'})
            if premium:
                rewardsStr += g_settings.htmlTemplates.format('premiumEarned', {'premium_plus': premium})
            commaItems = []
            if vehicles:
                commaItems += [ getUserName(vehicles_core.getVehicleType(vehicle)) for vehicle in vehicles ]
            if slots:
                commaItems.append(backport.text(R.strings.sm_messenger.result.slots()) + '&nbsp;(x' + str(slots) + ')')
            if items:
                for itemKey in sorted(items.iterkeys(), reverse=True):
                    item = self._itemsCache.items.getItemByCD(itemKey)
                    commaItems.append(item.userName + '&nbsp;(x' + str(items[itemKey]) + ')')

            if customizations:
                for customization in customizations:
                    itemTypeID = getItemTypeID(customization['custType'])
                    if itemTypeID:
                        style = self._customizationService.getItemByID(itemTypeID, customization['id'])
                        commaItems.append(style.userName + '&nbsp;(x' + str(customization['value']) + ')')

            if commaItems:
                if premium:
                    rewardsStr += '<br/>'
                rewardsStr += g_settings.htmlTemplates.format('commaItems', {'items': ', '.join(commaItems)})
            ctx['rewardsStr'] = rewardsStr
        return (templateName, ctx)


class StoryModeAwardFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'storyModeAwardMessage'

    def format(self, message, *args):
        medal = message.data.get('medalName')
        badge = message.data.get('badgeId')
        medalAward = backport.text(R.strings.sm_messenger.medal.medalName(), medal_name=backport.text(R.strings.achievements.dyn(medal)())) if medal else None
        badgeAward = backport.text(R.strings.sm_messenger.medal.badgeName(), badge_name=backport.text(R.strings.badge.dyn('badge_' + str(badge))())) if badge else None
        if medalAward and badgeAward:
            award = backport.text(R.strings.sm_messenger.medal.badgeAndMedal(), medal=medalAward, badge=badgeAward)
        elif medalAward:
            award = medalAward
        else:
            award = badgeAward
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'at': TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)),
         'award': award})
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]
