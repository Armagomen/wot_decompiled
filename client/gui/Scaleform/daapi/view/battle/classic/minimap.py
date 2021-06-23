# Source Generated with Decompyle++
# File: minimap.pyc (Python 2.7)

import logging
import BattleReplay
import BigWorld
import CommandMapping
import Keys
import Math
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.settings_core import settings_constants
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, getBaseTeamAndIDFromUniqueID, MarkerType, getUniqueTeamOrControlPointID
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.Scaleform.daapi.view.battle.shared.minimap import common, plugins
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import _LOCATION_PING_RANGE, _BASE_PING_RANGE, _EMinimapMouseKey
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.battle_control import minimap_utils, avatar_getter
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger import MessengerEntry
from messenger.proto.bw_chat2.battle_chat_cmd import BASE_CMD_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_logger = logging.getLogger(__name__)
_CLASSIC_MINIMAP_DIMENSIONS = 10

class ClassicMinimapComponent(component.MinimapComponent):
    
    def _setupPlugins(self, arenaVisitor):
        setup = super(ClassicMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = GlobalSettingsPlugin
        setup['points'] = TeamsOrControlsPointsPlugin
        if not BattleReplay.g_replayCtrl.isPlaying:
            setup['pinging'] = ClassicMinimapPingPlugin
        if IS_DEVELOPMENT:
            setup['teleport'] = ClassicTeleportPlugin
        return setup

    
    def hasMinimapGrid(self):
        return True

    
    def getMinimapDimensions(self):
        return _CLASSIC_MINIMAP_DIMENSIONS



class GlobalSettingsPlugin(common.SimplePlugin):
    __slots__ = ('__currentSizeSettings', '__isVisible', '__sizeIndex')
    _AccountSettingsClass = AccountSettings
    
    def __init__(self, parentObj):
        super(GlobalSettingsPlugin, self).__init__(parentObj)
        self._GlobalSettingsPlugin__currentSizeSettings = 'minimapSize'
        self._GlobalSettingsPlugin__isVisible = True
        self._GlobalSettingsPlugin__sizeIndex = 0

    
    def start(self):
        super(GlobalSettingsPlugin, self).start()
        if GUI_SETTINGS.minimapSize:
            g_eventBus.addListener(events.GameEvent.MINIMAP_CMD, self._GlobalSettingsPlugin__handleMinimapCmd, scope = EVENT_BUS_SCOPE.BATTLE)
            g_repeatKeyHandlers.add(self._GlobalSettingsPlugin__handleRepeatKeyEvent)

    
    def stop(self):
        if GUI_SETTINGS.minimapSize:
            g_eventBus.removeListener(events.GameEvent.MINIMAP_CMD, self._GlobalSettingsPlugin__handleMinimapCmd, scope = EVENT_BUS_SCOPE.BATTLE)
            g_repeatKeyHandlers.discard(self._GlobalSettingsPlugin__handleRepeatKeyEvent)
        super(GlobalSettingsPlugin, self).stop()

    
    def setSettings(self):
        newSize = settings.clampMinimapSizeIndex(self._AccountSettingsClass.getSettings(self._GlobalSettingsPlugin__currentSizeSettings))
        if self._GlobalSettingsPlugin__sizeIndex != newSize:
            self._GlobalSettingsPlugin__sizeIndex = newSize
            self._parentObj.as_setSizeS(self._GlobalSettingsPlugin__sizeIndex)
        self._GlobalSettingsPlugin__updateAlpha()

    
    def updateSettings(self, diff):
        if settings_constants.GAME.MINIMAP_ALPHA in diff or settings_constants.GAME.MINIMAP_ALPHA_ENABLED in diff:
            self._GlobalSettingsPlugin__updateAlpha()

    
    def applyNewSize(self, sizeIndex):
        LOG_DEBUG('Size index of minimap is changed', sizeIndex)
        self._GlobalSettingsPlugin__sizeIndex = sizeIndex
        self._GlobalSettingsPlugin__saveSettings()

    
    def _changeSizeSettings(self, newSizeSettings):
        if newSizeSettings == self._GlobalSettingsPlugin__currentSizeSettings:
            return newSizeSettings
        previousSettings = None._GlobalSettingsPlugin__currentSizeSettings
        self._GlobalSettingsPlugin__currentSizeSettings = newSizeSettings
        self.setSettings()
        return previousSettings

    
    def _toogleVisible(self):
        self._GlobalSettingsPlugin__isVisible = not (self._GlobalSettingsPlugin__isVisible)
        self._parentObj.as_setVisibleS(self._GlobalSettingsPlugin__isVisible)

    
    def _GlobalSettingsPlugin__saveSettings(self):
        self._AccountSettingsClass.setSettings(self._GlobalSettingsPlugin__currentSizeSettings, self._GlobalSettingsPlugin__sizeIndex)

    
    def _GlobalSettingsPlugin__setSizeByStep(self, step):
        newIndex = settings.clampMinimapSizeIndex(self._GlobalSettingsPlugin__sizeIndex + step)
        if self._GlobalSettingsPlugin__sizeIndex != newIndex:
            LOG_DEBUG('Try to change size index of minimap by step', newIndex)
            self._parentObj.as_setSizeS(newIndex)

    
    def _GlobalSettingsPlugin__handleKey(self, key):
        if self._parentObj.isModalViewShown():
            return None
        cmdMap = None.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_DOWN, key):
            self._GlobalSettingsPlugin__setSizeByStep(-1)
        elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_UP, key):
            self._GlobalSettingsPlugin__setSizeByStep(1)
        elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
            self._toogleVisible()

    
    def _GlobalSettingsPlugin__handleRepeatKeyEvent(self, event):
        if MessengerEntry.g_instance.gui.isFocused():
            return None
        if None.isRepeatedEvent() and event.isKeyDown() and not BigWorld.isKeyDown(Keys.KEY_RSHIFT) and CommandMapping.g_instance.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP), event.key):
            self._GlobalSettingsPlugin__handleKey(event.key)

    
    def _GlobalSettingsPlugin__handleMinimapCmd(self, event):
        self._GlobalSettingsPlugin__handleKey(event.ctx['key'])

    
    def _GlobalSettingsPlugin__updateAlpha(self):
        if self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_ALPHA_ENABLED):
            value = int(self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_ALPHA))
        else:
            value = 0
        self._parentObj.as_setAlphaS(1 - value / 100)



