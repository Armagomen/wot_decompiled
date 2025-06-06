# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_progressions_view.py
import logging
from functools import partial
from operator import itemgetter
import typing
from ClientSelectableCameraObject import ClientSelectableCameraObject
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_COLLECTION_SEEN, LAST_BATTLE_PASS_POINTS_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BATTLE_PASS_RANDOM_QUEST_BONUS_NAME, BATTLE_PASS_TICKETS_EVENT, BattlePassConsts, CurrencyBP, FinalReward
from frameworks.wulf import Array, ViewFlags, ViewSettings, ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl, getBattlePassTalerProductsUrl
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import changeBonusTooltipData, packBonusModelAndTooltipData, packSpecialTooltipData
from gui.battle_pass.battle_pass_constants import ChapterState, MIN_LEVEL
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import fillBattlePassCompoundPrice, getAllFinalRewards, getChapterType, getDataByTankman, getExtraInfoPageURL, getFinalTankmen, getInfoPageURL, getIntroVideoURL, getRewardSourceByType, getStyleForChapter, getVehicleInfoForChapter, isSeasonEndingSoon, isSeasonWithSpecialTankmenScreen, updateBuyAnimationFlag, getSingleVehicleForCustomization, getDefaultChaptersView
from gui.battle_pass.sounds import BattlePassSounds
from gui.collection.collections_helpers import loadCollectionsFromBattlePass
from gui.impl.auxiliary.collections_helper import fillCollectionModel
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_progressions_view_model import ActionTypes, BattlePassProgressionsViewModel, ChapterStates, ChapterType
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.utils import getVehicleForStyle
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattlePassBuyLevelWindow, showBattlePassBuyWindow, showBattlePassHowToEarnPointsView, showBattlePassStyleProgressionPreview, showBattlePassTankmenVoiceover, showBrowserOverlayView, showHangar, showShop, showStylePreview, showVehiclePreviewWithoutBottomPanel
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier, SimpleNotifier
from helpers import dependency, time_utils
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController, ICollectionsSystemController, ILootBoxSystemController, IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
from web.web_client_api.common import ItemPackEntry, ItemPackType
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.battle_pass.character_widget_view_model import CharacterWidgetViewModel
    from gui.impl.gen.view_models.views.lobby.battle_pass.style_info_model import StyleInfoModel
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)
_bpRes = R.strings.battle_pass
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}
_FREE_POINTS_INDEX = 0

