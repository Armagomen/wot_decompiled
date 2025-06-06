# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/ammo_ctrl.py
import logging
import typing
import weakref
from collections import namedtuple, defaultdict
from math import fabs, ceil
import BigWorld
import CommandMapping
import Event
import math_utils
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import VEHICLE_SETTING, ReloadRestriction, ARENA_PERIOD
from shared_utils import CONST_CONTAINER, first
from debug_utils import LOG_CODEPOINT_WARNING, LOG_ERROR
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import SHELL_SET_RESULT, CANT_SHOOT_ERROR, BATTLE_CTRL_ID, SHELL_QUANTITY_UNKNOWN
from gui.battle_control.view_components import ViewComponentsController
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.decorators import ReprInjector
from gui.Scaleform.genConsts.AUTOLOADERBOOSTVIEWSTATES import AUTOLOADERBOOSTVIEWSTATES
from ReloadEffect import ReloadEffectStrategy
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
__all__ = ('AmmoController', 'AmmoReplayPlayer')
_ClipBurstSettings = namedtuple('_ClipBurstSettings', 'size interval')
_HUNDRED_PERCENT = 100.0
_DualGunShellChangeTime = namedtuple('_DualGunShellChangeTime', 'left right activeIdx')
_TIME_CORRECTION_THRESHOLD = 0.01
_IGNORED_RELOADING_TIME = 0.15
_DUPLET_SHELLS_AMOUNT = 2
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import Shell
    from items.vehicle_items import Gun

class _GunSettings(namedtuple('_GunSettings', ('clip',
 'burst',
 'shots',
 'reloadEffect',
 'autoReload',
 'autoShoot',
 'isDualGun',
 'twinGunFactor',
 'shellChangeFactor'))):

    @classmethod
    def default(cls):
        return cls.__new__(cls, _ClipBurstSettings(1, 0.0), _ClipBurstSettings(1, 0.0), {}, None, None, None, False, 0.0, 0.0)

    @classmethod
    def make(cls, gun):
        shots = {}
        clip = _ClipBurstSettings(*gun.clip)
        burst = _ClipBurstSettings(*gun.burst)
        reloadEffect = None
        reloadEffectDesc = gun.reloadEffect
        if reloadEffectDesc is not None:
            reloadEffect = ReloadEffectStrategy(reloadEffectDesc)
        for shotIdx, shotDescr in enumerate(gun.shots):
            nationID, itemID = shotDescr.shell.id
            intCD = vehicles.makeIntCompactDescrByID('shell', nationID, itemID)
            shots[intCD] = (shotIdx,
             shotDescr.piercingPower[0],
             shotDescr.speed,
             shotDescr.shell)

        isDualGun = 'dualGun' in gun.tags
        isAutoReload = 'autoreload' in gun.tags
        autoReload = gun.autoreload if isAutoReload else None
        autoShoot = gun.autoShoot if 'autoShoot' in gun.tags else None
        twinGunFactor = gun.twinGun.twinGunReloadTime / gun.reloadTime if 'twinGun' in gun.tags else 0.0
        shellChangeFactor = gun.forcedReloadTime / (gun.autoreload.reloadTime[-1] if isAutoReload else gun.reloadTime)
        return cls.__new__(cls, clip, burst, shots, reloadEffect, autoReload, autoShoot, isDualGun, twinGunFactor, shellChangeFactor)

    def isCassetteClip(self):
        return self.clip.size > 1 or self.burst.size > 1

    def isBurstAndClip(self):
        return self.clip.size > 1 and self.burst.size > 1

    def isTwinGun(self):
        return self.twinGunFactor > 0.0

    def hasAutoShoot(self):
        return self.autoShoot is not None

    def hasAutoReload(self):
        return self.autoReload is not None

    def hasShellChangeFactor(self):
        return self.shellChangeFactor > 0.0

    def getClipInterval(self):
        return 0.0 if self.hasAutoShoot() else self.clip.interval

    def getLastAmmoCount(self, shellsAmount):
        lastAmmoCount = shellsAmount if shellsAmount > 0 else 1
        lastAmmoCount = self.burst.size if self.isBurstAndClip() else lastAmmoCount
        return self.clip.size if self.hasAutoShoot() else lastAmmoCount

    def getPiercingPower(self, intCD):
        if intCD in self.shots:
            power = self.shots[intCD][1]
        else:
            power = 0
        return power

    def getShellChangeFactor(self):
        return self.shellChangeFactor if self.hasShellChangeFactor() else 1.0

    def getShellDescriptor(self, intCD):
        if intCD in self.shots:
            shellDescriptor = self.shots[intCD][3]
        else:
            shellDescriptor = vehicles.getItemByCompactDescr(intCD)
        return shellDescriptor

    def getShotIndex(self, intCD):
        if intCD in self.shots:
            index = self.shots[intCD][0]
        else:
            index = -1
        return index

    def getShotSpeed(self, intCD):
        if intCD in self.shots:
            speed = self.shots[intCD][2]
        else:
            speed = -1
        return speed

    def getTwinGunFactor(self, currShellsAmount, nextShellsAmount):
        if currShellsAmount > nextShellsAmount:
            return 1.0 / self.twinGunFactor
        return self.twinGunFactor if currShellsAmount < nextShellsAmount else 1.0


