# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/actions_handlers.py
from collections import defaultdict
import BigWorld
import typing
from adisp import adisp_process
from CurrentVehicle import g_currentVehicle
from battle_pass_common import isPostProgressionChapter
from constants import PREBATTLE_TYPE, PENALTY_TYPES, FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import DialogsInterface, SystemMessages, makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getIntegratedAuctionUrl, getPlayerSeniorityAwardsUrl
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.battle_results import RequestResultsContext
from gui.clans.clan_helpers import showAcceptClanInviteDialog
from gui.collection.collections_helpers import loadHangarFromCollections
from gui.customization.constants import CustomizationModeSource, CustomizationModes
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.gen import R
from gui.impl.lobby.achievements.profile_utils import createAdvancedAchievementsCatalogInitAchievementIDs
from gui.lootbox_system.base.common import ViewID, Views
from gui.platform.base.statuses.constants import StatusTypes
from gui.prb_control import prbDispatcherProperty, prbInvitesProperty
from gui.prestige.prestige_helpers import showPrestigeOnboardingWindow, showPrestigeVehicleStats
from gui.ranked_battles import ranked_helpers
from gui.server_events.events_dispatcher import showMissionsBattlePass, showMissionsMapboxProgression, showPersonalMission, showBanWindow, showPenaltyWindow, showWarningWindow
from gui.shared import EVENT_BUS_SCOPE, actions, event_dispatcher as shared_events, events, g_eventBus
from gui.shared.event_dispatcher import hideWebBrowserOverlay, showBlueprintsSalePage, showCollectionAwardsWindow, showCollectionWindow, showCollectionsMainPage, showDelayedReward, showEpicBattlesAfterBattleWindow, showProgressiveRewardWindow, showRankedYearAwardWindow, showShop, showSteamConfirmEmailOverlay, showWinbackSelectRewardView, showWotPlusIntroView, showBarracks, showSeniorityRewardVehiclesWindow, showAdvancedAchievementsView, showTrophiesView, showAdvancedAchievementsCatalogView, showExchangeGoldWindow, showExchangeFreeXPWindow, showCrewPostProgressionView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import ClaimRewardForPostProgression
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.system_factory import collectAllNotificationsActionsHandlers, registerNotificationsActionsHandlers
from gui.shared.utils import decorators
from gui.wgcg.clan import contexts as clan_ctxs
from gui.wgnc import g_wgncProvider
from helpers import dependency
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from notification.settings import NOTIFICATION_BUTTON_STATE, NOTIFICATION_TYPE, NOTIFICATION_STATE
from predefined_hosts import g_preDefinedHosts
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController, IBattleRoyaleController, IBrowserController, ICollectionsSystemController, IMapboxController, IRankedBattlesController, ISeniorityAwardsController, IWinbackController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from skeletons.gui.web import IWebController
from soft_exception import SoftException
from uilogging.epic_battle.constants import EpicBattleLogActions, EpicBattleLogButtons, EpicBattleLogKeys
from uilogging.epic_battle.loggers import EpicBattleLogger
from uilogging.seniority_awards.constants import SeniorityAwardsLogSpaces
from uilogging.seniority_awards.loggers import VehicleSelectionNotificationLogger, CoinsNotificationLogger, RewardNotificationLogger
from uilogging.wot_plus.loggers import WotPlusNotificationLogger
from uilogging.wot_plus.logging_constants import NotificationAdditionalData
from uilogging.advanced_achievement.logger import AdvancedAchievementLogger
from uilogging.advanced_achievement.logging_constants import AdvancedAchievementButtons, AdvancedAchievementViewKey
from web.web_client_api import webApiCollection
from web.web_client_api.sound import HangarSoundWebApi
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Tuple
    from notification.NotificationsModel import NotificationsModel
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus

class ActionHandler(object):

    @classmethod
    def getNotType(cls):
        return NotImplementedError

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        if action not in self.getActions():
            raise SoftException('Handler does not handle action {0}'.format(action))


class NavigationDisabledActionHandler(ActionHandler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def handleAction(self, model, entityID, action):
        super(NavigationDisabledActionHandler, self).handleAction(model, entityID, action)
        if not self._canNavigate():
            return
        self.doAction(model, entityID, action)

    def doAction(self, model, entityID, action):
        raise NotImplementedError

    def _canNavigate(self):
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            BigWorld.callback(0.0, self.__showMessage)
            return False
        else:
            return True

    @staticmethod
    def __showMessage():
        SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


class _OpenEventBoardsHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_OpenEventBoardsHandler, self).handleAction(model, entityID, action)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MISSIONS), ctx={'tab': QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS}), scope=EVENT_BUS_SCOPE.LOBBY)


