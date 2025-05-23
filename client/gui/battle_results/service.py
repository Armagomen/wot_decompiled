# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/service.py
import logging
import typing
import BigWorld
import Event
from Account import PlayerAccount
from adisp import adisp_async, adisp_process
from constants import ARENA_BONUS_TYPE, PREMIUM_TYPE, PlayerSatisfactionRating
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui import SystemMessages
from gui.battle_results import context, emblems, reusable, stored_sorting
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.composer import RegularStatsComposer
from gui.battle_results.presenters.base_presenter import BaseStatsPresenter
from gui.battle_results.settings import PREMIUM_STATE
from gui.shared import event_dispatcher, events, g_eventBus
from gui.shared.gui_items.processors.common import BattleResultsGetter, PremiumBonusApplier
from gui.shared.gui_items.processors.player_satisfaction_rating import PlayerSatisfactionRatingProcessor
from gui.shared.system_factory import collectBattleResultStatsCtrl
from gui.shared.utils import decorators
from helpers import dependency
from helpers.func_utils import isDeveloperFunc
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl
_logger = logging.getLogger(__name__)

def createStatsCtrl(reusableInfo):
    bonusType = reusableInfo.common.arenaBonusType
    statsCtrl = collectBattleResultStatsCtrl(bonusType)
    if statsCtrl is None:
        statsCtrl = RegularStatsComposer
    return statsCtrl(reusableInfo)