class AutoReloadingBoostStates(CONST_CONTAINER):
    UNAVAILABLE = 'unavailable'
    INAPPLICABLE = 'inapplicable'
    WAITING_FOR_START = 'waiting_for_start'
    CHARGING = 'charging'
    CHARGED = 'charged'
    NOT_ACTIVE = (UNAVAILABLE, INAPPLICABLE)


class IAmmoListener(object):

    @property
    def isActive(self):
        return False

    def handleAmmoKey(self, key):
        pass

    def setCurrentShellCD(self, shellCD):
        pass

    def setNextShellCD(self, shellCD):
        pass


class IGunReloadingSnapshot(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError

    def isReloading(self):
        raise NotImplementedError

    def getActualValue(self):
        raise NotImplementedError

    def getBaseValue(self):
        raise NotImplementedError

    def isReloadingFinished(self):
        raise NotImplementedError


class IGunReloadingState(IGunReloadingSnapshot):
    __slots__ = ()

    def getSnapshot(self):
        raise NotImplementedError

    def startPredictedReloading(self, usePrediction, gunSettings):
        raise NotImplementedError

    def stopPredicateReloading(self):
        raise NotImplementedError


@ReprInjector.simple(('_actualTime', 'actual'), ('_baseTime', 'base'), ('getTimePassed', 'timePassed'), ('getTimeLeft', 'timeLeft'), ('isReloading', 'reloading'), ('isReloadingFinished', 'reloadingFinished'))
class ReloadingTimeSnapshot(IGunReloadingSnapshot):
    __slots__ = ('_actualTime', '_baseTime', '_startTime', '_updateTime', '_waitReloadingStartResponse')

    def __init__(self, actualTime=0.0, baseTime=0.0, startTime=0.0, updateTime=0.0, waitReloadingStartResponse=False):
        super(ReloadingTimeSnapshot, self).__init__()
        self._actualTime = actualTime
        self._baseTime = baseTime
        self._startTime = startTime
        self._updateTime = updateTime
        self._waitReloadingStartResponse = waitReloadingStartResponse

    def clear(self):
        self._actualTime = 0.0
        self._baseTime = 0.0
        self._startTime = 0.0
        self._updateTime = 0.0
        self._waitReloadingStartResponse = False

    def isReloading(self):
        return True if self._waitReloadingStartResponse else self._actualTime > 0

    def isReloadingFinished(self):
        return False if self._waitReloadingStartResponse else self._actualTime == 0

    def getActualValue(self):
        return self._actualTime

    def getBaseValue(self):
        return self._baseTime

    def getTimePassed(self):
        return self.__getTimePassedFrom(self._startTime)

    def getTimeLeft(self):
        return max(0.0, self._actualTime - self.__getTimePassedFrom(self._updateTime)) if not self.isReloadingFinished() else 0.0

    def __getTimePassedFrom(self, specifiedTime):
        return max(0.0, BigWorld.timeExact() - specifiedTime) if not self.isReloadingFinished() else 0.0


class ReloadingTimeState(ReloadingTimeSnapshot, IGunReloadingState):
    __slots__ = ('_startTime', '_baseTime', '_actualTime', '_updateTime', '_waitReloadingStartResponse')

    def getSnapshot(self):
        return ReloadingTimeSnapshot(actualTime=self._actualTime, baseTime=self._baseTime, startTime=self._startTime, updateTime=self._updateTime, waitReloadingStartResponse=self._waitReloadingStartResponse)

    def startPredictedReloading(self, usePrediction, gunSettings):
        self._waitReloadingStartResponse = not gunSettings.hasAutoShoot() and usePrediction

    def stopPredicateReloading(self):
        self._waitReloadingStartResponse = False

    def setTimes(self, actualTime, baseTime):
        if actualTime > 0:
            correction = baseTime - actualTime
            if correction > _TIME_CORRECTION_THRESHOLD:
                self._startTime = BigWorld.timeExact() - correction
            else:
                self._startTime = BigWorld.timeExact()
            self._updateTime = BigWorld.timeExact()
        else:
            self._startTime = 0.0
            self._updateTime = 0.0
        if actualTime == 0:
            self.stopPredicateReloading()
        self._actualTime = actualTime
        self._baseTime = baseTime


class _AutoShootsCtrl(object):
    __slots__ = ('__proxy', '__isStarted', '__callbackID')

    def __init__(self, proxy):
        super(_AutoShootsCtrl, self).__init__()
        self.__proxy = proxy
        self.__isStarted = False
        self.__callbackID = None
        return

    def destroy(self):
        self.reset()
        self.__proxy = None
        return

    def reset(self):
        self.__clearCallback()
        self.__isStarted = False

    def process(self, timeLeft, prevTimeLeft):
        result = self.__isStarted
        if self.__isStarted:
            self.__clearCallback()
            if not timeLeft:
                self.__setCallback(_IGNORED_RELOADING_TIME + 0.01)
            if timeLeft >= _IGNORED_RELOADING_TIME:
                self.__isStarted = result = False
        elif 0 < timeLeft < _IGNORED_RELOADING_TIME:
            if prevTimeLeft == -1:
                self.__isStarted = result = True
            elif prevTimeLeft == 0:
                result = True
        return result

    def __setCallback(self, reloadTime):
        self.__callbackID = BigWorld.callback(reloadTime + 0.01, self.__update)

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __update(self):
        self.__callbackID = None
        if self.__proxy:
            self.__isStarted = False
            self.__proxy.refreshGunReloading()
        return


class _AutoReloadingBoostStateCtrl(object):
    __slots__ = ('__changeEventDispatcher', '__state', '__stateDuration', '__stateTotalTime', '__nextStateCallbackID', '__snapshot', '__prevSnapshot', '__gunSettings', '__serverClipTime')
    _SHOOT_MIN_TIME_TRASHOLD = 0.2

    def __init__(self, changeEvtDispatcher):
        super(_AutoReloadingBoostStateCtrl, self).__init__()
        self.__changeEventDispatcher = changeEvtDispatcher
        self.__state = None
        self.__stateDuration = 0.0
        self.__stateTotalTime = 0.0
        self.__prevSnapshot = None
        self.__snapshot = None
        self.__nextStateCallbackID = None
        self.__gunSettings = None
        self.__serverClipTime = None
        return

    def clear(self):
        self.__cancelCallback()
        self.__state = self.__prevSnapshot = self.__snapshot = self.__gunSettings = None
        self.__stateDuration = self.__stateTotalTime = 0.0
        return

    def destroy(self):
        self.__changeEventDispatcher = None
        self.__prevSnapshot = None
        self.__snapshot = None
        self.__gunSettings = None
        self.__cancelCallback()
        return

    def setReloadingTimeSnapshot(self, snapshot, isBoostApplicable, gunSettings, clipTime=None):
        self.__prevSnapshot = self.__snapshot
        self.__snapshot = snapshot
        self.__gunSettings = gunSettings
        self.__serverClipTime = clipTime
        newState, newStateDuration, totalTime, extraData = self.__getNewState(isBoostApplicable)
        if newState != self.__state or newStateDuration != self.__stateDuration or totalTime != self.__stateTotalTime:
            self.__cancelCallback()
            self.__updateState(newState, newStateDuration, totalTime, extraData)
            self.__scheduleNextState()

    def __getNewState(self, isBoostApplicable):
        autoReloadSetting = self.__gunSettings.autoReload
        if autoReloadSetting is None:
            return (AutoReloadingBoostStates.UNAVAILABLE,
             0.0,
             0.0,
             {})
        gunHasBoostAbility = autoReloadSetting.boostFraction < 1.0
        if not gunHasBoostAbility:
            return (AutoReloadingBoostStates.UNAVAILABLE,
             0.0,
             0.0,
             {})
        elif not isBoostApplicable:
            shootHasBeenMade = False
            previousState = self.__state
            if previousState == AutoReloadingBoostStates.CHARGING:
                shootHasBeenMade = True
            elif previousState == AutoReloadingBoostStates.CHARGED:
                if self.__prevSnapshot:
                    if self.__prevSnapshot.getTimeLeft() > self._SHOOT_MIN_TIME_TRASHOLD:
                        shootHasBeenMade = True
            return (AutoReloadingBoostStates.INAPPLICABLE,
             0.0,
             0.0,
             {'shootHasBeenMade': shootHasBeenMade})
        else:
            return self.__getCurrentBoostTimelineState()

    def __getCurrentBoostTimelineState(self):
        autoReloadSetting = self.__gunSettings.autoReload
        if autoReloadSetting is None:
            return (AutoReloadingBoostStates.UNAVAILABLE,
             0.0,
             0.0,
             {})
        else:
            timePassed = self.__snapshot.getTimePassed()
            fullReloadingTime = self.__snapshot.getBaseValue()
            timeBetweenShots = self.__serverClipTime or self.__gunSettings.clip[1]
            boostStartDelay = timeBetweenShots + autoReloadSetting.boostStartTime
            if boostStartDelay > timePassed:
                timeToStartBoostCharging = boostStartDelay - timePassed
                if self.__state == AutoReloadingBoostStates.WAITING_FOR_START:
                    self.__resetWaitingToStart()
                return (AutoReloadingBoostStates.WAITING_FOR_START,
                 timeToStartBoostCharging,
                 boostStartDelay,
                 {})
            fullChargeTime = fullReloadingTime - autoReloadSetting.boostResidueTime
            return (AutoReloadingBoostStates.CHARGED,
             0.0,
             0.0,
             {}) if fullChargeTime < timePassed else (AutoReloadingBoostStates.CHARGING,
             fullChargeTime - timePassed,
             fullChargeTime - boostStartDelay,
             {})

    def __resetWaitingToStart(self):
        self.__changeEventDispatcher('', AUTOLOADERBOOSTVIEWSTATES.INVISIBLE, 0.0, {})

    def __onTimeForStateHasCome(self):
        self.__nextStateCallbackID = None
        self.__updateState(*self.__getCurrentBoostTimelineState())
        self.__scheduleNextState()
        return

    def __scheduleNextState(self):
        if self.__stateDuration > 0.0:
            self.__nextStateCallbackID = BigWorld.callback(self.__stateDuration, self.__onTimeForStateHasCome)

    def __cancelCallback(self):
        if self.__nextStateCallbackID is not None:
            BigWorld.cancelCallback(self.__nextStateCallbackID)
            self.__nextStateCallbackID = None
        return

    def __updateState(self, state, stateDuration, stateTotalTime, extraData):
        self.__state = state
        self.__stateDuration = stateDuration
        self.__stateTotalTime = stateTotalTime
        self.__changeEventDispatcher(state, stateDuration, stateTotalTime, extraData)


class AmmoController(MethodsRules, ViewComponentsController):
    __slots__ = ('__eManager', 'onShellsAdded', 'onShellsUpdated', 'onNextShellChanged', 'onCurrentShellChanged', 'onGunSettingsSet', 'onGunReloadTimeSet', 'onGunAutoReloadTimeSet', 'onGunAutoReloadBoostUpdated', '_autoReloadingBoostState', 'onShellsCleared', '__ammo', '_order', '__currShellCD', '__nextShellCD', '__gunSettings', '_reloadingState', '_autoReloadingState', '__autoShoots', '__weakref__', 'onDebuffStarted', '__quickChangerActive', 'onShellChangeTimeUpdated', '__shellChangeTime', '__quickChangerFactor', '__dualGunShellChangeTime', '__dualGunQuickChangeReady', '__quickChangerInProcess', '__infinity')
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, reloadingState=None):
        super(AmmoController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onShellsAdded = Event.Event(self.__eManager)
        self.onShellsUpdated = Event.Event(self.__eManager)
        self.onNextShellChanged = Event.Event(self.__eManager)
        self.onCurrentShellChanged = Event.Event(self.__eManager)
        self.onCurrentShellReset = Event.Event(self.__eManager)
        self.onGunSettingsSet = Event.Event(self.__eManager)
        self.onGunReloadTimeSet = Event.Event(self.__eManager)
        self.onDebuffStarted = Event.Event(self.__eManager)
        self.onGunAutoReloadTimeSet = Event.Event(self.__eManager)
        self.onGunAutoReloadBoostUpdated = Event.Event(self.__eManager)
        self.onShellChangeTimeUpdated = Event.Event(self.__eManager)
        self.onShellsCleared = Event.Event(self.__eManager)
        self.__ammo = {}
        self.__infinity = defaultdict(int)
        self._order = []
        self._reloadingState = reloadingState or ReloadingTimeState()
        self._autoReloadingState = ReloadingTimeState()
        self._autoReloadingBoostState = _AutoReloadingBoostStateCtrl(self.onGunAutoReloadBoostUpdated)
        self.__currShellCD = None
        self.__nextShellCD = None
        self.__gunSettings = _GunSettings.default()
        self.__autoShoots = _AutoShootsCtrl(weakref.proxy(self))
        self.__quickChangerActive = False
        self.__shellChangeTime = 0.0
        self.__dualGunShellChangeTime = _DualGunShellChangeTime(0.0, 0.0, 0)
        self.__quickChangerFactor = 0.0
        self.__dualGunQuickChangeReady = False
        self.__quickChangerInProcess = False
        return

    def __repr__(self):
        return '{0:>s}(ammo = {1!r:s}, current = {2!r:s}, next = {3!r:s}, gun = {4!r:s})'.format(self.__class__.__name__, self.__ammo, self.__currShellCD, self.__nextShellCD, self.__gunSettings)

    def getControllerID(self):
        return BATTLE_CTRL_ID.AMMO

    def startControl(self):
        pass

    def stopControl(self):
        self.clear(leave=True)

    def clear(self, leave=True):
        super(AmmoController, self).clear(True)
        if leave:
            self.__eManager.clear()
        self.clearAmmo()
        reloadEffect = self.__gunSettings.reloadEffect
        if reloadEffect is not None:
            reloadEffect.stop()
        self.__gunSettings = _GunSettings.default()
        self._reloadingState.clear()
        self._autoReloadingBoostState.clear()
        if leave:
            self.__autoShoots.destroy()
            self._autoReloadingBoostState.destroy()
            self.__dualGunQuickChangeReady = False
            self.__quickChangerInProcess = False
            self.__quickChangerActive = False
        else:
            self.onShellsCleared(self._reloadingState.getSnapshot())
        return

    def setViewComponents(self, *components):
        super(AmmoController, self).setViewComponents(*components)
        for component in components:
            component.setCurrentShellCD(self.__currShellCD)
            component.setNextShellCD(self.__nextShellCD)

    def getGunSettings(self):
        return self.__gunSettings

    def updateForNewSetup(self, gun, shells):
        currentShellCD, nextShellCD = self.getCurrentShellCD(), self.getNextShellCD()
        self.clear(leave=False)
        self.setGunSettings(gun)
        for shell in shells:
            self.setShells(shell.intCD, shell.count, 0)

        self.resetShellsSettings(currentShellCD, nextShellCD)

    def resetShellsSettings(self, currentShellCD, nextShellCD):
        if self.shellInAmmo(currentShellCD):
            curQuantity, _ = self.__ammo[currentShellCD]
            if curQuantity <= 0:
                currentShellCD = self.__getFirstAvailableShell()
        elif currentShellCD is None:
            currentShellCD = self.__getFirstAvailableShell()
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as current.', currentShellCD)
        if self.shellInAmmo(nextShellCD):
            nextQuantity, _ = self.__ammo[nextShellCD]
            if nextQuantity <= 0:
                nextShellCD = None
        elif nextShellCD is not None:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as next.', nextShellCD)
        if currentShellCD is not None:
            self.changeSetting(currentShellCD)
            self.changeSetting(currentShellCD)
        else:
            self.__currShellCD = None
            self.onCurrentShellReset()
        if nextShellCD is not None:
            self.changeSetting(nextShellCD)
        else:
            self.__nextShellCD = None
        self.processDelayer('setCurrentShellCD')
        return

    @MethodsRules.delayable()
    def setGunSettings(self, gun):
        self.__gunSettings = _GunSettings.make(gun)
        self.onGunSettingsSet(self.__gunSettings)

    def getNextShellCD(self):
        return self.__nextShellCD

    @MethodsRules.delayable('setShells')
    def setNextShellCD(self, intCD):
        result = False
        if intCD in self.__ammo:
            quantity, _ = self.__ammo[intCD]
            if self.__nextShellCD != intCD and quantity > 0:
                self.__nextShellCD = intCD
                self.__onNextShellChanged(intCD)
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as next.', intCD)
        return result

    def getCurrentShellCD(self):
        return self.__currShellCD

    @MethodsRules.delayable('setShells')
    def setCurrentShellCD(self, intCD, usePrediction=True):
        result = False
        if intCD in self.__ammo:
            if self.__currShellCD != intCD:
                self.__currShellCD = intCD
                self._reloadingState.startPredictedReloading(usePrediction, self.__gunSettings)
                self.__onCurrentShellChanged(intCD)
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as current.', intCD)
        return result

    @MethodsRules.delayable('setCurrentShellCD')
    def setGunReloadTime(self, timeLeft, baseTime, skipAutoLoader=False, shotsAmount=-1, clipTime=None):
        if not self.__gunSettings.hasAutoReload():
            self.__shellChangeTime = baseTime * self.__gunSettings.getShellChangeFactor()
        if self.__gunSettings.isTwinGun() and self.__currShellCD == self.__nextShellCD:
            isLastCurrShells = self.getShellsQuantityLeft() <= self.__gunSettings.getLastAmmoCount(shotsAmount)
            _, quantityNextLeft = self.__getPredictedLoadShells(self.__isBattlePeriod(), isLastCurrShells, shotsAmount)
            nextShellIsOne = quantityNextLeft == 1
            if shotsAmount == 1 and not isLastCurrShells or isLastCurrShells and nextShellIsOne:
                self.__shellChangeTime *= self.__gunSettings.twinGunFactor
        self.triggerReloadEffect(timeLeft, baseTime, shotsAmount=shotsAmount)
        interval = clipTime or self.__gunSettings.getClipInterval()
        if interval > 0 and self.__currShellCD in self.__ammo and baseTime > 0.0:
            shellsInClip = self.__ammo[self.__currShellCD][1]
            if self.__gunSettings.isBurstAndClip():
                quantityClip = ceil(shellsInClip / float(self.__gunSettings.burst.size))
                if not (quantityClip == 1 and timeLeft == 0 and not self.__gunSettings.hasAutoReload() or quantityClip <= 1 and timeLeft != 0):
                    if interval <= baseTime:
                        baseTime = interval
            elif not (shellsInClip == 1 and timeLeft == 0 and not self.__gunSettings.hasAutoReload() or shellsInClip == 0 and timeLeft != 0):
                if interval <= baseTime:
                    baseTime = interval
        elif baseTime == 0.0:
            baseTime = timeLeft
        isIgnored = False
        if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
            isIgnored = self.__autoShoots.process(timeLeft, self._reloadingState.getActualValue())
        else:
            self.__autoShoots.reset()
        self._reloadingState.setTimes(timeLeft, baseTime)
        if not isIgnored:
            self.onGunReloadTimeSet(self.__currShellCD, self._reloadingState.getSnapshot(), skipAutoLoader)
        self.updateShellChangeTime()

    def preprocessGunReloadTime(self, timeLeft, baseTime, shotsAmount):
        isBattlePeriod = self.__isBattlePeriod()
        currShellsCount = self.getShellsQuantityLeft()
        lastAmmoCount = self.__gunSettings.getLastAmmoCount(shotsAmount)
        if timeLeft <= 0.0:
            isLastCurrShells = currShellsCount <= lastAmmoCount
            if isLastCurrShells and currShellsCount == sum((item[2] for item in self.getOrderedShellsLayout())):
                baseTime = -1 if isBattlePeriod else baseTime
            elif self.__gunSettings.isTwinGun():
                intCD, quantity = self.__getPredictedLoadShells(isBattlePeriod, isLastCurrShells, shotsAmount)
                maxAmount = shotsAmount if intCD == self.__currShellCD and isBattlePeriod else _DUPLET_SHELLS_AMOUNT
                baseTime *= self.__gunSettings.getTwinGunFactor(shotsAmount, math_utils.clamp(1, maxAmount, quantity))
        if timeLeft < 0.0:
            timeLeft = -1
        return (timeLeft, baseTime, shotsAmount)

    def setGunAutoReloadTime(self, timeLeft, baseTime, firstClipBaseTime, isSlowed, isBoostApplicable, clipTime=None):
        self._autoReloadingState.setTimes(timeLeft, baseTime)
        if self.__gunSettings.hasAutoReload():
            self.__shellChangeTime = firstClipBaseTime * self.__gunSettings.getShellChangeFactor()
        self.__notifyAboutAutoReloadTimeChanges(isSlowed)
        self._autoReloadingBoostState.setReloadingTimeSnapshot(self._autoReloadingState.getSnapshot(), isBoostApplicable, self.__gunSettings, clipTime=clipTime)
        if self.__gunSettings.reloadEffect is not None and self.__currShellCD in self.__ammo:
            shellCounts = self.__ammo[self.__currShellCD]
            shellsInClip = shellCounts[1]
            clipCapacity = self.__gunSettings.clip.size
            canBeFull = shellCounts[0] >= clipCapacity
            lastShell = shellsInClip == clipCapacity - 1
            reloadStart = fabs(timeLeft - baseTime) < 0.001
            if timeLeft > 0.0:
                if reloadStart:
                    self.__gunSettings.reloadEffect.onClipLoad(timeLeft, shellsInClip, lastShell, canBeFull)
                else:
                    self.__gunSettings.reloadEffect.updateReloadTime(timeLeft, shellsInClip, lastShell, canBeFull)
            elif self.__gunSettings.clip.size == shellsInClip and not reloadStart:
                self.__gunSettings.reloadEffect.onFull()
        self.updateShellChangeTime()
        return

    def triggerReloadEffect(self, timeLeft, baseTime, directTrigger=False, shotsAmount=-1):
        if timeLeft > 0.0 and self.__gunSettings.reloadEffect is not None and self.__currShellCD in self.__ammo:
            clipCapacity = self.__gunSettings.clip.size
            self.__gunSettings.reloadEffect.start(timeLeft, baseTime, clipCapacity, directTrigger=directTrigger, shotsAmount=shotsAmount)
        elif timeLeft <= 0.0 and self.__gunSettings.reloadEffect is not None:
            self.__gunSettings.reloadEffect.reloadEnd()
        return

    def getGunReloadingState(self):
        return self._reloadingState.getSnapshot()

    def getAutoReloadingState(self):
        return self._autoReloadingState.getSnapshot()

    def isGunReloading(self):
        return not self._reloadingState.isReloadingFinished()

    def getShellChangeTime(self):
        return self.__shellChangeTime

    @MethodsRules.delayable('setGunReloadTime')
    def refreshGunReloading(self):
        self.onGunReloadTimeSet(self.__currShellCD, self._reloadingState.getSnapshot(), False)
        self.updateShellChangeTime()

    def getShells(self, intCD):
        try:
            quantity, quantityInClip = self.__ammo[intCD]
        except KeyError:
            LOG_ERROR('Shell is not found.', intCD)
            quantity, quantityInClip = (SHELL_QUANTITY_UNKNOWN,) * 2

        return (quantity, quantityInClip)

    def shellInAmmo(self, intCD):
        return intCD in self.__ammo

    def getOrderedShellsLayout(self):
        result = []
        for intCD in self._order:
            descriptor = self.__gunSettings.getShellDescriptor(intCD)
            quantity, quantityInClip = self.__ammo[intCD]
            isInfinite = self.__isInfiniteShell(intCD)
            result.append((intCD,
             descriptor,
             quantity,
             quantityInClip,
             self.__gunSettings,
             isInfinite))

        return result

    def getShellsOrderIter(self):
        return (intCD for intCD in self._order)

    def getShellsLayout(self):
        return self.__ammo.iteritems()

    def getCurrentShells(self):
        return self.getShells(self.__currShellCD) if self.__currShellCD is not None else (SHELL_QUANTITY_UNKNOWN,) * 2

    def getShellsQuantityLeft(self):
        quantity, quantityInClip = self.getCurrentShells()
        if self.__gunSettings.isCassetteClip():
            result = quantityInClip
            if result == 0 and self._reloadingState.isReloadingFinished():
                clipSize = self.__gunSettings.clip.size
                if clipSize <= quantity:
                    result = clipSize
                else:
                    result = quantity
            return result
        else:
            return quantity

    def getAllShellsQuantityLeft(self):
        quantity = self.getShellsQuantityLeft()
        return sum((quantity for quantity, _ in self.__ammo.itervalues())) if quantity == 0 else quantity

    def getClipPercentLeft(self):
        if not self.__gunSettings.isCassetteClip():
            return 0.0
        _, quantityInClip = self.getCurrentShells()
        return 0.0 if quantityInClip < 0 else float(quantityInClip) / self.__gunSettings.clip.size

    @MethodsRules.delayable('setGunSettings')
    def setShells(self, intCD, quantity, quantityInClip):
        result = SHELL_SET_RESULT.UNDEFINED
        if self.__gunSettings.getShotIndex(intCD) < 0:
            _logger.warning('Trying to set data for shell %d, which is not suitable for current gun', intCD)
            return result
        if intCD in self.__ammo:
            prevAmmo = self.__ammo[intCD]
            self.__ammo[intCD] = (quantity, quantityInClip)
            result |= SHELL_SET_RESULT.UPDATED
            if intCD == self.__currShellCD:
                result |= SHELL_SET_RESULT.CURRENT
                if quantityInClip > 0 and prevAmmo[1] == 0 and quantity == prevAmmo[0]:
                    result |= SHELL_SET_RESULT.CASSETTE_RELOAD
            self.onShellsUpdated(intCD, quantity, quantityInClip, result)
        else:
            self.__ammo[intCD] = (quantity, quantityInClip)
            self._order.append(intCD)
            result |= SHELL_SET_RESULT.ADDED
            descriptor = self.__gunSettings.getShellDescriptor(intCD)
            isInfinite = self.__isInfiniteShell(intCD)
            self.onShellsAdded(intCD, descriptor, quantity, quantityInClip, self.__gunSettings, isInfinite)
        self.updateShellChangeTime()
        return result

    def getNextSettingCode(self, intCD):
        if intCD == self.__currShellCD and intCD == self.__nextShellCD:
            return None
        elif intCD not in self.__ammo.keys():
            LOG_ERROR('Shell is not found.', intCD)
            return None
        else:
            quantity, _ = self.__ammo[intCD]
            if quantity <= 0:
                return None
            if intCD == self.__nextShellCD:
                code = VEHICLE_SETTING.CURRENT_SHELLS
            else:
                code = VEHICLE_SETTING.NEXT_SHELLS
            autoShootGunCtrl = self.__guiSessionProvider.shared.autoShootCtrl
            return None if code == VEHICLE_SETTING.CURRENT_SHELLS and autoShootGunCtrl.isBurstActive() else code

    def changeSetting(self, intCD, avatar=None):
        if not avatar_getter.isVehicleAlive(avatar):
            return False
        else:
            code = self.getNextSettingCode(intCD)
            if code is None:
                return False
            avatar_getter.predictVehicleSetting(code, intCD, avatar)
            avatar_getter.changeVehicleSetting(code, intCD, avatar)
            return True

    def reloadPartialClip(self, avatar=None):
        clipSize = self.__gunSettings.clip.size
        if clipSize > 1 and self.__currShellCD in self.__ammo and not self.__gunSettings.hasAutoReload():
            quantity, quantityInClip = self.__ammo[self.__currShellCD]
            if quantity != 0 and (quantityInClip < clipSize or self.__nextShellCD != self.__currShellCD):
                avatar_getter.changeVehicleSetting(VEHICLE_SETTING.RELOAD_PARTIAL_CLIP, 0, avatar)

    def canShoot(self, isRepeat=False):
        if self.__currShellCD is None:
            result, error = False, CANT_SHOOT_ERROR.WAITING
        elif self.__ammo[self.__currShellCD][0] == 0:
            result, error = False, CANT_SHOOT_ERROR.NO_AMMO
        elif self.isGunReloading():
            if not isRepeat and self.__gunSettings.hasAutoReload():
                self.__shotFail()
            result, error = False, CANT_SHOOT_ERROR.RELOADING
        elif self.__ammo[self.__currShellCD][1] == 0:
            if self.__gunSettings.hasAutoShoot():
                result, error = False, CANT_SHOOT_ERROR.EMPTY_AUTO_CLIP
            elif self.__gunSettings.isCassetteClip():
                result, error = True, CANT_SHOOT_ERROR.EMPTY_CLIP
            else:
                result, error = True, CANT_SHOOT_ERROR.UNDEFINED
        else:
            result, error = True, CANT_SHOOT_ERROR.UNDEFINED
        return (result, error)

    def clearAmmo(self):
        self.__ammo.clear()
        self.__infinity.clear()
        self._order = []
        self.__currShellCD = None
        self.__nextShellCD = None
        return

    def setDualGunShellChangeTime(self, left, right, activeIdx):
        self.__dualGunShellChangeTime = _DualGunShellChangeTime(left, right, activeIdx)

    def getDualGunShellChangeTime(self):
        return self.__dualGunShellChangeTime

    def setDualGunQuickChangeReady(self, ready):
        self.__dualGunQuickChangeReady = ready
        self.updateShellChangeTime()

    def setQuickChangerFactor(self, isActive, factor):
        self.__quickChangerActive = isActive
        self.__quickChangerFactor = factor
        self.updateShellChangeTime(forced=True)

    def getQuickShellChangeTime(self):
        minValue = 0.1
        quickShellChangeTime = self.__shellChangeTime * self.__quickChangerFactor
        shellChangeTime = self.__shellChangeTime
        if self.__gunSettings.isDualGun:
            activeIdx = self.__dualGunShellChangeTime.activeIdx
            if activeIdx == 0:
                activeGunTime = self.__dualGunShellChangeTime.left
            else:
                activeGunTime = self.__dualGunShellChangeTime.right
            shellChangeTime = activeGunTime
            quickShellChangeTime = activeGunTime * self.__quickChangerFactor
        vehicle = self.__guiSessionProvider.shared.vehicleState.getControllingVehicle()
        if vehicle is not None:
            restrict = ReloadRestriction.getBy(vehicle.typeDescriptor)
            if quickShellChangeTime < restrict:
                quickShellChangeTime = min(restrict, shellChangeTime)
        return max(quickShellChangeTime, minValue)

    def canQuickShellChange(self):
        canChange = self.__canChangeShell()
        readyToQuickChange = not self._reloadingState.isReloading()
        if self.__gunSettings.clip.size > 1:
            readyToQuickChange &= self.__gunSettings.clip.size == self.__ammo.get(self.__currShellCD, (0, 0))[1]
        if self.__gunSettings.isDualGun:
            readyToQuickChange &= self.__dualGunQuickChangeReady
        if self.__gunSettings.isTwinGun():
            readyToQuickChange &= self.getShellsQuantityLeft() > 1
        return self.__quickChangerActive and readyToQuickChange and canChange and self.__shellChangeTime > 0

    def updateVehicleQuickShellChanger(self, isActive):
        self.__quickChangerInProcess = isActive

    def getIntuitionReloadInProcess(self):
        return self.__quickChangerInProcess

    def handleAmmoChoice(self, key):
        if any([ component.isActive for component in self._viewComponents ]):
            for component in self._viewComponents:
                component.handleAmmoKey(key)

    def updateShellChangeTime(self, forced=False):
        isVisible, shellChangeTime = False, self.__shellChangeTime
        if self.__gunSettings.hasShellChangeFactor():
            isVisible = self.__canChangeShell() and not self._reloadingState.isReloading()
            shellChangeTime = self.getQuickShellChangeTime() if self.canQuickShellChange() else shellChangeTime
        elif self.__quickChangerActive:
            isVisible, shellChangeTime = self.canQuickShellChange(), self.getQuickShellChangeTime()
        isVisible = isVisible and self.__isBattlePeriod()
        if self.__quickChangerActive or self.__gunSettings.hasShellChangeFactor() or forced:
            self.onShellChangeTimeUpdated(isVisible, shellChangeTime)
        return (isVisible, shellChangeTime)

    def __isBattlePeriod(self):
        return self.__guiSessionProvider.shared.arenaPeriod.getPeriod() == ARENA_PERIOD.BATTLE

    def __isInfiniteShell(self, intCD):
        if intCD not in self.__infinity:
            arena = avatar_getter.getArena()
            isInfiniteBonusCap = arena.hasBonusCap(BONUS_CAPS.INFINITE_AMMO) if arena else False
            isInfinite = self.__gunSettings.getShellDescriptor(intCD).isInfinite or isInfiniteBonusCap and not self.__gunSettings.getShellDescriptor(intCD).isForceFinite
            self.__infinity[intCD] = isInfinite
        return self.__infinity[intCD]

    def __onCurrentShellChanged(self, intCD):
        self.onCurrentShellChanged(intCD)
        for component in self._viewComponents:
            component.setCurrentShellCD(intCD)

    def __onNextShellChanged(self, intCD):
        self.onNextShellChanged(intCD)
        for component in self._viewComponents:
            component.setNextShellCD(intCD)

    def __canChangeShell(self):
        return sum((1 for quantity, _ in self.__ammo.itervalues() if quantity > 0)) > 1

    def __shotFail(self):
        if self.__gunSettings.reloadEffect is not None and self.__currShellCD in self.__ammo:
            shellCounts = self.__ammo[self.__currShellCD]
            if shellCounts[1] == 0:
                self.__gunSettings.reloadEffect.shotFail()
        return

    def __notifyAboutAutoReloadTimeChanges(self, isSlowed):
        self.onGunAutoReloadTimeSet(self._autoReloadingState.getSnapshot(), isSlowed)

    def __getFirstAvailableShell(self, notAvailableCD=None):
        return first((cd for cd in self._order if cd != notAvailableCD and self.__ammo[cd][0] > 0))

    def __getPredictedLoadShells(self, isBattlePeriod, isLastCurrShells, shotsAmount):
        return self.__getPredictedNextShells(isLastCurrShells, shotsAmount) if isBattlePeriod else (self.__currShellCD, self.getShellsQuantityLeft())

    def __getPredictedNextShells(self, isLastCurrShells, shotsAmount):
        predictedShellCD = self.__nextShellCD
        if predictedShellCD is None or predictedShellCD == self.__currShellCD and isLastCurrShells:
            predictedShellCD = self.__getFirstAvailableShell(self.__currShellCD)
        quantity = self.getShells(predictedShellCD)[0]
        if predictedShellCD == self.__currShellCD:
            quantity -= shotsAmount
        return (predictedShellCD, quantity)


class AmmoReplayRecorder(AmmoController):
    __slots__ = ('__changeRecord', '__timeRecord')

    def __init__(self, replayCtrl):
        super(AmmoReplayRecorder, self).__init__()
        self.__changeRecord = replayCtrl.setAmmoSetting
        self.__timeRecord = replayCtrl.setGunReloadTime

    def clear(self, leave=True):
        super(AmmoReplayRecorder, self).clear(leave)
        if leave:
            self.__changeRecord = None
            self.__timeRecord = None
        return

    def setGunReloadTime(self, timeLeft, baseTime, skipAutoLoader=False, shotsAmount=-1, clipTime=None):
        if self.__timeRecord is not None:
            if timeLeft < 0:
                self.__timeRecord(0, -1)
            else:
                startTime = baseTime - timeLeft
                self.__timeRecord(startTime, baseTime)
        super(AmmoReplayRecorder, self).setGunReloadTime(timeLeft, baseTime, skipAutoLoader, shotsAmount, clipTime)
        return

    def changeSetting(self, intCD, avatar=None):
        changed = super(AmmoReplayRecorder, self).changeSetting(intCD, avatar)
        if changed and intCD in self._order:
            if self.__changeRecord is not None:
                self.__changeRecord(self._order.index(intCD))
        return changed


class AmmoReplayPlayer(AmmoController):
    __slots__ = ('__replayCtrl',)

    def __init__(self, replayCtrl):
        super(AmmoReplayPlayer, self).__init__()
        self.__replayCtrl = replayCtrl
        self.__replayCtrl.onAmmoSettingChanged += self.__onAmmoSettingChanged

    def clear(self, leave=True):
        if leave:
            if self.__replayCtrl is not None:
                self.__replayCtrl.onAmmoSettingChanged -= self.__onAmmoSettingChanged
                self.__replayCtrl = None
        super(AmmoReplayPlayer, self).clear(leave)
        return

    def changeSetting(self, intCD, avatar=None):
        return False

    @MethodsRules.delayable('setShells')
    def __onAmmoSettingChanged(self, idx):
        if idx >= len(self._order) or idx < 0:
            return
        else:
            intCD = self._order[idx]
            code = self.getNextSettingCode(intCD)
            if code is not None:
                avatar_getter.predictVehicleSetting(code, intCD)
            return