class _ShowArenaResultHandler(ActionHandler):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    def handleAction(self, model, entityID, action):
        super(_ShowArenaResultHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        savedData = notification.getSavedData()
        if not savedData:
            self._updateNotification(notification)
            LOG_ERROR('arenaUniqueID not found', notification)
            return
        self._showWindow(notification, savedData)

    def _updateNotification(self, notification):
        _, formatted, settings = self.proto.serviceChannel.getMessage(notification.getID())
        if formatted and settings:
            formatted['buttonsStates'].update({'submit': NOTIFICATION_BUTTON_STATE.HIDDEN})
            formatted['message'] += makeHtmlString('html_templates:lobby/system_messages', 'infoNoAvailable')
            notification.update(formatted)

    def _showWindow(self, notification, arenaUniqueID):
        pass

    def _showI18nMessage(self, key, msgType):

        def showMessage():
            SystemMessages.pushI18nMessage(key, type=msgType)

        BigWorld.callback(0.0, showMessage)


class _ShowClanSettingsHandler(ActionHandler):

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanSettingsHandler, self).handleAction(model, entityID, action)
        LOG_DEBUG('_ShowClanSettingsHandler handleAction:')
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.SETTINGS_WINDOW), ctx={'redefinedKeyMode': False}), EVENT_BUS_SCOPE.LOBBY)


class _ShowClanSettingsFromAppsHandler(_ShowClanSettingsHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APPS


class _ShowClanSettingsFromInvitesHandler(_ShowClanSettingsHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITES


class _ShowClanAppsHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APPS

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanAppsHandler, self).handleAction(model, entityID, action)
        return shared_events.showClanInvitesWindow()


class _ShowClanInvitesHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITES

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanInvitesHandler, self).handleAction(model, entityID, action)
        shared_events.showClanPersonalInvitesWindow()


class _ClanAppHandler(ActionHandler):
    clanCtrl = dependency.descriptor(IWebController)

    def _getAccountID(self, model, entityID):
        return model.getNotification(self.getNotType(), entityID).getAccountID()

    def _getApplicationID(self, model, entityID):
        return model.getNotification(self.getNotType(), entityID).getApplicationID()


