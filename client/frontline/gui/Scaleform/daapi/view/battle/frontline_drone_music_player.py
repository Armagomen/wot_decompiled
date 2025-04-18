# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_drone_music_player.py
from functools import partial
import time
import WWISE
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer, _Condition, _TimeRemainedCondition, _BaseCaptureCondition, _RtpcEvents, _Severity, _delegate, _initCondition, _MusicID
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_FRONTLINE_MUSIC_STATE_GROUP = 'STATE_epicnormandy_battle_music'
_SEVERITY_TO_MUSIC_ID = {_Severity.NONE: 'STATE_epicnormandy_battle_silence',
 _Severity.LOW: 'STATE_epicnormandy_battle_music_01',
 _Severity.MEDIUM: 'STATE_epicnormandy_battle_music_02',
 _Severity.HIGH: 'STATE_epicnormandy_battle_music_03',
 _Severity.VERY_HIGH: 'STATE_epicnormandy_battle_music_00'}

class _FrontlineCondition(_Condition):

    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        return False

    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        return False

    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        return False


class _FrontlineZoneTransitionCondition(_FrontlineCondition):

    def __init__(self, criticalValue):
        super(_FrontlineZoneTransitionCondition, self).__init__(criticalValue, _Severity.MEDIUM)
        self._initialized = True

    @_initCondition
    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        return self._updateValidValue(True) if waypointSectorTimeTuple[0] is not None else self._updateValidValue(False)


