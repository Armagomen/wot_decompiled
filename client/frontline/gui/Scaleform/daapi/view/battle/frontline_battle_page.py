# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_battle_page.py
import BigWorld
import CommandMapping
from constants import ARENA_PERIOD
from frontline.gui.Scaleform.daapi.view.battle.frontline_crosshair import FrontlineCrosshairPanelContainer
from frontline.gui.Scaleform.daapi.view.battle.frontline_drone_music_player import FrontlineDroneMusicPlayer
from frontline.gui.Scaleform.daapi.view.battle.frontline_finish_sound_player import FrontlineFinishSoundPlayer
from frontline.gui.Scaleform.daapi.view.battle.frontline_markers2d import FrontlineMarkersManager
from frontline.gui.Scaleform.daapi.view.meta.FrontlineBattlePageMeta import FrontlineBattlePageMeta
from frontline.gui.Scaleform.genConsts.FRONTLINE_BATTLE_VIEW_ALIASES import FRONTLINE_BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases as ClassicDynAliases
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.sound_ctrls.epic_battle_sounds import EpicBattleSoundController
from gui.shared import EVENT_BUS_SCOPE, events
from shared_utils import CONST_CONTAINER

class DynamicAliases(CONST_CONTAINER):
    EPIC_FINISH_SOUND_PLAYER = 'epicFinishSoundPlayer'
    EPIC_DRONE_MUSIC_PLAYER = 'epicDroneMusicPlayer'


class _FrontlineBattleComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_FrontlineBattleComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL,
           DynamicAliases.EPIC_DRONE_MUSIC_PLAYER,
           ClassicDynAliases.PREBATTLE_TIMER_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.PROGRESSION_CTRL, (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_UPGRADE_PANEL,)),
         (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,)),
         (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.RESPAWN, (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_VIEW,)),
         (BATTLE_CTRL_ID.MAPS, (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN, BATTLE_VIEW_ALIASES.MINIMAP)),
         (BATTLE_CTRL_ID.SPECTATOR, (BATTLE_VIEW_ALIASES.SPECTATOR_VIEW,)),
         (BATTLE_CTRL_ID.GAME_NOTIFICATIONS, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.EPIC_MISSIONS, (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MISSIONS_PANEL,)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.EPIC_DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.EPIC_DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL,)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.EPIC_DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL))), viewsConfig=((DynamicAliases.EPIC_DRONE_MUSIC_PLAYER, FrontlineDroneMusicPlayer), (ClassicDynAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))


FRONTLINE_BATTLE_CLASSIC_CONFIG = _FrontlineBattleComponentsConfig()
_FRONTLINE_BATTLE_CLASSICS_COMPONENTS = FRONTLINE_BATTLE_CLASSIC_CONFIG
_FRONTLINE_BATTLE_EXTENDED_COMPONENTS = FRONTLINE_BATTLE_CLASSIC_CONFIG + ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.EPIC_FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.EPIC_FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.EPIC_FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.EPIC_FINISH_SOUND_PLAYER, FrontlineFinishSoundPlayer),))

class PageStates(object):
    NONE = -1
    GAME = 0
    LOADING = 1
    TABSCREEN = 2
    OVERVIEWMAP = 3
    RADIAL = 4
    RESPAWN = 5
    COUNTDOWN = 6
    SPECTATOR_FREE = 7
    SPECTATOR_FOLLOW = 8
    SPECTATOR_DEATHCAM = 9
    GAME_OVER = 10


_NEVER_HIDE = {BATTLE_VIEW_ALIASES.SIXTH_SENSE, BATTLE_VIEW_ALIASES.RIBBONS_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL}
_GAME_UI = {BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES,
 BATTLE_VIEW_ALIASES.DEBUG_PANEL,
 BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
 BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_SCORE_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
 BATTLE_VIEW_ALIASES.MINIMAP,
 BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MISSIONS_PANEL,
 BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RECOVERY_PANEL,
 BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR,
 BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR,
 BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_INGAME_RANK,
 BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,
 BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL,
 BATTLE_VIEW_ALIASES.CALLOUT_PANEL,
 BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MODIFICATION_PANEL}
_SPECTATOR_UI = {BATTLE_VIEW_ALIASES.SPECTATOR_VIEW,
 BATTLE_VIEW_ALIASES.DEBUG_PANEL,
 BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_SCORE_PANEL,
 BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,
 BATTLE_VIEW_ALIASES.MINIMAP,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL}
_POSTMORTEM_UI = {BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL,
 BATTLE_VIEW_ALIASES.DEBUG_PANEL,
 BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_SCORE_PANEL,
 BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,
 BATTLE_VIEW_ALIASES.MINIMAP,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL}