class TeamsOrControlsPointsPlugin(common.EntriesPlugin):
    __slots__ = ('__personalTeam', '__entries', '__markerIDs', '__hasActiveCommit')
    
    def __init__(self, parentObj):
        super(TeamsOrControlsPointsPlugin, self).__init__(parentObj)
        self._TeamsOrControlsPointsPlugin__personalTeam = 0
        self._TeamsOrControlsPointsPlugin__entries = []
        self._TeamsOrControlsPointsPlugin__markerIDs = { }
        self._TeamsOrControlsPointsPlugin__hasActiveCommit = False

    
    def start(self):
        super(TeamsOrControlsPointsPlugin, self).start()
        g_playerEvents.onTeamChanged += self._TeamsOrControlsPointsPlugin__onTeamChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self._TeamsOrControlsPointsPlugin__onActionAddedToMarkerReceived
            ctrl.onReplyFeedbackReceived += self._TeamsOrControlsPointsPlugin__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self._TeamsOrControlsPointsPlugin__onRemoveCommandReceived
        self.restart()

    
    def stop(self):
        g_playerEvents.onTeamChanged -= self._TeamsOrControlsPointsPlugin__onTeamChanged
        super(TeamsOrControlsPointsPlugin, self).stop()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self._TeamsOrControlsPointsPlugin__onActionAddedToMarkerReceived
            ctrl.onReplyFeedbackReceived -= self._TeamsOrControlsPointsPlugin__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self._TeamsOrControlsPointsPlugin__onRemoveCommandReceived

    
    def restart(self):
        for x in self._TeamsOrControlsPointsPlugin__entries:
            self._delEntry(x)
        
        self._TeamsOrControlsPointsPlugin__entries = []
        self._TeamsOrControlsPointsPlugin__personalTeam = self._arenaDP.getNumberOfTeam()
        self._TeamsOrControlsPointsPlugin__addTeamSpawnPoints()
        self._TeamsOrControlsPointsPlugin__addTeamBasePositions()
        self._TeamsOrControlsPointsPlugin__addControlPoints()

    
    def _TeamsOrControlsPointsPlugin__onActionAddedToMarkerReceived(self, senderID, commandID, markerType, objectID):
        if _ACTIONS.battleChatCommandFromActionID(commandID).name not in BASE_CMD_NAMES:
            return None
        if None not in self._TeamsOrControlsPointsPlugin__markerIDs:
            return None
        model = None._TeamsOrControlsPointsPlugin__markerIDs[objectID]
        if model is not None:
            if _ACTIONS.battleChatCommandFromActionID(commandID).name in [
                BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
                BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE]:
                self._TeamsOrControlsPointsPlugin__onReplyFeedbackReceived(objectID, senderID, MarkerType.BASE_MARKER_TYPE, 0, 1)
            else:
                self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_ATTACK)

    
    def _TeamsOrControlsPointsPlugin__onReplyFeedbackReceived(self, ucmdID, replierID, markerType, oldReplyCount, newReplyCount):
        if markerType != MarkerType.BASE_MARKER_TYPE:
            return None
        newReply = None > oldReplyCount
        playerHasReply = replierID == avatar_getter.getPlayerVehicleID()
        if ucmdID in self._TeamsOrControlsPointsPlugin__markerIDs and newReply:
            if playerHasReply:
                self._invoke(self._TeamsOrControlsPointsPlugin__markerIDs[ucmdID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_REPLY)
                self._TeamsOrControlsPointsPlugin__hasActiveCommit = True
            elif not self._TeamsOrControlsPointsPlugin__hasActiveCommit:
                self._invoke(self._TeamsOrControlsPointsPlugin__markerIDs[ucmdID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_IDLE)
            
        if ucmdID in self._TeamsOrControlsPointsPlugin__markerIDs:
            if newReplyCount < oldReplyCount or playerHasReply or newReplyCount <= 0:
                self._invoke(self._TeamsOrControlsPointsPlugin__markerIDs[ucmdID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_IDLE)
                if playerHasReply:
                    self._TeamsOrControlsPointsPlugin__hasActiveCommit = False
                
            

    
    def _TeamsOrControlsPointsPlugin__onRemoveCommandReceived(self, removeID, markerType):
        if not (self._TeamsOrControlsPointsPlugin__markerIDs) or markerType != MarkerType.BASE_MARKER_TYPE:
            return None
        if None in self._TeamsOrControlsPointsPlugin__markerIDs:
            self._invoke(self._TeamsOrControlsPointsPlugin__markerIDs[removeID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
            return None
        None.error(str(removeID) + ' not found in markerIDs')

    
    def _TeamsOrControlsPointsPlugin__onTeamChanged(self, teamID):
        self.restart()

    
    def _TeamsOrControlsPointsPlugin__addBaseEntry(self, symbol, position, uid):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        model = self._addEntryEx(uid, symbol, _C_NAME.TEAM_POINTS, matrix = matrix, active = True)
        if model is not None:
            self._TeamsOrControlsPointsPlugin__markerIDs[uid] = model
            (_, number) = getBaseTeamAndIDFromUniqueID(uid)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_POINT_NUMBER, number)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)

    
    def _TeamsOrControlsPointsPlugin__addPointEntry(self, symbol, position, number):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _C_NAME.TEAM_POINTS, matrix = matrix, active = True)
        if entryID:
            self._invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_POINT_NUMBER, number)
            self._TeamsOrControlsPointsPlugin__entries.append(entryID)

    
    def _TeamsOrControlsPointsPlugin__addTeamSpawnPoints(self):
        points = self._arenaVisitor.getTeamSpawnPointsIterator(self._TeamsOrControlsPointsPlugin__personalTeam)
        for (team, position, number) in points:
            if team == self._TeamsOrControlsPointsPlugin__personalTeam:
                symbol = _S_NAME.ALLY_TEAM_SPAWN
            else:
                symbol = _S_NAME.ENEMY_TEAM_SPAWN
            self._TeamsOrControlsPointsPlugin__addPointEntry(symbol, position, number)
        

    
    def _TeamsOrControlsPointsPlugin__addTeamBasePositions(self):
        positions = self._arenaVisitor.type.getTeamBasePositionsIterator()
        for (team, position, number) in positions:
            if team == self._TeamsOrControlsPointsPlugin__personalTeam:
                symbol = _S_NAME.ALLY_TEAM_BASE
            else:
                symbol = _S_NAME.ENEMY_TEAM_BASE
            uid = getUniqueTeamOrControlPointID(team, number)
            self._TeamsOrControlsPointsPlugin__addBaseEntry(symbol, position, uid)
        

    
    def _TeamsOrControlsPointsPlugin__addControlPoints(self):
        points = self._arenaVisitor.type.getControlPointsIterator()
        for (position, number) in points:
            uid = getUniqueTeamOrControlPointID(0, number)
            self._TeamsOrControlsPointsPlugin__addBaseEntry(_S_NAME.CONTROL_POINT, position, uid)
        



class ClassicMinimapPingPlugin(plugins.MinimapPingPlugin):
    
    def _getClickPosition(self, x, y):
        return minimap_utils.makePointMatrixByLocal(x, y, *self._boundingBox).translation

    
    def _getIdByBaseNumber(self, team, number):
        return getUniqueTeamOrControlPointID(team, number)

    
    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        bases = self._ClassicMinimapPingPlugin__getNearestBaseForPosition(position, _BASE_PING_RANGE)
        if bases is not None:
            self._make3DPingBases(commands, bases)
            return None
        locationID = None._getNearestLocationIDForPosition(position, _LOCATION_PING_RANGE)
        if locationID is not None:
            self._replyPing3DMarker(commands, locationID)
            return None
        None.sendAttentionToPosition3D(position, locationCommand)

    
    def _ClassicMinimapPingPlugin__getNearestBaseForPosition(self, inPosition, range_):
        positions = self._arenaVisitor.type.getTeamBasePositionsIterator()
        minVal = None
        for (team, position, number) in positions:
            if minVal is None:
                minVal = (team, position, number)
                continue
            if Math.Vector3(position).flatDistTo(inPosition) < Math.Vector3(minVal[1]).flatDistTo(inPosition):
                minVal = (team, position, number)
                continue
        for (posControl, number) in self._arenaVisitor.type.getControlPointsIterator():
            if minVal is None:
                minVal = (0, posControl, number)
                continue
            if Math.Vector3(posControl).flatDistTo(inPosition) < Math.Vector3(minVal[1]).flatDistTo(inPosition):
                minVal = (0, posControl, number)
                continue
        if minVal is None:
            return None
        if None.Vector3(minVal[1]).flatDistTo(inPosition) <= range_:
            return minVal



class ClassicTeleportPlugin(ClassicMinimapPingPlugin):
    
    def onMinimapClicked(self, x, y, buttonIdx, minimapScaleIndex):
        if buttonIdx != _EMinimapMouseKey.KEY_MBL.value:
            return None
        player = None.player()
        if player is not None and player.isTeleport:
            position = self._getClickPosition(x, y)
            result = BigWorld.collide(player.spaceID, (position.x, 1000, position.z), (position.x, -1000, position.z))
            player.base.vehicle_teleport((position[0], result[0][1], position[2]), 0)