class _FrontlineMainObjectivesTotalHealthCondition(_FrontlineCondition):

    def __init__(self, criticalValue):
        super(_FrontlineMainObjectivesTotalHealthCondition, self).__init__(criticalValue, _Severity.HIGH)
        self._initialized = True

    @_initCondition
    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        if sessionProvider is None:
            return
        else:
            destructibleComponent = getattr(sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                return
            totalRemainingHealthPercentage = destructibleComponent.getTotalRemainingHealthPercentage()
            return self._updateValidValue(True) if totalRemainingHealthPercentage <= self.criticalValue else None


class _FrontlineMainObjectivesNumDestroyedCondition(_FrontlineCondition):

    def __init__(self, criticalValue):
        super(_FrontlineMainObjectivesNumDestroyedCondition, self).__init__(criticalValue, _Severity.HIGH)
        self._initialized = True

    @_initCondition
    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        if sessionProvider is None:
            return
        else:
            destructibleComponent = getattr(sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                return
            numDestroyedMainObjectives = destructibleComponent.getNumDestroyedEntities()
            return self._updateValidValue(True) if numDestroyedMainObjectives >= self.criticalValue else None


class _FrontlineRespawnViewCondition(_FrontlineCondition):

    def __init__(self, criticalValue):
        super(_FrontlineRespawnViewCondition, self).__init__(criticalValue, _Severity.VERY_HIGH)
        self._initialized = True

    @_initCondition
    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        return self._updateValidValue(isVisible)


class _FrontlineTimeRemainedCondition(_TimeRemainedCondition):

    def __init__(self, criticalValue):
        super(_FrontlineTimeRemainedCondition, self).__init__(criticalValue, _Severity.HIGH)
        self.__stopEpicTimeRemainedCooldown = None
        return

    def dispose(self):
        super(_FrontlineTimeRemainedCondition, self).dispose()
        if self.__stopEpicTimeRemainedCooldown is not None:
            BigWorld.cancelCallback(self.__stopEpicTimeRemainedCooldown)
            self.__stopEpicTimeRemainedCooldown = None
        return

    def _isCriticalAchieved(self):
        criticalTimeValue, musicStopPredelay = self.criticalValue
        if self._period is not None and self._totalTime is not None:
            self._initialized = True
        if self._period == ARENA_PERIOD.BATTLE and self._totalTime is not None and self._totalTime <= criticalTimeValue:
            if self.__stopEpicTimeRemainedCooldown is not None:
                BigWorld.cancelCallback(self.__stopEpicTimeRemainedCooldown)
                LOG_DEBUG('[EPIC Drone] Time Remained. Cooldown canceled')
                self.__stopEpicTimeRemainedCooldown = None
            return self._updateValidValue(True)
        else:
            if self.isSatisfied():
                criticalTimeValue, musicStopPredelay = self.criticalValue
                if self.__stopEpicTimeRemainedCooldown is None:
                    LOG_DEBUG('[EPIC Drone] Time Remained. Stop music EpicTimeRemainedCooldown has been started - musicStopPredelay: ', musicStopPredelay)
                    self.__stopEpicTimeRemainedCooldown = BigWorld.callback(musicStopPredelay, partial(self.__onEpicTimeRemainedCooldownOver, time.time()))
            return False

    def __onEpicTimeRemainedCooldownOver(self, startTime):
        LOG_DEBUG('[EPIC Drone] Time Remained. Cooldown ended. {} seconds passed. Music will be stopped.'.format(time.time() - startTime))
        self.__stopEpicTimeRemainedCooldown = None
        if self._updateValidValue(False):
            self.onValidChangedInternally()
        return

    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        pass

    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        pass

    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        pass


class _FrontlineBaseCaptureCondition(_BaseCaptureCondition):

    def __init__(self, criticalValue, severity):
        super(_FrontlineBaseCaptureCondition, self).__init__(criticalValue, severity)
        self.__baseCaptured = False

    def setTeamBaseCaptured(self, clientID, playerTeam):
        self.__baseCaptured = True

    def _validatePoints(self):
        criticalPointsCount, musicStopPredelay = self.criticalValue
        for points in self._pointsToBase.itervalues():
            if self._stopCapturingCooldown is not None and points:
                if self._stopCapturingCooldown is not None:
                    BigWorld.cancelCallback(self._stopCapturingCooldown)
                    LOG_DEBUG('[EPIC Drone] Base Capturing. Cooldown stopped')
                    self._stopCapturingCooldown = None
                return False
            if points >= criticalPointsCount:
                return self._updateValidValue(True)

        if self.isSatisfied() and self._stopCapturingCooldown is None:
            if self.__baseCaptured is True:
                self.__baseCaptured = False
            LOG_DEBUG('[EPIC Drone] Base Capturing. Stop music cooldown has been started - musicStopPredelay: ', musicStopPredelay)
            self._stopCapturingCooldown = BigWorld.callback(musicStopPredelay, partial(self._onCooldownOver, time.time()))
        return False

    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        pass

    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        pass

    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        pass


class _FrontlineAlliedBaseCaptureCondition(_FrontlineBaseCaptureCondition):

    def __init__(self, criticalValue):
        super(_FrontlineAlliedBaseCaptureCondition, self).__init__(criticalValue, _Severity.LOW)

    def _getValidBaseMask(self):
        pass

    def _getRtpcPointsID(self):
        return _RtpcEvents.ALLIES_BASE_POINTS_CAPTURING

    def _getRtpcInvadersCountID(self):
        return _RtpcEvents.ALLIES_INVADERS_COUNT

    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        pass

    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        pass

    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        pass


class _FrontlineEnemyBaseCaptureCondition(_FrontlineBaseCaptureCondition):

    def __init__(self, criticalValue):
        super(_FrontlineEnemyBaseCaptureCondition, self).__init__(criticalValue, _Severity.LOW)

    def _getValidBaseMask(self):
        pass

    def _getRtpcPointsID(self):
        return _RtpcEvents.ENEMIES_BASE_POINTS_CAPTURING

    def _getRtpcInvadersCountID(self):
        return _RtpcEvents.ENEMIES_INVADERS_COUNT

    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        pass

    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        pass

    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        pass


class FrontlineDroneMusicPlayer(DroneMusicPlayer):
    _SETTING_TO_CONDITION_MAPPING = {'timeRemained': (lambda player: True, (_FrontlineTimeRemainedCondition,), lambda name, key, data: (data[name].getValue(key), data['musicStopPredelay'].getValue(key))),
     'capturedPoints': (lambda player: True, (_FrontlineAlliedBaseCaptureCondition, _FrontlineEnemyBaseCaptureCondition), lambda name, key, data: (data[name].getValue(key), data['musicStopPredelay'].getValue(key))),
     'epicRespawnView': (lambda player: True, (_FrontlineRespawnViewCondition,), lambda name, key, data: data[name].getValue(key)),
     'epicMainObjectivesTotalHealth': (lambda player: True, (_FrontlineMainObjectivesTotalHealthCondition,), lambda name, key, data: data[name].getValue(key)),
     'epicMainObjectivesNumDestroyed': (lambda player: True, (_FrontlineMainObjectivesNumDestroyedCondition,), lambda name, key, data: data[name].getValue(key)),
     'epicZoneTransition': (lambda player: True, (_FrontlineZoneTransitionCondition,), lambda name, key, data: data[name].getValue(key))}

    def __init__(self):
        super(FrontlineDroneMusicPlayer, self).__init__()
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.onRespawnVisibilityChanged
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityHealthChanged += self.onDestructibleEntityHealthChanged
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        sectorComp = getattr(componentSystem, 'sectorComponent', None)
        if sectorComp is not None:
            sectorComp.onWaypointsForPlayerActivated += self.onWaypointsForPlayerActivated
        return

    def detachedFromCtrl(self, ctrlID):
        super(FrontlineDroneMusicPlayer, self).detachedFromCtrl(ctrlID)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.onRespawnVisibilityChanged
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityHealthChanged -= self.onDestructibleEntityHealthChanged
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        sectorComp = getattr(componentSystem, 'sectorComponent', None)
        if sectorComp is not None:
            sectorComp.onWaypointsForPlayerActivated -= self.onWaypointsForPlayerActivated
        return

    @_delegate
    def setTeamBaseCaptured(self, clientID, playerTeam):
        pass

    @_delegate
    def onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        pass

    @_delegate
    def onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        pass

    @_delegate
    def onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        pass

    def _validateConditions(self):
        isPlaying = self._playingMusicID is not None
        satisfied = [ c for c in self._conditions if c.isSatisfied() ]
        highestSeverity = _Severity.NONE
        if satisfied:
            for condition in satisfied:
                isPlaying = self._playingMusicID is not None
                if not isPlaying:
                    self._setPlayingMusicID(_MusicID.INTENSIVE)
                    self._playMusic()
                LOG_DEBUG('[EPIC Drone] Satisfied conditions: {}'.format(satisfied))
                if highestSeverity <= condition.getSeverity():
                    highestSeverity = condition.getSeverity()

            self.__setEpicMusicState(_FRONTLINE_MUSIC_STATE_GROUP, highestSeverity)
        elif isPlaying:
            self.__setEpicMusicState(_FRONTLINE_MUSIC_STATE_GROUP, _Severity.NONE)
        return

    def __setEpicMusicState(self, stateGroup, currentSeverity):
        musicStateID = _SEVERITY_TO_MUSIC_ID[currentSeverity]
        WWISE.WW_setState(stateGroup, musicStateID)