_ENABLE_CONTROL_MODE = {PageStates.TABSCREEN,
 PageStates.RESPAWN,
 PageStates.RADIAL,
 PageStates.LOADING}
_PAGE_STATE_TO_CONTROL_PARAMS = {(PageStates.TABSCREEN, False): (BATTLE_VIEW_ALIASES.FULL_STATS, True, True),
 (PageStates.RESPAWN, False): (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_VIEW, True, True),
 (PageStates.RADIAL, False): (BATTLE_VIEW_ALIASES.RADIAL_MENU, False, False),
 (PageStates.LOADING, False): (BATTLE_VIEW_ALIASES.BATTLE_LOADING, True, True),
 (PageStates.RESPAWN, True): (FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_VIEW, True, False)}
_STATE_TO_UI = {PageStates.GAME: _GAME_UI.union({FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_UPGRADE_PANEL}),
 PageStates.LOADING: {BATTLE_VIEW_ALIASES.BATTLE_LOADING, FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_DEPLOYMENT_MAP, BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL},
 PageStates.TABSCREEN: {BATTLE_VIEW_ALIASES.FULL_STATS, BATTLE_VIEW_ALIASES.DEBUG_PANEL, BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL},
 PageStates.OVERVIEWMAP: {FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_DEPLOYMENT_MAP,
                          FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN,
                          FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_SCORE_PANEL,
                          BATTLE_VIEW_ALIASES.BATTLE_TIMER,
                          BATTLE_VIEW_ALIASES.DEBUG_PANEL,
                          BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
                          BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL},
 PageStates.RADIAL: _GAME_UI.union({BATTLE_VIEW_ALIASES.RADIAL_MENU}),
 PageStates.RESPAWN: {FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_VIEW,
                      BATTLE_VIEW_ALIASES.DEBUG_PANEL,
                      FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_DEPLOYMENT_MAP,
                      BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
                      BATTLE_VIEW_ALIASES.BATTLE_TIMER},
 PageStates.COUNTDOWN: _GAME_UI.difference({FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL, FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MISSIONS_PANEL, BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL}).union({BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL}),
 PageStates.SPECTATOR_DEATHCAM: _POSTMORTEM_UI.union({BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
                                 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL,
                                 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
                                 FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL}),
 PageStates.SPECTATOR_FREE: _SPECTATOR_UI.union({FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_PLATOON_PANEL, FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL}),
 PageStates.SPECTATOR_FOLLOW: _POSTMORTEM_UI.union({BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
                               FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RECOVERY_PANEL,
                               FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL,
                               BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL,
                               FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MISSIONS_PANEL,
                               BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL}),
 PageStates.GAME_OVER: _GAME_UI.difference({FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_REINFORCEMENT_PANEL,
                        FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_MISSIONS_PANEL,
                        BATTLE_VIEW_ALIASES.BATTLE_TIMER,
                        BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR,
                        BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR,
                        BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL})}
_FRONTLINE_EXTERNAL_COMPONENTS = (FrontlineCrosshairPanelContainer, FrontlineMarkersManager, KillCamMarkersManager)