class _AcceptClanAppHandler(_ClanAppHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APP

    @classmethod
    def getActions(cls):
        pass

    @adisp_process
    def handleAction(self, model, entityID, action):
        super(_AcceptClanAppHandler, self).handleAction(model, entityID, action)
        yield self.clanCtrl.sendRequest(clan_ctxs.AcceptApplicationCtx(self._getApplicationID(model, entityID)), allowDelay=True)


class _DeclineClanAppHandler(_ClanAppHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APP

    @classmethod
    def getActions(cls):
        pass

    @adisp_process
    def handleAction(self, model, entityID, action):
        super(_DeclineClanAppHandler, self).handleAction(model, entityID, action)
        yield self.clanCtrl.sendRequest(clan_ctxs.DeclineApplicationCtx(self._getApplicationID(model, entityID)), allowDelay=True)


class _ShowClanAppUserInfoHandler(_ClanAppHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APP

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanAppUserInfoHandler, self).handleAction(model, entityID, action)
        accID = self._getAccountID(model, entityID)

        def onDossierReceived(databaseID, userName):
            shared_events.showProfileWindow(databaseID, userName)

        shared_events.requestProfile(accID, model.getNotification(self.getNotType(), entityID).getUserName(), successCallback=onDossierReceived)
        return None


class _ClanInviteHandler(ActionHandler):
    clanCtrl = dependency.descriptor(IWebController)

    def _getInviteID(self, model, entityID):
        return model.getNotification(self.getNotType(), entityID).getInviteID()


class _AcceptClanInviteHandler(_ClanInviteHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITE

    @classmethod
    def getActions(cls):
        pass

    @adisp_process
    def handleAction(self, model, entityID, action):
        super(_AcceptClanInviteHandler, self).handleAction(model, entityID, action)
        entity = model.getNotification(self.getNotType(), entityID).getEntity()
        clanName = entity.getClanName()
        clanTag = entity.getClanTag()
        result = yield showAcceptClanInviteDialog(clanName, clanTag)
        if result:
            yield self.clanCtrl.sendRequest(clan_ctxs.AcceptInviteCtx(self._getInviteID(model, entityID)), allowDelay=True)


class _DeclineClanInviteHandler(_ClanInviteHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITE

    @classmethod
    def getActions(cls):
        pass

    @adisp_process
    def handleAction(self, model, entityID, action):
        super(_DeclineClanInviteHandler, self).handleAction(model, entityID, action)
        yield self.clanCtrl.sendRequest(clan_ctxs.DeclineInviteCtx(self._getInviteID(model, entityID)), allowDelay=True)


class _ShowClanProfileHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanProfileHandler, self).handleAction(model, entityID, action)
        clan = model.getNotification(self.getNotType(), entityID)
        shared_events.showClanProfileWindow(clan.getClanID(), clan.getClanAbbrev())


class ShowRankedSeasonCompleteHandler(ActionHandler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            self.__showSeasonAward(savedData['quest'], savedData['awards'])
        return

    def __showSeasonAward(self, quest, data):
        seasonID, _, _ = ranked_helpers.getDataFromSeasonTokenQuestID(quest.getID())
        season = self.rankedController.getSeason(seasonID)
        if season is not None:
            shared_events.showRankedSeasonCompleteView({'quest': quest,
             'awards': data})
        return


class ShowRankedFinalYearHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            self.__showFinalAward(savedData['questID'], savedData['awards'])
        return

    def __showFinalAward(self, questID, data):
        points = ranked_helpers.getDataFromFinalTokenQuestID(questID)
        showRankedYearAwardWindow(data, points)


class ShowRankedYearPositionHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None and isinstance(savedData, dict):
            playerPosition = savedData.get('yearPosition')
            rewardsData = savedData.get('rewardsData')
            if playerPosition is not None and rewardsData:
                shared_events.showRankedYearLBAwardWindow(playerPosition, rewardsData)
        return


class ShowRankedBattlePageHandler(ActionHandler):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None and isinstance(savedData, dict):
            ctx = savedData.get('ctx')
            if ctx is not None and ctx.get('selectedItemID') is not None:
                self.__rankedController.showRankedBattlePage(ctx)
        return


class SelectBattleRoyaleMode(ActionHandler):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        self.battleRoyale.selectRoyaleBattle()


class ShowBattleResultsHandler(_ShowArenaResultHandler):
    battleResults = dependency.descriptor(IBattleResultsService)

    def _updateNotification(self, notification):
        super(ShowBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    @classmethod
    def getActions(cls):
        pass

    @decorators.adisp_process('loadStats')
    def _showWindow(self, notification, arenaUniqueID):
        uniqueID = long(arenaUniqueID)
        result = yield self.battleResults.requestResults(RequestResultsContext(uniqueID, showImmediately=False, showIfPosted=True, resetCache=False))
        if not result:
            self._updateNotification(notification)


class ShowFortBattleResultsHandler(_ShowArenaResultHandler):

    @classmethod
    def getActions(cls):
        pass

    def _updateNotification(self, notification):
        super(ShowFortBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, data):
        if data:
            battleResultData = data.get('battleResult', None)
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS), ctx={'data': battleResultData}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self._updateNotification(notification)
        return


class OpenPollHandler(ActionHandler):
    browserCtrl = dependency.descriptor(IBrowserController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(OpenPollHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification is not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        link, title = notification.getSettings().auxData
        if not link:
            LOG_ERROR('Poll link is not found', notification)
            return
        self.__doOpen(link, title)

    @adisp_process
    def __doOpen(self, link, title):
        browserID = yield self.browserCtrl.load(link, title, showActionBtn=False, handlers=webApiCollection(HangarSoundWebApi))
        browser = self.browserCtrl.getBrowser(browserID)
        if browser is not None:
            browser.setIsAudioMutable(True)
        return


class AcceptPrbInviteHandler(ActionHandler):
    __winbackController = dependency.descriptor(IWinbackController)

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.INVITE

    @classmethod
    def getActions(cls):
        pass

    @adisp_process
    def handleAction(self, model, entityID, action):
        super(AcceptPrbInviteHandler, self).handleAction(model, entityID, action)
        yield lambda callback: callback(None)
        postActions = []
        invite = self.prbInvites.getInvite(entityID)
        state = self.prbDispatcher.getFunctionalState()
        if state.doLeaveToAcceptInvite(invite.type):
            postActions.append(actions.LeavePrbModalEntity())
            if self.__winbackController.isModeAvailable() and invite.type == PREBATTLE_TYPE.SQUAD:
                postActions.append(actions.LeaveWinbackModeEntity())
        if invite and invite.anotherPeriphery:
            success = True
            if g_preDefinedHosts.isRoamingPeriphery(invite.peripheryID):
                success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
            if not success:
                return
            postActions.append(actions.DisconnectFromPeriphery(loginViewPreselectedPeriphery=invite.peripheryID))
            postActions.append(actions.ConnectToPeriphery(invite.peripheryID))
            postActions.append(actions.PrbInvitesInit())
            postActions.append(actions.LeavePrbEntity())
        g_eventBus.handleEvent(events.PrbInvitesEvent(events.PrbInvitesEvent.ACCEPT, inviteID=entityID, postActions=postActions), scope=EVENT_BUS_SCOPE.LOBBY)


class DeclinePrbInviteHandler(ActionHandler):

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.INVITE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(DeclinePrbInviteHandler, self).handleAction(model, entityID, action)
        if entityID:
            self.prbInvites.declineInvite(entityID)
        else:
            LOG_ERROR('Invite is invalid', entityID)


class ApproveFriendshipHandler(ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(ApproveFriendshipHandler, self).handleAction(model, entityID, action)
        self.proto.contacts.approveFriendship(entityID)


class CancelFriendshipHandler(ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(CancelFriendshipHandler, self).handleAction(model, entityID, action)
        self.proto.contacts.cancelFriendship(entityID)


class WGNCActionsHandler(ActionHandler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.WGNC_POP_UP

    def handleAction(self, model, entityID, action):
        if not self._canNavigate():
            return
        notification = model.collection.getItem(NOTIFICATION_TYPE.WGNC_POP_UP, entityID)
        if notification:
            actorName = notification.getSavedData()
        else:
            actorName = ''
        g_wgncProvider.doAction(entityID, action, actorName)

    def _canNavigate(self):
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            BigWorld.callback(0.0, self.__showMessage)
            return False
        else:
            return True

    @staticmethod
    def __showMessage():
        SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


class SecurityLinkHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SECURITY_SETTINGS))


class ClanRulesHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.CLAN_RULES))


class OpenCustomizationHandler(ActionHandler):
    service = dependency.descriptor(ICustomizationService)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(OpenCustomizationHandler, self).handleAction(model, entityID, action)
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        vehicleIntCD = savedData.get('vehicleIntCD')
        vehicle = self.service.getItemByCD(vehicleIntCD)

        def toCustomizationCallback():
            ctx = self.service.getCtx()
            if savedData.get('toStyle'):
                if ctx.modeId not in CustomizationModes.BASE_STYLES:
                    ctx.changeMode(CustomizationModes.STYLE_2D, source=CustomizationModeSource.NOTIFICATION)
            elif savedData.get('toProjectionDecals'):
                itemCD = savedData.get('itemIntCD', 0)
                goToEditableStyle = ctx.canEditStyle(itemCD)
                style = None
                if ctx.modeId in CustomizationModes.BASE_STYLES:
                    style = ctx.mode.modifiedStyle
                if goToEditableStyle and style is not None:
                    ctx.editStyle(style.intCD, source=CustomizationModeSource.NOTIFICATION)
                else:
                    ctx.changeMode(CustomizationModes.CUSTOM, source=CustomizationModeSource.NOTIFICATION)
                ctx.mode.changeTab(tabId=CustomizationTabs.PROJECTION_DECALS, itemCD=itemCD)
            return

        if vehicle.invID != -1:
            context = self.service.getCtx()
            if context is not None and g_currentVehicle.isPresent() and g_currentVehicle.item.intCD == vehicleIntCD:
                toCustomizationCallback()
            else:
                g_eventBus.handleEvent(events.CustomizationEvent(events.CustomizationEvent.SHOW, ctx={'vehInvID': vehicle.invID,
                 'callback': toCustomizationCallback}), scope=EVENT_BUS_SCOPE.LOBBY)
        return


class ProlongStyleRent(ActionHandler):
    service = dependency.descriptor(ICustomizationService)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(ProlongStyleRent, self).handleAction(model, entityID, action)
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        vehicleIntCD = savedData.get('vehicleIntCD')
        styleIntCD = savedData.get('styleIntCD')
        vehicle = self.service.getItemByCD(vehicleIntCD)
        style = self.service.getItemByCD(styleIntCD)

        def prolongRentCallback():
            ctx = self.service.getCtx()
            ctx.changeMode(CustomizationModes.STYLE_3D if style.is3D else CustomizationModes.STYLE_2D)
            ctx.mode.prolongRent(style)

        if vehicle.invID != -1:
            g_eventBus.handleEvent(events.CustomizationEvent(events.CustomizationEvent.SHOW, ctx={'vehInvID': vehicle.invID,
             'callback': prolongRentCallback}), scope=EVENT_BUS_SCOPE.LOBBY)


class _OpenMissingEventsHandler(ActionHandler):
    __notification = dependency.descriptor(INotificationWindowController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MISSING_EVENTS

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = self.__notification
        if notification.isEnabled():
            notification.releasePostponed()
        else:
            BigWorld.callback(0, self.__showErrorMessage)

    @staticmethod
    def __showErrorMessage():
        SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.queue.isInQueue()), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.HIGH)


class _OpenNotrecruitedHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.RECRUIT_REMINDER

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showBarracks(location=BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED)


class _OpenNotrecruitedSysMessageHandler(_OpenNotrecruitedHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE


class _OpenBarracksHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showBarracks()


class _OpenConfirmEmailHandler(NavigationDisabledActionHandler):
    __wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.EMAIL_CONFIRMATION_REMINDER

    @classmethod
    def getActions(cls):
        pass

    @wg_async
    def doAction(self, model, entityID, action):
        status = yield wg_await(self.__wgnpSteamAccCtrl.getEmailStatus())
        if status.typeIs(StatusTypes.ADDED):
            showSteamConfirmEmailOverlay(email=status.email)


class OpenPersonalMissionHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            showPersonalMission(missionID=savedData['questID'])
        return


class _OpenLootBoxesHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            pass
        return


class _LootBoxesAutoOpenHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None and 'rewards' in savedData:
            pass
        return


class _OpenLootBoxSystemHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData and 'eventName' in savedData:
            Views.load(ViewID.MAIN, eventName=savedData['eventName'])


class _LootBoxSystemAutoOpenHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None and 'rewards' in savedData:
            Views.load(ViewID.AUTOOPEN, savedData['eventName'], savedData['rewards'], savedData['boxIDs'])
        return


class _OpenProgressiveRewardView(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.PROGRESSIVE_REWARD

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showProgressiveRewardWindow()


class _OpenBattlePassProgressionView(NavigationDisabledActionHandler):
    __battlePass = dependency.descriptor(IBattlePassController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        hideWebBrowserOverlay()
        if savedData is not None:
            chapterID = savedData.get('chapterID')
            if not isPostProgressionChapter(chapterID):
                showMissionsBattlePass(R.views.lobby.battle_pass.BattlePassProgressionsView(), chapterID)
            else:
                showMissionsBattlePass(R.views.lobby.battle_pass.PostProgressionView())
        else:
            showMissionsBattlePass()
        return


class _OpenBattlePassChapterChoiceView(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())


class _OpenBPExtraWillEndSoon(NavigationDisabledActionHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        chapterID = self.__battlePassController.getExtraChapterID()
        if chapterID:
            showMissionsBattlePass(R.views.lobby.battle_pass.BattlePassProgressionsView(), chapterID)


class _OpentBlueprintsConvertSale(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showBlueprintsSalePage()


class _OpenMapboxProgression(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showMissionsMapboxProgression()


class _OpenMapboxSurvey(NavigationDisabledActionHandler):
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        if self.__mapboxCtrl.getProgressionData() is not None:
            self.__mapboxCtrl.showSurvey(notification.getSavedData())
        else:
            showMissionsMapboxProgression()
        return


class _OpenDelayedReward(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showDelayedReward()


class _OpenChapterChoiceView(_OpenBattlePassProgressionView):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.BATTLE_PASS_SWITCH_CHAPTER_REMINDER


class _OpenEpicBattlesAfterBattleWindow(NavigationDisabledActionHandler):
    __slots__ = ('__uiEpicBattleLogger',)

    def __init__(self):
        super(_OpenEpicBattlesAfterBattleWindow, self).__init__()
        self.__uiEpicBattleLogger = EpicBattleLogger()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        levelUpInfo = notification.getSavedData()
        showEpicBattlesAfterBattleWindow(levelUpInfo)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, EpicBattleLogButtons.LEVELUP_NOTIFICATION.value, EpicBattleLogKeys.HANGAR.value)


class _OpenCustomizationStylesSection(NavigationDisabledActionHandler):
    __customizationService = dependency.descriptor(ICustomizationService)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        notificationData = notification.getSavedData() or {}
        styleID = notificationData.get('styleID')
        if styleID:
            style = self.__customizationService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
            self.__customizationService.showCustomization(modeId=CustomizationModes.STYLE_3D if style.is3D else CustomizationModes.STYLE_2D, tabId=CustomizationTabs.STYLES_3D if style.is3D else CustomizationTabs.STYLES_2D, itemCD=style.intCD)


class _OpenIntegratedAuction(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showShop(getIntegratedAuctionUrl())


class _OpenIntegratedAuctionStart(_OpenIntegratedAuction):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.AUCTION_STAGE_START

    @classmethod
    def getActions(cls):
        pass


class _OpenIntegratedAuctionFinish(_OpenIntegratedAuction):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.AUCTION_STAGE_FINISH

    @classmethod
    def getActions(cls):
        pass


class _OpenPersonalReservesHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        shared_events.showBoostersActivation()


class _SeniorityAwardsTokensHandler(NavigationDisabledActionHandler):
    __slots__ = ('__uiCoinsNotificationLogger',)

    def __init__(self):
        super(_SeniorityAwardsTokensHandler, self).__init__()
        self.__uiCoinsNotificationLogger = CoinsNotificationLogger()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.SENIORITY_AWARDS_TOKENS

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        displaySpace = SeniorityAwardsLogSpaces.HANGAR if model.getDisplayState() == NOTIFICATION_STATE.POPUPS else SeniorityAwardsLogSpaces.NOTIFICATION_CENTER
        self.__uiCoinsNotificationLogger.handleClickAction(displaySpace)
        showShop(getPlayerSeniorityAwardsUrl())


class _OpenSeniorityAwardsVehicleSelection(NavigationDisabledActionHandler):
    __slots__ = ('__uiVehicleSelectionNotificationLogger',)
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self):
        super(_OpenSeniorityAwardsVehicleSelection, self).__init__()
        self.__uiVehicleSelectionNotificationLogger = VehicleSelectionNotificationLogger()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self.__uiVehicleSelectionNotificationLogger.handleClickAction()
        if self.__seniorityAwardCtrl.isVehicleSelectionAvailable:
            showSeniorityRewardVehiclesWindow()


class _OpenSeniorityAwardsPersonalVehicleSelection(_OpenSeniorityAwardsVehicleSelection):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.SENIORITY_AWARDS_VEHICLE_SELECTION


class _OpenSeniorityAwards(NavigationDisabledActionHandler):
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)
    __slots__ = ('__uiRewardNotificationLogger',)

    def __init__(self):
        super(_OpenSeniorityAwards, self).__init__()
        self.__uiRewardNotificationLogger = RewardNotificationLogger()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.SENIORITY_AWARDS_QUEST

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        displaySpace = SeniorityAwardsLogSpaces.HANGAR if model.getDisplayState() == NOTIFICATION_STATE.POPUPS else SeniorityAwardsLogSpaces.NOTIFICATION_CENTER
        self.__uiRewardNotificationLogger.handleClickAction(displaySpace)
        self.__seniorityAwardCtrl.claimReward()


class _OpenWinbackSelectableRewardView(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.WINBACK_SELECTABLE_REWARD_AVAILABLE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showWinbackSelectRewardView()


class _OpenWinbackSelectableRewardViewFromQuest(_OpenWinbackSelectableRewardView):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE


class _OpenAchievementsScreen(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx={'selectedAlias': VIEW_ALIAS.PROFILE_TOTAL_PAGE}), scope=EVENT_BUS_SCOPE.LOBBY)


class _OpenAdvancedAchievementsScreen(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        data = model.getNotification(self.getNotType(), entityID).getSavedData() or {}
        isTrophy = data.get('isTrophy')
        target = data.get('target')
        uiLogger = AdvancedAchievementLogger(AdvancedAchievementViewKey.NOTIFICATION_CENTER)
        closeCallbackPlaceholder = lambda *args, **kwargs: None
        uiLogger.logClick(AdvancedAchievementButtons.TO_ACHIEVEMENT)
        if isTrophy:
            showTrophiesView(closeCallback=closeCallbackPlaceholder, parentScreen=AdvancedAchievementViewKey.NOTIFICATION_CENTER)
        elif target:
            id, category = target
            initAchievementsIds = createAdvancedAchievementsCatalogInitAchievementIDs(id, category)
            showAdvancedAchievementsCatalogView(initAchievementsIds, category, closeCallback=closeCallbackPlaceholder, parentScreen=AdvancedAchievementViewKey.NOTIFICATION_CENTER)
        else:
            showAdvancedAchievementsView()


class _OpenCollectionHandler(NavigationDisabledActionHandler):
    __collections = dependency.descriptor(ICollectionsSystemController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        collectionID = (model.getNotification(self.getNotType(), entityID).getSavedData() or {}).get('collectionId')
        if collectionID:
            backText = backport.text(R.strings.menu.viewHeader.backBtn.descrLabel.hangar())
            showCollectionWindow(collectionID, backCallback=loadHangarFromCollections, backBtnText=backText)
        else:
            showCollectionsMainPage()


class _OpenCollectionEntryHandler(_OpenCollectionHandler):
    __collections = dependency.descriptor(ICollectionsSystemController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.COLLECTIONS_ENTRY

    @classmethod
    def getActions(cls):
        pass


class _OpenCollectionRenewHandler(_OpenCollectionHandler):
    __collections = dependency.descriptor(ICollectionsSystemController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.COLLECTIONS_RENEW

    @classmethod
    def getActions(cls):
        pass


class _OpenCollectionRewardHandler(NavigationDisabledActionHandler):
    __collections = dependency.descriptor(ICollectionsSystemController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        savedData = model.getNotification(self.getNotType(), entityID).getSavedData()
        showCollectionAwardsWindow(savedData['collectionId'], savedData['bonuses'])


class _OpenWotPlusIntroView(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_OpenWotPlusIntroView, self).handleAction(model, entityID, action)
        WotPlusNotificationLogger().logDetailsButtonClickEvent(NotificationAdditionalData.SPECIAL_NOTIFICATION)
        showWotPlusIntroView()


class _OpenPrestigeVehicleStats(NavigationDisabledActionHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        savedData = model.getNotification(self.getNotType(), entityID).getSavedData()
        showPrestigeVehicleStats(savedData['vehCD'])


class _OpenCrewPostProgression(NavigationDisabledActionHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showCrewPostProgressionView()


class _ClaimRewardPostProgression(NavigationDisabledActionHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    @decorators.adisp_process('updating')
    def doAction(self, model, entityID, action):
        processor = ClaimRewardForPostProgression(crewBooksViewedCache().xppToConvert())
        result = yield processor.request()
        if result.userMsg:

            def showMessage():
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, messageData=result.auxData)

            BigWorld.callback(0, showMessage)


class _OpenPrestigeOnboardingWindow(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.PRESTIGE_FIRST_ENTRY

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showPrestigeOnboardingWindow()


class _OpenPunishmentWindowHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            penaltyType = savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.PENALTY_TYPE]
            if penaltyType == PENALTY_TYPES.BAN:
                showBanWindow(savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TYPE_ID], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TIME], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.BAN_DURATION], force=True)
            if penaltyType == PENALTY_TYPES.PENALTY:
                showPenaltyWindow(savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TYPE_ID], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TIME], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.PUNISHMENT_REASON], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.IS_AFK_VIOLATION], force=True)
            if penaltyType == PENALTY_TYPES.WARNING:
                showWarningWindow(savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TYPE_ID], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TIME], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.PUNISHMENT_REASON], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.IS_AFK_VIOLATION], force=True)
        return


class _OpenGoldExchangeWindow(NavigationDisabledActionHandler):
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.EXCHANGE_RATE_GOLD_DISCOUNT

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showExchangeGoldWindow()


class _OpenXpExchangeWindow(NavigationDisabledActionHandler):
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.EXCHANGE_RATE_XP_DISCOUNT

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showExchangeFreeXPWindow()


_AVAILABLE_HANDLERS = [ShowBattleResultsHandler,
 ShowFortBattleResultsHandler,
 OpenPollHandler,
 AcceptPrbInviteHandler,
 DeclinePrbInviteHandler,
 ApproveFriendshipHandler,
 CancelFriendshipHandler,
 WGNCActionsHandler,
 SecurityLinkHandler,
 ClanRulesHandler,
 ShowRankedSeasonCompleteHandler,
 ShowRankedFinalYearHandler,
 ShowRankedYearPositionHandler,
 ShowRankedBattlePageHandler,
 SelectBattleRoyaleMode,
 _ShowClanAppsHandler,
 _ShowClanInvitesHandler,
 _AcceptClanAppHandler,
 _DeclineClanAppHandler,
 _ShowClanAppUserInfoHandler,
 _ShowClanProfileHandler,
 _ShowClanSettingsFromAppsHandler,
 _ShowClanSettingsFromInvitesHandler,
 _AcceptClanInviteHandler,
 _DeclineClanInviteHandler,
 _OpenEventBoardsHandler,
 OpenCustomizationHandler,
 _OpenNotrecruitedHandler,
 OpenPersonalMissionHandler,
 _OpenLootBoxesHandler,
 _LootBoxesAutoOpenHandler,
 _OpenLootBoxSystemHandler,
 _LootBoxSystemAutoOpenHandler,
 _OpenProgressiveRewardView,
 ProlongStyleRent,
 _OpenBattlePassProgressionView,
 _OpenBattlePassChapterChoiceView,
 _OpenBPExtraWillEndSoon,
 _OpenMissingEventsHandler,
 _OpenNotrecruitedSysMessageHandler,
 _OpentBlueprintsConvertSale,
 _OpenConfirmEmailHandler,
 _OpenMapboxProgression,
 _OpenMapboxSurvey,
 _OpenDelayedReward,
 _OpenChapterChoiceView,
 _OpenEpicBattlesAfterBattleWindow,
 _OpenCustomizationStylesSection,
 _OpenIntegratedAuction,
 _OpenIntegratedAuctionStart,
 _OpenIntegratedAuctionFinish,
 _OpenPersonalReservesHandler,
 _SeniorityAwardsTokensHandler,
 _OpenSeniorityAwards,
 _OpenMissingEventsHandler,
 _OpenCollectionHandler,
 _OpenCollectionEntryHandler,
 _OpenCollectionRenewHandler,
 _OpenCollectionRewardHandler,
 _OpenWinbackSelectableRewardView,
 _OpenWinbackSelectableRewardViewFromQuest,
 _OpenAchievementsScreen,
 _OpenAdvancedAchievementsScreen,
 _OpenWotPlusIntroView,
 _OpenBarracksHandler,
 _OpenPrestigeVehicleStats,
 _OpenPrestigeOnboardingWindow,
 _OpenSeniorityAwardsVehicleSelection,
 _OpenSeniorityAwardsPersonalVehicleSelection,
 _OpenPunishmentWindowHandler,
 _OpenXpExchangeWindow,
 _OpenGoldExchangeWindow,
 _OpenCrewPostProgression,
 _ClaimRewardPostProgression]
registerNotificationsActionsHandlers(_AVAILABLE_HANDLERS)

class NotificationsActionsHandlers(object):
    __slots__ = ('__single', '__multi')

    def __init__(self, handlers=None):
        super(NotificationsActionsHandlers, self).__init__()
        self.__single = {}
        self.__multi = defaultdict(set)
        if not handlers:
            handlers = collectAllNotificationsActionsHandlers()
        for clazz in handlers:
            actionsList = clazz.getActions()
            if actionsList:
                if len(actionsList) == 1:
                    self.__single[clazz.getNotType(), actionsList[0]] = clazz
                else:
                    LOG_ERROR('Handler is not added to collection', clazz)
            self.__multi[clazz.getNotType()].add(clazz)

    def handleAction(self, model, typeID, entityID, actionName):
        key = (typeID, actionName)
        if key in self.__single:
            clazz = self.__single[key]
            clazz().handleAction(model, entityID, actionName)
        elif typeID in self.__multi:
            for clazz in self.__multi[typeID]:
                clazz().handleAction(model, entityID, actionName)

        else:
            LOG_ERROR('Action handler not found', typeID, entityID, actionName)

    def cleanUp(self):
        self.__single.clear()
        self.__multi.clear()