class BattlePassProgressionsView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battlePass = dependency.descriptor(IBattlePassController)
    __gui = dependency.descriptor(IGuiLoader)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    ANIMATION_PURCHASE_LEVELS = 'animPurchaseLevels'
    ANIMATIONS = {ANIMATION_PURCHASE_LEVELS: False}
    __MINIMAL_TANKMEN_COUNT = 2

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassProgressionsView())
        settings.flags = ViewFlags.VIEW
        settings.model = BattlePassProgressionsViewModel()
        self.__tooltipItems = {}
        self.__specialTooltipItems = {}
        self.__viewActive = False
        self.__chapterID = kwargs.get('chapterID') or self.__getDefaultChapterID()
        self.__showReplaceRewardAnimations = False
        self.__notifier = None
        self.__exitSoundsIsPlayed = False
        super(BattlePassProgressionsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassProgressionsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassProgressionsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(BattlePassProgressionsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            tooltipData = self.__tooltipItems.get(tooltipId)
            return tooltipData if tooltipData is not None else self.__specialTooltipItems.get(tooltipId)

    def activate(self):
        self._subscribe()
        self.__updateProgressData()
        self.__updateActionType()
        self.__startSounds()

    def deactivate(self):
        if not self.__exitSoundsIsPlayed:
            self.__stopSounds()
            self.__startCommonSound()
        self._unsubscribe()

    def onViewSwitch(self):
        self.__startCommonSound()

    def setChapter(self, chapterID):
        if chapterID != self.__chapterID:
            self.deactivate()
            self.__chapterID = chapterID or self.__getDefaultChapterID()
            self.activate()

    def _getEvents(self):
        return ((self.viewModel.onActionClick, self.__onActionClick),
         (self.viewModel.onAboutClick, self.__onAboutClick),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.widget3dStyle.onPreviewClick, self.__onProgressiveStylePreview),
         (self.viewModel.widgetFinalRewards.onRewardPreviewClick, self.__onFinalRewardPreview),
         (self.viewModel.onTakeClick, self.__onTakeClick),
         (self.viewModel.onTakeAllClick, self.__onTakeAllClick),
         (self.viewModel.onOpenShopClick, self.__onOpenShopClick),
         (self.viewModel.onPointsInfoClick, self.__onPointsInfoClick),
         (self.viewModel.onFinishedAnimation, self.__resetReplaceRewardAnimations),
         (self.viewModel.onLevelsAnimationFinished, self.__resetLevelAnimations),
         (self.viewModel.onStyleBonusPreview, self.__onStyleBonusPreview),
         (self.viewModel.widgetFinalRewards.showTankmen, self.__showTankmen),
         (self.viewModel.onChapterChoice, self.__onChapterChoice),
         (self.viewModel.awardsWidget.onBpcoinClick, self.__showCoinsShop),
         (self.viewModel.awardsWidget.showTalers, self.__showPointsShop),
         (self.viewModel.awardsWidget.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.awardsWidget.showTankmen, self.__showTankmen),
         (self.viewModel.awardsWidget.collectionEntryPoint.openCollection, self.__openCollection),
         (self.viewModel.awardsWidget.showTickets, self.__showTickets),
         (self.__battlePass.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePass.onBattlePassIsBought, self.__onBattlePassBought),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChange),
         (self.__battlePass.onRewardSelectChange, self.__onRewardSelectChange),
         (self.__battlePass.onOffersUpdated, self.__onOffersUpdated),
         (self.__battlePass.onSelectTokenUpdated, self.__onSelectTokenUpdated),
         (self.__battlePass.onChapterChanged, self.__onChapterChanged),
         (self.__battlePass.onExtraChapterExpired, self.__onExtraChapterExpired),
         (self.__collectionsSystem.onBalanceUpdated, self.__onCollectionsUpdated),
         (self.__collectionsSystem.onServerSettingsChanged, self.__onCollectionsUpdated),
         (self.__lootBoxes.onStatusChanged, self.__onTicketsUpdated),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onTicketsUpdated),
         (self.__lootBoxes.onBoxesCountChanged, self.__onTicketsCountUpdated),
         (self.__wallet.onWalletStatusChanged, self.__updateWalletAvailability),
         (g_playerEvents.onClientUpdated, self.__onBPTalerUpdated))

    def _getListeners(self):
        return ((events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY),
         (events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),
         (events.BattlePassEvent.ON_PURCHASE_LEVELS, self.__onPurchaseLevels, EVENT_BUS_SCOPE.LOBBY),
         (events.BattlePassEvent.BUYING_THINGS, self.__updateActionType, EVENT_BUS_SCOPE.LOBBY),
         (events.CollectionsEvent.NEW_ITEM_SHOWN, self.__onCollectionsUpdated, EVENT_BUS_SCOPE.LOBBY))

    def _getCallbacks(self):
        return (('stats.bpcoin', self.__updateBalance),)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoading(*args, **kwargs)
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(PeriodicNotifier(self.__battlePass.getSeasonTimeLeft, self.__setExpirations))
        self.__notifier.addNotificator(SimpleNotifier(self.__battlePass.getFinalOfferTimeLeft, self.__updateActionType))
        self.__notifier.startNotification()
        self.__updateProgressData()
        self.__updateActionType()
        self.__startSounds()

    def _onLoaded(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoaded(*args, **kwargs)
        self.__setShowBuyAnimations()

    def _finalize(self):
        self.__tooltipItems = None
        self.__specialTooltipItems = None
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clearNotification()
        if not self.__exitSoundsIsPlayed:
            self.__stopSounds()
        super(BattlePassProgressionsView, self)._finalize()
        return

    def __onActionClick(self):
        self.__resetBuyAnimation()
        self.__stopVoiceovers()
        ctrl = self.__battlePass
        if ctrl.isChapterActive(self.__chapterID):
            if ctrl.isBought(chapterID=self.__chapterID):
                self.__showBuyLevelsWindow()
            else:
                self.__showBuyWindow()
        elif not ctrl.isChapterCompleted(self.__chapterID):
            ctrl.activateChapter(self.__chapterID)
        elif not ctrl.isBought(chapterID=self.__chapterID):
            self.__showBuyWindow()

    def __onAboutClick(self):
        self.__loadUrl(getExtraInfoPageURL() if self.__battlePass.isExtraChapter(self.__chapterID) else getInfoPageURL())

    @staticmethod
    def __onClose():
        showHangar()

    @staticmethod
    def __loadUrl(url):
        showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __setBattlePassIntroShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})

    @replaceNoneKwargsModel
    def __updateProgressData(self, model=None):
        self.__setAwards(model)
        self.__updateData(model=model)
        self.__updateBalance(model=model)
        self.__updateWalletAvailability(model=model)
        self.__updatePrice(model=model)

    def __setAwards(self, model):
        bpController = self.__battlePass
        self.__tooltipItems.clear()
        self.__specialTooltipItems.clear()
        self.__setFinalRewardsWidget(model)
        model.levels.clearItems()
        minLevel, maxLevel = bpController.getChapterLevelInterval(self.__chapterID)
        freeBonuses = sorted(bpController.getAwardsInterval(self.__chapterID, minLevel, maxLevel, BattlePassConsts.REWARD_FREE).iteritems(), key=itemgetter(0))
        paidBonuses = sorted(bpController.getAwardsInterval(self.__chapterID, minLevel, maxLevel, BattlePassConsts.REWARD_PAID).iteritems(), key=itemgetter(0))
        for (level, freeBonus), (_, paidBonus) in zip(freeBonuses, paidBonuses):
            isNeedToTakeFree, isChooseFreeRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_FREE, level)
            isNeedToTakePaid, isChoosePaidRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_PAID, level)
            levelModel = RewardLevelModel()
            levelModel.setLevel(level)
            levelModel.setIsRare(bpController.isRareLevel(self.__chapterID, level))
            levelModel.setIsFreeRewardChoiceEnabled(isChooseFreeRewardEnabled)
            levelModel.setIsPaidRewardChoiceEnabled(isChoosePaidRewardEnabled)
            levelModel.setLevelPoints(bpController.getLevelPoints(self.__chapterID, level - 1))
            levelModel.setNeedTakeFree(isNeedToTakeFree)
            levelModel.setNeedTakePaid(isNeedToTakePaid)
            realFreeAwards = self.__battlePass.replaceOfferByReward(freeBonus)
            packBonusModelAndTooltipData(realFreeAwards, levelModel.freeRewardItems, self.__tooltipItems)
            realPaidAwards = self.__battlePass.replaceOfferByReward(paidBonus)
            packBonusModelAndTooltipData(realPaidAwards, levelModel.paidRewardItems, self.__tooltipItems)
            model.levels.addViewModel(levelModel)

    def __setProgressiveStyleWidget(self, model):
        style = getStyleForChapter(self.__chapterID)
        if style is not None:
            vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
            vehicle = getVehicleByIntCD(vehicleCD)
            fillVehicleInfo(model.widget3dStyle.vehicleInfo, vehicle)
            model.widget3dStyle.setStyleName(style.userName)
            model.widget3dStyle.setStyleId(style.id)
            self.__setStyleTaken(model=model)
        return

    def __setCharacterWidget(self, model, rewardSource=BattlePassConsts.REWARD_FREE):
        if rewardSource in (BattlePassConsts.REWARD_BOTH, BattlePassConsts.REWARD_FREE):
            character = self.__getFinalTankman(BattlePassConsts.REWARD_FREE)
            if character is not None:
                self.__setCharacterModel(model.free, character)
        if rewardSource in (BattlePassConsts.REWARD_BOTH, BattlePassConsts.REWARD_PAID):
            character = self.__getFinalTankman(BattlePassConsts.REWARD_PAID)
            if character is not None:
                self.__setCharacterModel(model.paid, character)
        return

    def __setStyleWidget(self, model, style):
        model.setStyleName(style.userName)
        model.setStyleId(style.id)
        vehicleCD = getSingleVehicleForCustomization(style)
        if vehicleCD is not None:
            vehicle = getVehicleByIntCD(vehicleCD)
            if vehicle is not None:
                fillVehicleInfo(model.vehicleInfo, vehicle)
                model.setIsVehicleInHangar(vehicle.isInInventory)
        return

    def __setCharacterModel(self, model, character):
        iconName, characterName, skills, groupName = getDataByTankman(character)
        skillsArray = Array()
        for skill in skills:
            skillsArray.addString(skill)

        model.setIcon(iconName)
        model.setTankman(characterName)
        model.setSkills(skillsArray)
        model.setTooltipId(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED)
        model.setGroupName(groupName)
        model.setHasVoice(self.__battlePass.isVoicedTankman(groupName))
        packSpecialTooltipData(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, self.__specialTooltipItems, character.getRecruitID())

    def __setFinalRewardsWidget(self, model):
        if not self.__battlePass.getRewardTypes(self.__chapterID):
            _logger.error('Cannot find rewards for widget in progression for chapter=%s', self.__chapterID)
            return
        elif getRewardSourceByType(FinalReward.PROGRESSIVE_STYLE, self.__chapterID) == BattlePassConsts.REWARD_FREE:
            self.__setProgressiveStyleWidget(model)
            return
        else:
            maxLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            style = getStyleForChapter(self.__chapterID)
            if style is not None:
                self.__setStyleWidget(model.widgetFinalRewards.styleInfo, style)
            vehicleSource = getRewardSourceByType(FinalReward.VEHICLE, self.__chapterID)
            if vehicleSource is not None:
                vehicle, _ = getVehicleInfoForChapter(self.__chapterID, awardSource=vehicleSource)
                if vehicle is not None:
                    fillVehicleInfo(model.widgetFinalRewards.vehicleInfo, vehicle)
            tankmanSource = getRewardSourceByType(FinalReward.TANKMAN, self.__chapterID)
            if tankmanSource is not None:
                self.__setCharacterWidget(model.widgetFinalRewards.tankmanInfo, rewardSource=tankmanSource)
            questSource = getRewardSourceByType(FinalReward.BATTLE_QUEST, self.__chapterID)
            if questSource is not None:
                rewards = self.__battlePass.getSingleAward(self.__chapterID, maxLevel, questSource)
                battleQuestReward = findFirst(lambda b: b.getName() == BATTLE_PASS_RANDOM_QUEST_BONUS_NAME, rewards)
                if battleQuestReward is not None:
                    model.widgetFinalRewards.setBattleQuest(battleQuestReward.tokenID)
            return

    def __resetRewardsInterval(self, model, fromLevel, toLevel, replaceRewards=False):
        startLevel, finalLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        if fromLevel == toLevel:
            return
        fromLevel += 1
        if toLevel > finalLevel:
            toLevel = finalLevel
        for level in range(fromLevel, toLevel + 1):
            levelData = model.levels.getItem(level - startLevel)
            isNeedToTakeFree, isChooseFreeRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_FREE, level)
            if replaceRewards and levelData.getNeedTakeFree() and not isNeedToTakeFree:
                levelData.freeRewardItems.clearItems()
                awards = self.__battlePass.getSingleAward(self.__chapterID, level, BattlePassConsts.REWARD_FREE)
                realAwards = self.__battlePass.replaceOfferByReward(awards)
                packBonusModelAndTooltipData(realAwards, levelData.freeRewardItems, self.__tooltipItems)
                self.__showReplaceRewardAnimations = True
            isNeedToTakePaid, isChoosePaidRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_PAID, level)
            if replaceRewards and levelData.getNeedTakePaid() and not isNeedToTakePaid:
                levelData.paidRewardItems.clearItems()
                awards = self.__battlePass.getSingleAward(self.__chapterID, level, BattlePassConsts.REWARD_PAID)
                realAwards = self.__battlePass.replaceOfferByReward(awards)
                packBonusModelAndTooltipData(realAwards, levelData.paidRewardItems, self.__tooltipItems)
                self.__showReplaceRewardAnimations = True
            levelData.setNeedTakeFree(isNeedToTakeFree)
            levelData.setNeedTakePaid(isNeedToTakePaid)
            levelData.setIsFreeRewardChoiceEnabled(isChooseFreeRewardEnabled)
            levelData.setIsPaidRewardChoiceEnabled(isChoosePaidRewardEnabled)

        model.setShowReplaceRewardsAnimations(self.__showReplaceRewardAnimations)
        model.levels.invalidate()

    def __getRewardLevelState(self, awardType, level):
        bpController = self.__battlePass
        isNeedToTake = bpController.isNeedToTakeReward(self.__chapterID, awardType, level)
        isChooseRewardEnabled = isNeedToTake and bpController.isChooseRewardEnabled(awardType, self.__chapterID, level)
        return (isNeedToTake, isChooseRewardEnabled)

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        self.__updateLevelState(model)
        isBattlePassBought = self.__battlePass.isBought(chapterID=self.__chapterID)
        model.setIsBattlePassPurchased(isBattlePassBought)
        model.setIsPaused(self.__battlePass.isPaused())
        model.setChapterState(_CHAPTER_STATES.get(self.__battlePass.getChapterState(self.__chapterID)))
        self.__setRewardTypes(model)
        model.setChapterID(self.__chapterID)
        model.setSeasonNum(self.__battlePass.getSeasonNum())
        model.setChapterType(ChapterType(getChapterType(self.__chapterID)))
        model.setIsSeasonEndingSoon(isSeasonEndingSoon())
        model.setHasExtra(self.__battlePass.hasExtra())
        model.setIsSpecialTankmenEnabled(self.__isSpecialVoiceTankmenEnabled())
        model.awardsWidget.setIsTalerEnabled(not self.__battlePass.isHoliday())
        model.awardsWidget.setIsBpCoinEnabled(not self.__battlePass.isHoliday())
        model.awardsWidget.setTalerCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.TALER.value, 0))
        model.awardsWidget.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.awardsWidget.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())
        model.awardsWidget.setIsSpecialVoiceTankmenEnabled(self.__isSpecialVoiceTankmenEnabled())
        fillCollectionModel(model.awardsWidget.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())
        self.__onTicketsUpdated()
        self.__onTicketsCountUpdated()
        self.__setExpirations(model=model)
        self.__setFinalRewardsWidget(model)
        self.__updateRewardSelectButton(model=model)

    @replaceNoneKwargsModel
    def __setExpirations(self, model=None):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            endTimestamp = self.__battlePass.getChapterExpiration(self.__chapterID)
            timeLeft = self.__battlePass.getChapterRemainingTime(self.__chapterID)
        else:
            endTimestamp = self.__battlePass.getSeasonFinishTime()
            timeLeft = self.__battlePass.getSeasonTimeLeft()
        model.setExpireTime(time_utils.makeLocalServerTime(endTimestamp))
        model.setTimeLeft(timeLeft)

    def __setStyleTaken(self, model):
        style = getStyleForChapter(self.__chapterID)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        model.setIsStyleTaken(style.isInInventory or bool(style.installedCount(vehicle.intCD)))

    def __updateLevelState(self, model):
        previousBattlePassPointsSeen = AccountSettings.getSettings(LAST_BATTLE_PASS_POINTS_SEEN)
        previousChapterPoints = previousBattlePassPointsSeen.get(self.__chapterID, 0)
        previousFreePoints = previousBattlePassPointsSeen.get(_FREE_POINTS_INDEX, 0)
        currentChapterPoints = self.__battlePass.getPointsInChapter(self.__chapterID)
        previousLevel = self.__battlePass.getLevelByPoints(self.__chapterID, previousChapterPoints)
        previousPoints, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, previousChapterPoints, previousLevel)
        previousLevel += 1
        currentLevel = self.__battlePass.getLevelByPoints(self.__chapterID, currentChapterPoints)
        currentPoints, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, currentChapterPoints, currentLevel)
        currentLevel += 1
        finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
        currentLevel = currentLevel if currentLevel <= finalLevel else finalLevel
        freePointsInChapter = self.__battlePass.getFreePoints() + currentChapterPoints
        potentialLevel = self.__battlePass.getLevelByPoints(self.__chapterID, freePointsInChapter)
        freePointsInLevel, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, freePointsInChapter, potentialLevel)
        potentialLevel += 1
        previousPotentialLevel = self.__battlePass.getLevelByPoints(self.__chapterID, previousFreePoints)
        previousFreePointsInLevel, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, previousFreePoints, previousPotentialLevel)
        previousPotentialLevel += 1
        if self.__battlePass.isExtraChapter(self.__chapterID):
            freePointsInChapter = 0
            freePointsInLevel = 0
            potentialLevel = 0
            previousFreePoints = 0
            previousFreePointsInLevel = 0
            previousPotentialLevel = 0
        model.setPreviousPointsInChapter(previousChapterPoints)
        model.setPreviousPointsInLevel(previousPoints)
        model.setPreviousLevel(previousLevel)
        model.setCurrentPointsInChapter(currentChapterPoints)
        model.setCurrentPointsInLevel(currentPoints)
        model.setCurrentLevel(currentLevel)
        model.setFreePointsInChapter(freePointsInChapter)
        model.setFreePointsInLevel(freePointsInLevel)
        model.setPreviousFreePointsInChapter(previousFreePoints)
        model.setPreviousFreePointsInLevel(previousFreePointsInLevel)
        model.setPreviousPotentialLevel(previousPotentialLevel)
        model.setPotentialLevel(potentialLevel)
        previousBattlePassPointsSeen[self.__chapterID] = currentChapterPoints
        previousBattlePassPointsSeen[_FREE_POINTS_INDEX] = freePointsInChapter
        AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, previousBattlePassPointsSeen)

    def __updateActionType(self, *_):
        bpController = self.__battlePass
        isBattlePassBought = bpController.isBought(chapterID=self.__chapterID)
        isActiveChapter = bpController.isChapterActive(self.__chapterID)
        isCompleted = bpController.isChapterCompleted(self.__chapterID)
        state = ActionTypes.NOACTION
        if isActiveChapter:
            state = ActionTypes.BUY if not isBattlePassBought else ActionTypes.BUYLEVEL
        elif not isCompleted:
            state = ActionTypes.ACTIVATECHAPTER
        elif not isBattlePassBought:
            state = ActionTypes.BUY
        with self.viewModel.transaction() as model:
            model.setActionType(state)

    @replaceNoneKwargsModel
    def __updateRewardSelectButton(self, model=None):
        model.setIsChooseDeviceEnabled(False)
        notChosenRewardCount = self.__battlePass.getNotChosenRewardCount()
        model.setIsChooseDeviceEnabled(self.__battlePass.canChooseAnyReward())
        model.awardsWidget.setNotChosenRewardCount(notChosenRewardCount)

    @replaceNoneKwargsModel
    def __updateRewardSelectButtons(self, model=None):
        self.__resetRewardSelectButtons(model, MIN_LEVEL)

    def __resetRewardSelectButtons(self, model, fromLevel):
        startLevel, finalLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        if fromLevel <= startLevel:
            fromLevel = startLevel + 1
        for level in range(fromLevel, finalLevel + 1):
            item = model.levels.getItem(level - startLevel)
            _, isChooseFreeRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_FREE, level)
            _, isChoosePaidRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_PAID, level)
            item.setIsFreeRewardChoiceEnabled(isChooseFreeRewardEnabled)
            item.setIsPaidRewardChoiceEnabled(isChoosePaidRewardEnabled)

        model.levels.invalidate()

    def __onMissionsTabChanged(self, event):
        viewActive = event.ctx.get('alias') == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS
        if self.__viewActive == viewActive and self.__viewActive:
            self.__clearSubViews()
        self.__viewActive = viewActive

    def __clearSubViews(self):

        def __isValidSubView(v):
            return v.viewFlags & ViewFlags.VIEW_TYPE_MASK == ViewFlags.LOBBY_TOP_SUB_VIEW and v.viewStatus in (ViewStatus.LOADED, ViewStatus.LOADING)

        for view in self.__gui.windowsManager.findViews(__isValidSubView):
            view.destroyWindow()

    def __onAwardViewClose(self, *_):
        self.__setShowBuyAnimations()

    def __onBattlePassSettingsChange(self, *_):
        if not self.__battlePass.isChapterExists(self.__chapterID):
            showMissionsBattlePass(getDefaultChaptersView(battlePass=self.__battlePass))
            return
        if self.__battlePass.isPaused():
            showMissionsBattlePass()
            return
        if not (self.__battlePass.isEnabled() and self.__battlePass.isActive()):
            showHangar()
            return
        self.__updateProgressData()
        self.__updateActionType()

    def __onGoToChapter(self, args):
        chapter = args.get('chapterNumber')
        if chapter is None:
            return
        else:
            self.__chapterID = int(chapter)
            self.__updateProgressData()
            self.__updateActionType()
            return

    def __onProgressiveStylePreview(self, args):
        level = args.get('level')
        if level is None:
            return
        else:
            styleInfo = getStyleForChapter(self.__chapterID, battlePass=self.__battlePass)
            vehicleCD = getVehicleCDForStyle(styleInfo, itemsCache=self.__itemsCache)
            self.__switchCamera()
            showBattlePassStyleProgressionPreview(vehicleCD, styleInfo, styleInfo.getDescription(), self.__getPreviewCallback(), chapterId=self.__chapterID, styleLevel=int(level))
            return

    def __onFinalRewardPreview(self):
        self.__switchCamera()
        allRewardTypes = getAllFinalRewards(self.__chapterID, battlePass=self.__battlePass)
        if FinalReward.VEHICLE in allRewardTypes:
            self.__showVehiclePreview()
        elif FinalReward.STYLE in allRewardTypes:
            self.__showStylePreview()

    def __showVehiclePreview(self):
        vehicle, style = getVehicleInfoForChapter(self.__chapterID, awardSource=BattlePassConsts.REWARD_BOTH)
        styleInfo = getStyleForChapter(self.__chapterID, battlePass=self.__battlePass)
        if styleInfo is not None:
            showStylePreview(vehicle.intCD, style=styleInfo, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
             'tabIDs': (TabID.VEHICLE, TabID.STYLE),
             'currentTabID': TabID.STYLE,
             'style': styleInfo}, itemsPack=self.__getPreviewItemPack(), backCallback=self.__getPreviewCallback())
        else:
            showVehiclePreviewWithoutBottomPanel(vehicle.intCD, backCallback=self.__getPreviewCallback(), itemsPack=self.__getPreviewItemPack(), style=style)
        return

    def __showStylePreview(self):
        style = getStyleForChapter(self.__chapterID, battlePass=self.__battlePass)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        showStylePreview(vehicleCD, style=style, itemsPack=self.__getPreviewItemPack(), backCallback=self.__getPreviewCallback())

    def __getPreviewItemPack(self):
        return (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),)

    def __getPreviewCallback(self):
        return partial(showMissionsBattlePass, R.views.lobby.battle_pass.BattlePassProgressionsView(), self.__chapterID)

    def __onPointsUpdated(self):
        with self.viewModel.transaction() as model:
            newChapter = self.__battlePass.getCurrentChapterID()
            newPoints = self.__battlePass.getPointsInChapter(self.__chapterID)
            newFreePoints = self.__battlePass.getFreePoints() + newPoints
            oldFreePoints = model.getFreePointsInChapter()
            if model.getChapterID() != newChapter and newFreePoints == oldFreePoints:
                return
            oldPoints = model.getCurrentPointsInChapter()
            oldLevel = self.__battlePass.getLevelByPoints(self.__chapterID, oldPoints)
            newLevel = self.__battlePass.getLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, oldLevel, newLevel)
            self.__updateData(model=model)
        isDrawPoints = newLevel < oldLevel or newPoints < oldPoints or newFreePoints > oldFreePoints
        if isDrawPoints:
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.__updateActionType()

    def __updateTooltipsSingleCard(self, rewards, model):
        tooltipIds = [ item.getTooltipId() for item in model.rewardItems.getItems() ]
        tooltipIds = tooltipIds[:len(rewards)]
        changeBonusTooltipData(zip(rewards, tooltipIds), self.__tooltipItems)

    def __onBattlePassBought(self):
        with self.viewModel.transaction() as model:
            finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, MIN_LEVEL, finalLevel)
            self.__updateData(model=model)
        self.__updateActionType()

    def __onRewardSelectChange(self):
        self.__updateRewardSelectButton()
        with self.viewModel.transaction() as model:
            self.__setFinalRewardsWidget(model)
            finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, MIN_LEVEL, finalLevel, replaceRewards=True)

    def __onSelectTokenUpdated(self):

        def __viewsPredicate(view):
            return view.layoutID in (R.views.lobby.battle_pass.BattlePassAwardsView(), R.views.lobby.battle_pass.RewardsSelectionView())

        if self.__gui.windowsManager.findViews(__viewsPredicate):
            return
        self.__updateRewardSelectButton()
        with self.viewModel.transaction() as model:
            self.__setFinalRewardsWidget(model)
            model.awardsWidget.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
            model.awardsWidget.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())
            finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, MIN_LEVEL, finalLevel, replaceRewards=False)

    def __onChapterChanged(self):
        if self.__chapterID not in self.__battlePass.getMainChapterIDs():
            return
        self.__updateActionType()
        self.__updateProgressData()

    def __onExtraChapterExpired(self):
        showMissionsBattlePass(getDefaultChaptersView(battlePass=self.__battlePass))

    @replaceNoneKwargsModel
    def __onOffersUpdated(self, model=None):
        self.__updateRewardSelectButton(model=model)
        self.__updateRewardSelectButtons(model=model)

    def __onPurchaseLevels(self, _):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = True

    @replaceNoneKwargsModel
    def __setShowBuyAnimations(self, model=None):
        showAnimations = False
        isBattlePassBought = self.__battlePass.isBought(chapterID=self.__chapterID)
        if isBattlePassBought:
            showAnimations = updateBuyAnimationFlag(chapterID=self.__chapterID, settingsCore=self.__settingsCore, battlePass=self.__battlePass)
            model.setIsBattlePassPurchased(isBattlePassBought)
        model.setShowBuyAnimations(showAnimations)
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = False

    def __getDefaultChapterID(self):
        return self.__battlePass.getCurrentChapterID() or first(sorted(self.__battlePass.getMainChapterIDs()))

    def __showIntroVideo(self, onStart=False):
        settings = self.__settingsCore.serverSettings
        if onStart:
            if settings.getBPStorage().get(BattlePassStorageKeys.INTRO_VIDEO_SHOWN):
                return False
            settings.saveInBPStorage({BattlePassStorageKeys.INTRO_VIDEO_SHOWN: True})
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)
        return True

    def __showBuyWindow(self, backCallback=None):
        showBattlePassBuyWindow({'backCallback': backCallback})

    def __showBuyLevelsWindow(self, backCallback=None):
        showBattlePassBuyLevelWindow({'backCallback': backCallback,
         'chapterID': self.__chapterID})

    def __onTakeClick(self, args):
        level = args.get('level')
        if not level:
            return
        self.__battlePass.takeRewardForLevel(self.__chapterID, level)

    def __onTakeAllClick(self):
        self.__battlePass.takeAllRewards()

    @staticmethod
    def __onOpenShopClick():
        showShop(getBattlePassCoinProductsUrl())

    def __onPointsInfoClick(self):
        showBattlePassHowToEarnPointsView(parent=self.getParentWindow(), chapterID=self.__chapterID)

    @staticmethod
    def __onChapterChoice():
        showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())

    @replaceNoneKwargsModel
    def __updateWalletAvailability(self, status=None, model=None):
        model.setIsWalletAvailable(self.__wallet.isAvailable)

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.awardsWidget.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __updatePrice(self, model=None):
        compoundPrice = self.__battlePass.getBattlePassCost(self.__chapterID)
        fillBattlePassCompoundPrice(model.price, compoundPrice)

    @replaceNoneKwargsModel
    def __resetReplaceRewardAnimations(self, model=None):
        self.__showReplaceRewardAnimations = False
        model.setShowReplaceRewardsAnimations(self.__showReplaceRewardAnimations)

    @replaceNoneKwargsModel
    def __resetLevelAnimations(self, model=None):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = False
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])

    @replaceNoneKwargsModel
    def __resetBuyAnimation(self, model=None):
        model.setShowBuyAnimations(False)
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])

    def __onBPTalerUpdated(self, *data):
        if data[0].get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.TALER.value, ''):
            with self.viewModel.awardsWidget.transaction() as model:
                model.setTalerCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.TALER.value, 0))

    def __takeAllRewards(self):
        self.__battlePass.takeAllRewards()

    def __openCollection(self):
        if not AccountSettings.getSettings(IS_BATTLE_PASS_COLLECTION_SEEN):
            AccountSettings.setSettings(IS_BATTLE_PASS_COLLECTION_SEEN, True)
            self.__onCollectionsUpdated()
        loadCollectionsFromBattlePass(self.layoutID, self.__chapterID, battlePass=self.__battlePass)

    @staticmethod
    def __showCoinsShop():
        showShop(getBattlePassCoinProductsUrl())

    @staticmethod
    def __showPointsShop():
        showShop(getBattlePassTalerProductsUrl())

    def __onCollectionsUpdated(self, *_):
        with self.viewModel.awardsWidget.transaction() as model:
            fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    def __showTankmen(self):
        self.__stopVoiceovers()
        showBattlePassTankmenVoiceover()

    def __stopSounds(self):
        self.__stopVoiceovers()
        if self.__battlePass.isExtraChapter(self.__chapterID):
            self.soundManager.playInstantSound(BattlePassSounds.SPECIAL_TASKS_EXIT)
        self.__exitSoundsIsPlayed = True

    def __startSounds(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            self.soundManager.playInstantSound(BattlePassSounds.TASKS_EXIT)
            self.soundManager.playInstantSound(BattlePassSounds.SPECIAL_TASKS_ENTER)
        self.__exitSoundsIsPlayed = False

    def __startCommonSound(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            self.soundManager.playInstantSound(BattlePassSounds.TASKS_ENTER)

    def __stopVoiceovers(self):
        if self.__battlePass.getSpecialTankmen():
            if self.__battlePass.isHoliday():
                voiceoverStopSound = BattlePassSounds.HOLIDAY_VOICEOVER_STOP
            elif self.__battlePass.isExtraChapter(self.__chapterID):
                voiceoverStopSound = BattlePassSounds.VOICEOVER_STOP
            else:
                voiceoverStopSound = BattlePassSounds.REGULAR_VOICEOVER_STOP
            self.soundManager.playInstantSound(voiceoverStopSound)

    def __isSpecialVoiceTankmenEnabled(self):
        if not isSeasonWithSpecialTankmenScreen():
            return False
        specialVoiceChapters = self.__battlePass.getSpecialVoiceChapters()
        return self.__battlePass.isExtraChapter(self.__chapterID) and self.__chapterID in specialVoiceChapters or any((not self.__battlePass.isExtraChapter(chapterID) for chapterID in specialVoiceChapters))

    def __setRewardTypes(self, model):
        freeArray = model.getFreeFinalRewards()
        freeArray.clear()
        for freeReward in self.__battlePass.getFreeFinalRewardTypes(self.__chapterID):
            freeArray.addString(freeReward)

        freeArray.invalidate()
        paidArray = model.getPaidFinalRewards()
        paidArray.clear()
        for paidReward in self.__battlePass.getPaidFinalRewardTypes(self.__chapterID):
            paidArray.addString(paidReward)

        paidArray.invalidate()

    def __getFinalTankman(self, awardType):
        finalTankmen = getFinalTankmen(self.__chapterID, awardType, battlePass=self.__battlePass)
        return first(finalTankmen)

    @staticmethod
    def __switchCamera():
        ClientSelectableCameraObject.switchCamera()

    def __showTickets(self):
        showHangar()
        Views.load(ViewID.MAIN, eventName=BATTLE_PASS_TICKETS_EVENT, backCallback=partial(showMissionsBattlePass, R.views.lobby.battle_pass.BattlePassProgressionsView(), self.__chapterID))

    def __onTicketsUpdated(self):
        self.viewModel.awardsWidget.setIsTicketsEnabled(self.__lootBoxes.isLootBoxesAvailable and BATTLE_PASS_TICKETS_EVENT in self.__lootBoxes.getActiveEvents() and bool(self.__lootBoxes.getActiveBoxes(BATTLE_PASS_TICKETS_EVENT)))

    def __onTicketsCountUpdated(self):
        self.viewModel.awardsWidget.setTicketsCount(self.__lootBoxes.getBoxesCount(BATTLE_PASS_TICKETS_EVENT))

    @args2params(int)
    def __onStyleBonusPreview(self, bonusId):
        style = self.__itemsCache.items.getItemByCD(bonusId)
        vehicle = getVehicleForStyle(style)
        self.__switchCamera()
        showStylePreview(vehicle.intCD, style=style, backCallback=self.__getPreviewCallback())