class FrontlineBattlePage(FrontlineBattlePageMeta, BattleGUIKeyHandler):

    def __init__(self, components=None, external=_FRONTLINE_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        if components is None:
            components = _FRONTLINE_BATTLE_CLASSICS_COMPONENTS if self.sessionProvider.isReplayPlaying else _FRONTLINE_BATTLE_EXTENDED_COMPONENTS
        super(FrontlineBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__currPeriod = None
        self.__epicSoundControl = None
        self.__pageState = PageStates.COUNTDOWN
        self.__topState = PageStates.NONE
        self.__activeState = PageStates.NONE
        self.__respawnAvailable = False
        return

    @staticmethod
    def _swapVisibleStates(visibleUI, hiddenUI, value, fromVisibleUI=False):
        if fromVisibleUI and value in visibleUI:
            visibleUI.remove(value)
            hiddenUI.add(value)
        elif value in hiddenUI:
            hiddenUI.remove(value)
            visibleUI.add(value)

    def _invalidateState(self):
        if self.__topState != PageStates.NONE:
            targetState = self.__topState
        else:
            targetState = self.__pageState
        if targetState == PageStates.NONE or self.__activeState == targetState:
            return
        else:
            controlKey = (self.__activeState, self.sessionProvider.isReplayPlaying)
            if self.__activeState in _ENABLE_CONTROL_MODE and controlKey in _PAGE_STATE_TO_CONTROL_PARAMS:
                alias, _, _ = _PAGE_STATE_TO_CONTROL_PARAMS[controlKey]
                self.app.leaveGuiControlMode(alias)
            self.__activeState = targetState
            controlKey = (self.__activeState, self.sessionProvider.isReplayPlaying)
            if self.__activeState in _ENABLE_CONTROL_MODE and controlKey in _PAGE_STATE_TO_CONTROL_PARAMS:
                alias, p1, p2 = _PAGE_STATE_TO_CONTROL_PARAMS[controlKey]
                self.app.enterGuiControlMode(alias, cursorVisible=p1, enableAiming=p2)
            visibleUI = _STATE_TO_UI[targetState].copy()
            currVis = set(self.as_getComponentsVisibilityS())
            hiddenUI = currVis.difference(visibleUI)
            hiddenUI.difference_update(_NEVER_HIDE)
            visibleUI.update(_NEVER_HIDE)
            ctrl = self.sessionProvider.shared.vehicleState
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                if vehicle.typeDescriptor.hasSiegeMode or vehicle.isTrackWithinTrack:
                    self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
                else:
                    self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR, True)
                if vehicle.typeDescriptor.isDualgunVehicle:
                    self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL)
                else:
                    self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL, True)
                if vehicle.typeDescriptor.hasRocketAcceleration:
                    self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR)
                else:
                    self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR, True)
            ctrl = self.sessionProvider.dynamic.maps
            if ctrl:
                ctrl.setOverviewMapScreenVisibility(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN in visibleUI)
            ctrl = self.sessionProvider.shared.prebattleSetups
            if self.__activeState == PageStates.COUNTDOWN and ctrl and ctrl.isSelectionStarted():
                self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, True)
            if self.__respawnAvailable and self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL):
                self._swapVisibleStates(visibleUI, hiddenUI, BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, True)
            if targetState == PageStates.RESPAWN or targetState == PageStates.LOADING:
                visibleUI.difference_update(_NEVER_HIDE)
                hiddenUI.update(_NEVER_HIDE)
            self._setComponentsVisibility(visible=visibleUI, hidden=hiddenUI)
            return

    def _populate(self):
        super(FrontlineBattlePage, self)._populate()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            self.__arena_onPeriodChange(arena.period)
        self.__epicSoundControl = EpicBattleSoundController()
        self.__epicSoundControl.init()
        self.as_setVehPostProgressionEnabledS(True)
        return

    def _dispose(self):
        if self.__epicSoundControl is not None:
            self.__epicSoundControl.destroy()
            self.__epicSoundControl = None
        super(FrontlineBattlePage, self)._dispose()
        return

    def __arena_onPeriodChange(self, period, *args):
        if self.__currPeriod == period:
            return
        self.__currPeriod = period
        if period in (ARENA_PERIOD.WAITING, ARENA_PERIOD.IDLE):
            if self.__pageState != PageStates.COUNTDOWN:
                self.__pageState = PageStates.COUNTDOWN
                self._invalidateState()
        if period == ARENA_PERIOD.BATTLE:
            if self.__pageState == PageStates.COUNTDOWN:
                self.__pageState = PageStates.GAME
                self._invalidateState()

    def handleEscKey(self, isDown):
        isMapVisible = self.as_isComponentVisibleS(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN)
        if isMapVisible:
            self._setComponentsVisibility(hidden=[FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN, FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_DEPLOYMENT_MAP])
            self._toggleOverviewMap()
        return isMapVisible

    def _handleToggleOverviewMap(self, event):
        if not self._isVisible:
            return
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, event.ctx['key']):
            self._toggleOverviewMap()

    def _handleToggleFullStats(self, event):
        isDown = event.ctx['isDown']
        self._toggleFullStats(isDown)

    def _onBattleLoadingStart(self):
        self.__topState = PageStates.LOADING
        self._invalidateState()

    def _onBattleLoadingFinish(self):
        if self.__topState == PageStates.LOADING:
            self.__topState = PageStates.NONE
            self._invalidateState()
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

        if self.sessionProvider.shared.hitDirection is not None:
            self.sessionProvider.shared.hitDirection.setVisible(True)
        return

    def _toggleRadialMenu(self, isShown, allowAction=True):
        radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU)
        if radialMenu is None:
            return
        else:
            if not isShown and self.__topState == PageStates.RADIAL:
                self.__topState = PageStates.NONE
                radialMenu.hide(allowAction)
            elif isShown and self.__topState == PageStates.NONE and self.__pageState != PageStates.RESPAWN:
                self.__topState = PageStates.RADIAL
                radialMenu.show()
            else:
                return
            self._invalidateState()
            return

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        if not isShown and self.__topState == PageStates.TABSCREEN:
            self.__topState = PageStates.NONE
        elif isShown and self.__topState != PageStates.RADIAL:
            self.__checkOverviewMap()
            if self.__pageState == PageStates.RESPAWN:
                BigWorld.worldDrawEnabled(True)
            self.__topState = PageStates.TABSCREEN
        elif not isShown and self.__pageState == PageStates.RESPAWN:
            BigWorld.worldDrawEnabled(False)
        else:
            return
        self._invalidateState()

    def _toggleOverviewMap(self):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        if self.__topState == PageStates.OVERVIEWMAP:
            self.__topState = PageStates.NONE
        elif self.__topState == PageStates.NONE and self.__pageState != PageStates.RESPAWN or self.__topState == PageStates.TABSCREEN and self.__pageState != PageStates.RESPAWN:
            self.__topState = PageStates.OVERVIEWMAP
        else:
            return
        self._invalidateState()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(FrontlineBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        specCtrl = self.sessionProvider.shared.spectator
        if specCtrl is None:
            return
        else:
            self.__checkOverviewMap()
            self.__checkRadialMenu()
            self.__respawnAvailable = respawnAvailable
            if specCtrl.spectatorViewMode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
                self.__pageState = PageStates.SPECTATOR_FREE
            elif specCtrl.spectatorViewMode == EPIC_CONSTS.SPECTATOR_MODE_FOLLOW:
                self.__pageState = PageStates.SPECTATOR_FOLLOW
            elif specCtrl.spectatorViewMode == EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM:
                self.__pageState = PageStates.SPECTATOR_DEATHCAM
            else:
                return
            self._invalidateState()
            return

    def _handleGUIToggled(self, event):
        if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.FULL_STATS) and not self.as_isComponentVisibleS(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_RESPAWN_VIEW) and not self.as_isComponentVisibleS(FRONTLINE_BATTLE_VIEW_ALIASES.FRONTLINE_OVERVIEW_MAP_SCREEN):
            self._toggleGuiVisible()

    def __onSpectatorModeChanged(self, mode):
        if mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.__pageState = PageStates.SPECTATOR_FREE
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_FOLLOW:
            self.__pageState = PageStates.SPECTATOR_FOLLOW
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM:
            self.__pageState = PageStates.SPECTATOR_DEATHCAM
        else:
            return
        self._invalidateState()

    def __onRespawnVisibility(self, isVisible, fromTab=False):
        if not self._isVisible and isVisible:
            self._toggleGuiVisible()
        if isVisible and self.__topState == PageStates.TABSCREEN:
            self.__checkOverviewMap()
            self.__checkRadialMenu()
            self.__pageState = PageStates.RESPAWN
        elif isVisible and self.__pageState != PageStates.RESPAWN:
            self.__checkOverviewMap()
            self.__checkRadialMenu()
            self.__pageState = PageStates.RESPAWN
            BigWorld.worldDrawEnabled(False)
            for component in self._external:
                component.active(False)

        elif not isVisible and self.__pageState == PageStates.RESPAWN:
            self.__pageState = PageStates.GAME
            BigWorld.worldDrawEnabled(True)
            for component in self._external:
                component.active(True)

        else:
            if not isVisible and self.__pageState in (PageStates.SPECTATOR_FREE, PageStates.SPECTATOR_FOLLOW, PageStates.SPECTATOR_DEATHCAM):
                BigWorld.worldDrawEnabled(True)
            return
        self._invalidateState()

    def _onPostMortemReload(self):
        self.__onPostmortemDisable()
        super(FrontlineBattlePage, self)._onPostMortemReload()

    def __onPostmortemDisable(self):
        if not self._isInPostmortem:
            return
        self.__pageState = PageStates.GAME
        self._invalidateState()
        self._isInPostmortem = False

    def _onAvatarCtrlModeChanged(self, ctrlMode):
        pass

    def __onRoundFinished(self, winningTeam, reason):
        self.__pageState = PageStates.GAME_OVER
        self._invalidateState()

    def __checkOverviewMap(self):
        if self.__topState == PageStates.OVERVIEWMAP:
            ctrl = self.sessionProvider.dynamic.maps
            if ctrl:
                ctrl.overviewMapTriggered()

    def __checkRadialMenu(self):
        if self.__topState == PageStates.RADIAL:
            self._toggleRadialMenu(False)

    def _startBattleSession(self):
        super(FrontlineBattlePage, self)._startBattleSession()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__arena_onPeriodChange
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibility
            self.__onRespawnVisibility(ctrl.isRespawnVisible())
        self.addListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        specCtrl = self.sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
        return

    def _stopBattleSession(self):
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__arena_onPeriodChange
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibility
        self.removeListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        specCtrl = self.sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        super(FrontlineBattlePage, self)._stopBattleSession()
        return

    def onDeactivateRadialMenu(self):
        self.__checkRadialMenu()