class BattleResultsService(IBattleResultsService):
    battleMatters = dependency.descriptor(IBattleMattersController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    wotPlusController = dependency.descriptor(IWotPlusController)
    __slots__ = ('__battleResults', '__statsCtrls', '__buy', '__eventsManager', 'onResultPosted', '__appliedAddXPBonus', '__playerSatisfactionRatings')

    def __init__(self):
        super(BattleResultsService, self).__init__()
        self.__statsCtrls = {}
        self.__buy = set()
        self.__appliedAddXPBonus = set()
        self.__eventsManager = Event.EventManager()
        self.__playerSatisfactionRatings = dict()
        self.onResultPosted = Event.Event(self.__eventsManager)

    def init(self):
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyViewLoaded)
        g_eventBus.addListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)

    def fini(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyViewLoaded)
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)
        self.clear()

    def clear(self):
        while self.__statsCtrls:
            _, item = self.__statsCtrls.popitem()
            item.clear()

        self.__eventsManager.clear()

    @adisp_async
    @adisp_process
    def requestResults(self, ctx, callback=None):
        arenaUniqueID = ctx.getArenaUniqueID()
        if ctx.needToShowImmediately():
            event_dispatcher.showBattleResultsWindow(arenaUniqueID)
        if not ctx.resetCache() and arenaUniqueID in self.__statsCtrls:
            isSuccess = True

            def dummy(callback=None):
                if callback is not None:
                    callback(None)
                return

            yield dummy
            self.__notifyBattleResultsPosted(arenaUniqueID, needToShowUI=ctx.needToShowIfPosted())
        else:
            results = yield BattleResultsGetter(arenaUniqueID).request()
            if not results.success and ctx.getArenaBonusType() in (ARENA_BONUS_TYPE.MAPS_TRAINING, ARENA_BONUS_TYPE.EPIC_BATTLE):
                results = yield self.waitForBattleResults(arenaUniqueID)
            isSuccess = results.success
            if not isSuccess or not self.postResult(results.auxData, ctx.needToShowIfPosted()):
                self.__statsCtrls.pop(arenaUniqueID, None)
                event_dispatcher.hideBattleResults()
        if callback is not None:
            callback(isSuccess)
        return

    @adisp_async
    def requestEmblem(self, ctx, callback=None):
        fetcher = emblems.createFetcher(ctx)
        if fetcher is not None:
            fetcher.fetch(callback)
        else:
            LOG_WARNING('Icon fetcher is not found', ctx)
            if callback is not None:
                callback(None)
        return

    def postResult(self, result, needToShowUI=True):
        reusableInfo = reusable.createReusableInfo(result)
        if reusableInfo is None:
            pushNoBattleResultsDataMessage()
            return False
        else:
            self.__updateReusableInfo(reusableInfo)
            arenaUniqueID = reusableInfo.arenaUniqueID
            playerSatisfactionRating = reusableInfo.personal.avatar.playerSatisfactionRating
            if playerSatisfactionRating != PlayerSatisfactionRating.NONE:
                self.__playerSatisfactionRatings[arenaUniqueID] = playerSatisfactionRating
            statsCtrl = createStatsCtrl(reusableInfo)
            if statsCtrl is None:
                pushNoBattleResultsDataMessage()
                return False
            statsCtrl.setResults(result, reusableInfo)
            self.__statsCtrls[arenaUniqueID] = statsCtrl
            resultsWindow = self.__notifyBattleResultsPosted(arenaUniqueID, needToShowUI=needToShowUI)
            self.onResultPosted(reusableInfo, statsCtrl, resultsWindow)
            self.__postStatistics(reusableInfo, result)
            return True

    def areResultsPosted(self, arenaUniqueID):
        return arenaUniqueID in self.__statsCtrls

    def getResultsVO(self, arenaUniqueID):
        if arenaUniqueID in self.__statsCtrls:
            found = self.__statsCtrls[arenaUniqueID]
            vo = found.getVO()
        else:
            vo = None
        return vo

    def getPresenter(self, arenaUniqueID):
        if arenaUniqueID not in self.__statsCtrls:
            _logger.error('Missing suitable battle results presenter.')
            return None
        else:
            return self.__statsCtrls[arenaUniqueID]

    def saveStatsSorting(self, bonusType, iconType, sortDirection):
        stored_sorting.writeStatsSorting(bonusType, iconType, sortDirection)

    @decorators.adisp_process('updating')
    def applyAdditionalBonus(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        if arenaInfo is None:
            return
        else:
            result = yield PremiumBonusApplier(arenaUniqueID, arenaInfo.vehicleID).request()
            if result and result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                self.__appliedAddXPBonus.add(arenaUniqueID)
                yield self.__updateStatsCtrl(arenaUniqueID, arenaInfo)
            self.__onAddXPBonusChanged(bool(result and result.success))
            return

    def isAddXPBonusApplied(self, arenaUniqueID):
        return arenaUniqueID in self.__appliedAddXPBonus

    def isAddXPBonusEnabled(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        isWotPlusEnabled = self.lobbyContext.getServerSettings().isRenewableSubEnabled()
        return arenaInfo is not None and (bool(PREMIUM_TYPE.activePremium(arenaInfo.premMask) & PREMIUM_TYPE.PLUS) or self.itemsCache.items.stats.isPremium or self.wotPlusController.isEnabled() and isWotPlusEnabled)

    def getAdditionalXPValue(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        return 0 if arenaInfo is None else arenaInfo.extraXP

    @adisp_process
    def submitPlayerSatisfactionRating(self, arenaUniqueID, rating):
        result = yield PlayerSatisfactionRatingProcessor(arenaUniqueID, rating).request()
        if result and result.userMsg:
            _logger.warning(result.userMsg)
        if result and result.success:
            self.__playerSatisfactionRatings[arenaUniqueID] = rating

    def getPlayerSatisfactionRating(self, arenaUniqueID):
        return self.__playerSatisfactionRatings.get(arenaUniqueID, PlayerSatisfactionRating.NONE)

    @isDeveloperFunc
    def resetPlayerSatisfactionRatings(self):
        arenaUniqueIDs = self.__playerSatisfactionRatings.keys()
        if not arenaUniqueIDs:
            return
        BigWorld.player().registerWithPlayerSatisfactionMgr(arenaUniqueIDs)
        self.__playerSatisfactionRatings.clear()

    def isCrewSameForArena(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        vehicle = self.getVehicleForArena(arenaUniqueID)
        if arenaInfo is not None and vehicle is not None:
            currentCrew = set((tankman.invID for _, tankman in vehicle.crew if tankman is not None))
            lastCrew = set((tankmanID for tankmanID, _ in arenaInfo.extraTmenXP))
            return currentCrew == lastCrew
        else:
            return False

    def isXPToTManSameForArena(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        vehicle = self.getVehicleForArena(arenaUniqueID)
        return vehicle.isXPToTman == arenaInfo.isXPToTMan if arenaInfo is not None and vehicle is not None else False

    def getVehicleForArena(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        return self.itemsCache.items.getItemByCD(arenaInfo.vehicleID) if arenaInfo is not None else None

    def __postStatistics(self, reusableInfo, result):
        playerAccount = BigWorld.player()
        if playerAccount is None or not isinstance(playerAccount, PlayerAccount):
            raise SoftException('Could not post afterbattle statistics, possible not in hangar')
        if reusableInfo.common.arenaBonusType != ARENA_BONUS_TYPE.REGULAR:
            _logger.debug('Only random battles results are logging')
            return
        else:
            return

    def __getAdditionalXPBattles(self):
        return self.itemsCache.items.stats.additionalXPCache

    @adisp_process
    def __showResults(self, ctx):
        yield self.requestResults(ctx)

    def notifyBattleResultsPosted(self, arenaUniqueID, needToShowUI=False):
        self.__notifyBattleResultsPosted(arenaUniqueID, needToShowUI)

    def __notifyBattleResultsPosted(self, arenaUniqueID, needToShowUI=False):
        statsCtrl = self.__statsCtrls[arenaUniqueID]
        window = None
        if needToShowUI:
            window = statsCtrl.onShowResults(arenaUniqueID)
        statsCtrl.onResultsPosted(arenaUniqueID)
        return window

    def __handleLobbyViewLoaded(self, _):
        battleCtx = self.sessionProvider.getCtx()
        arenaUniqueID = battleCtx.lastArenaUniqueID
        arenaBonusType = battleCtx.lastArenaBonusType or ARENA_BONUS_TYPE.UNKNOWN
        if arenaUniqueID:
            try:
                self.__showResults(context.RequestResultsContext(arenaUniqueID, arenaBonusType))
            except Exception:
                LOG_CURRENT_EXCEPTION()

            battleCtx.lastArenaUniqueID = None
            battleCtx.lastArenaBonusType = None
        return

    @adisp_async
    @adisp_process
    def __updateStatsCtrl(self, arenaUniqueID, xpBonusData, callback):
        results = yield BattleResultsGetter(arenaUniqueID).request()
        if results.success:
            result = results.auxData
            reusableInfo = reusable.createReusableInfo(result)
            if reusableInfo is None:
                pushNoBattleResultsDataMessage()
                callback(False)
            self.__updateReusableInfo(reusableInfo, xpBonusData)
            arenaUniqueID = reusableInfo.arenaUniqueID
            statsCtrl = self.__statsCtrls.get(arenaUniqueID)
            if statsCtrl is None or not isinstance(statsCtrl, BaseStatsPresenter):
                statsCtrl = createStatsCtrl(reusableInfo)
            statsCtrl.setResults(result, reusableInfo)
            self.__statsCtrls[arenaUniqueID] = statsCtrl
        callback(True)
        return

    def __updateReusableInfo(self, reusableInfo, xpBonusData=None):
        arenaUniqueID = reusableInfo.arenaUniqueID
        reusableInfo.premiumState = self.__makePremiumState(arenaUniqueID, PREMIUM_TYPE.BASIC)
        reusableInfo.premiumPlusState = self.__makePremiumState(arenaUniqueID, PREMIUM_TYPE.PLUS)
        isXPBonusApplied = self.isAddXPBonusApplied(arenaUniqueID)
        reusableInfo.isAddXPBonusApplied = isXPBonusApplied
        if xpBonusData:
            reusableInfo.updateXPEarnings(xpBonusData)
        reusableInfo.clientIndex = self.lobbyContext.getClientIDByArenaUniqueID(arenaUniqueID)

    def __onPremiumBought(self, event):
        ctx = event.ctx
        arenaUniqueID = event.ctx['arenaUniqueID']
        becomePremium = event.ctx['becomePremium']
        if becomePremium and arenaUniqueID:
            self.__buy.add(arenaUniqueID)
            event_dispatcher.hideBattleResults()
            self.__showResults(context.RequestResultsContext(arenaUniqueID, resetCache=True))

    def __makePremiumState(self, arenaUniqueID, premType=PREMIUM_TYPE.BASIC):
        state = PREMIUM_STATE.NONE
        settings = self.lobbyContext.getServerSettings()
        if settings is not None and settings.isPremiumInPostBattleEnabled():
            state |= PREMIUM_STATE.BUY_ENABLED
        if self.itemsCache.items.stats.isActivePremium(premType):
            state |= PREMIUM_STATE.HAS_ALREADY
        if arenaUniqueID in self.__buy:
            state |= PREMIUM_STATE.BOUGHT
        return state

    def __onAddXPBonusChanged(self, isBonusApplied=True):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, ctx={'isBonusApplied': isBonusApplied}))

    @adisp_async
    @adisp_process
    def waitForBattleResults(self, arenaUniqueID, callback=None):

        @adisp_async
        def wait(t, callback):
            BigWorld.callback(t, lambda : callback(None))

        isSuccess = False
        results = None
        while not isSuccess:
            yield wait(1)
            results = yield BattleResultsGetter(arenaUniqueID).request()
            isSuccess = results.success

        if callback is not None:
            callback(results)
        return
