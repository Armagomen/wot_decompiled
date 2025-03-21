# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/__init__.py
import math
import sys
from math import ceil
from constants import DAMAGE_INTERPOLATION_DIST_LAST
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import SHELLS_COUNT_PROP_NAME, RELOAD_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, DISPERSION_RADIUS_PROP_NAME, AIMING_TIME_PROP_NAME, PIERCING_POWER_PROP_NAME, DAMAGE_PROP_NAME, SHELLS_PROP_NAME, STUN_DURATION_PROP_NAME, GUARANTEED_STUN_DURATION_PROP_NAME, AUTO_RELOAD_PROP_NAME, DUAL_GUN_CHARGE_TIME, DUAL_GUN_RATE_TIME, RELOAD_TIME_SECS_PROP_NAME, DUAL_ACCURACY_COOLING_DELAY, BURST_FIRE_RATE, MAX_MUTABLE_DAMAGE_PROP_NAME, MIN_MUTABLE_DAMAGE_PROP_NAME
from helpers import time_utils
from helpers_common import computeDamageAtDist
from items import vehicles, artefacts
from items.components import component_constants
RELATIVE_PARAMS = ('relativePower', 'relativeArmor', 'relativeMobility', 'relativeCamouflage', 'relativeVisibility')
MAX_RELATIVE_VALUE = 1000
NO_DATA = 'no data'
_AUTO_RELOAD_TAG = 'autoreload'
_AUTO_SHOOT_TAG = 'autoShoot'
_DUAL_GUN_TAG = 'dualGun'
_DUAL_ACCURACY_TAG = 'dualAccuracy'
_TWIN_GUN_TAG = 'twinGun'

def _updateMinMaxValues(targetDict, key, value):
    targetDict[key] = (min(targetDict[key][0], value), max(targetDict[key][1], value))


def _addAutoReload(result, configReloadTimes, shellsCount):
    if len(configReloadTimes) < shellsCount:
        extraCount = shellsCount - len(configReloadTimes)
        fullReloadTimes = configReloadTimes + configReloadTimes[-1:] * extraCount
    else:
        fullReloadTimes = configReloadTimes[:]
    autoReloadTimes = result[AUTO_RELOAD_PROP_NAME]
    currCount = len(autoReloadTimes)
    for idx, reloadTime in enumerate(fullReloadTimes):
        if idx < currCount:
            currReloadTime = autoReloadTimes[idx]
            currReloadTime[0] = min(reloadTime, currReloadTime[0])
            currReloadTime[1] = min(reloadTime, currReloadTime[1])
        autoReloadTimes.append([reloadTime, reloadTime])


def isAutoReloadGun(gun):
    return _AUTO_RELOAD_TAG in gun.tags if gun is not None else False


def isAutoShootGun(gun):
    return _AUTO_SHOOT_TAG in gun.tags if gun is not None else False


def isDualGun(gun):
    return _DUAL_GUN_TAG in gun.tags if gun is not None else False


def isDualAccuracy(gun):
    return _DUAL_ACCURACY_TAG in gun.tags if gun is not None else False


def isBurstGun(gunDescr):
    return gunDescr.burst != component_constants.DEFAULT_GUN_BURST if gunDescr is not None else False


def isTwinGun(gun):
    return _TWIN_GUN_TAG in gun.tags if gun is not None else False


def getShotsPerMinute(descriptor, reloadTime, autoReloadGun=False):
    clip = descriptor.clip
    burst = descriptor.burst
    if autoReloadGun:
        clipCount = 1
        reloadTime = max(reloadTime, clip[1])
    else:
        clipCount = float(clip[0]) / (burst[0] if clip[0] > 1 else 1)
    value = burst[0] * clipCount * time_utils.ONE_MINUTE / (reloadTime + (burst[0] - 1) * burst[1] * clipCount + (clipCount - 1) * clip[1])
    return value


def calcGunParams(gunDescr, descriptors):
    result = {SHELLS_COUNT_PROP_NAME: (sys.maxint, -1),
     RELOAD_TIME_PROP_NAME: (sys.maxint, -1),
     RELOAD_MAGAZINE_TIME_PROP_NAME: (sys.maxint, -1),
     RELOAD_TIME_SECS_PROP_NAME: [],
     SHELL_RELOADING_TIME_PROP_NAME: (sys.maxint, -1),
     BURST_FIRE_RATE: [],
     DISPERSION_RADIUS_PROP_NAME: (sys.maxint, -1),
     AIMING_TIME_PROP_NAME: (sys.maxint, -1),
     PIERCING_POWER_PROP_NAME: [],
     DAMAGE_PROP_NAME: [],
     MAX_MUTABLE_DAMAGE_PROP_NAME: [],
     MIN_MUTABLE_DAMAGE_PROP_NAME: [],
     SHELLS_PROP_NAME: [],
     STUN_DURATION_PROP_NAME: [],
     GUARANTEED_STUN_DURATION_PROP_NAME: [],
     AUTO_RELOAD_PROP_NAME: [],
     DUAL_GUN_RATE_TIME: (sys.maxint, -1),
     DUAL_GUN_CHARGE_TIME: [],
     DUAL_ACCURACY_COOLING_DELAY: (sys.maxint, -1)}
    for descr in descriptors:
        currShellsCount = descr.clip[0]
        if currShellsCount > 1:
            _updateMinMaxValues(result, SHELL_RELOADING_TIME_PROP_NAME, descr.clip[1])
            _updateMinMaxValues(result, RELOAD_MAGAZINE_TIME_PROP_NAME, descr.reloadTime)
            _updateMinMaxValues(result, SHELLS_COUNT_PROP_NAME, currShellsCount)
        autoReload = isAutoReloadGun(descr)
        if autoReload:
            autoReloadTimes = descr.autoreload.reloadTime
            _addAutoReload(result, autoReloadTimes, currShellsCount)
            reloadTime = min(autoReloadTimes)
        else:
            reloadTime = descr.reloadTime
        _updateMinMaxValues(result, RELOAD_TIME_PROP_NAME, getShotsPerMinute(descr, reloadTime, autoReload))
        curDispRadius = round(descr.shotDispersionAngle * 100, 2)
        curAimingTime = round(descr.aimingTime, 1)
        _updateMinMaxValues(result, DISPERSION_RADIUS_PROP_NAME, curDispRadius)
        _updateMinMaxValues(result, AIMING_TIME_PROP_NAME, curAimingTime)
        chargeTime = ()
        rateTime = -1
        reloadTimeSecs = (reloadTime,)
        if isDualGun(descr):
            chargeTime = (descr.dualGun.chargeTime, descr.dualGun.reloadLockTime)
            rateTime = descr.dualGun.rateTime
            reloadTimeSecs = descr.dualGun.reloadTimes
        elif isTwinGun(descr):
            reloadTimeSecs = ()
        _updateMinMaxValues(result, DUAL_GUN_RATE_TIME, rateTime)
        result[DUAL_GUN_CHARGE_TIME] = chargeTime
        result[RELOAD_TIME_SECS_PROP_NAME] = reloadTimeSecs
        if isBurstGun(descr):
            burstSize, burstInterval = descr.burst
            result[BURST_FIRE_RATE].extend([burstInterval, burstSize])

    for shot in gunDescr.shots:
        shell = shot.shell
        result[PIERCING_POWER_PROP_NAME].append(shot.piercingPower[0])
        result[DAMAGE_PROP_NAME].append(shell.armorDamage[0])
        shellKind = backport.text(R.strings.item_types.shell.kinds.dyn(shell.kind)())
        result[MAX_MUTABLE_DAMAGE_PROP_NAME].append(shell.armorDamage[0])
        result[MIN_MUTABLE_DAMAGE_PROP_NAME].append(computeDamageAtDist(shell.armorDamage, min(shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST)) if shell.isDamageMutable else shell.armorDamage[0])
        result[SHELLS_PROP_NAME].append(shellKind)
        if shell.hasStun:
            stun = shell.stun
            stunDuration = stun.stunDuration
            result[STUN_DURATION_PROP_NAME].append(stun.stunDuration)
            result[GUARANTEED_STUN_DURATION_PROP_NAME].append(stun.guaranteedStunDuration * stunDuration)

    for key in (PIERCING_POWER_PROP_NAME,
     DAMAGE_PROP_NAME,
     MAX_MUTABLE_DAMAGE_PROP_NAME,
     MIN_MUTABLE_DAMAGE_PROP_NAME,
     SHELLS_PROP_NAME,
     STUN_DURATION_PROP_NAME,
     GUARANTEED_STUN_DURATION_PROP_NAME,
     BURST_FIRE_RATE):
        result[key] = tuple(result[key])

    if AUTO_RELOAD_PROP_NAME in result:
        result[AUTO_RELOAD_PROP_NAME] = tuple((tuple(minMaxPair) for minMaxPair in result[AUTO_RELOAD_PROP_NAME]))
    return result


def calcShellParams(descriptors):
    result = {PIERCING_POWER_PROP_NAME: (sys.maxint, -1),
     DAMAGE_PROP_NAME: (sys.maxint, -1)}
    for d in descriptors:
        piercingPower = d.piercingPower[0]
        shell = d.shell
        ppRand = shell.piercingPowerRandomization
        damageRand = shell.damageRandomization
        curPiercingPower = (int(piercingPower - piercingPower * ppRand), int(ceil(piercingPower + piercingPower * ppRand)))
        damage = shell.armorDamage[0]
        curDamage = (int(damage - damage * damageRand), int(ceil(damage + damage * damageRand)))
        result[PIERCING_POWER_PROP_NAME] = (min(result[PIERCING_POWER_PROP_NAME][0], curPiercingPower[0]), max(result[PIERCING_POWER_PROP_NAME][1], curPiercingPower[1]))
        result[DAMAGE_PROP_NAME] = (min(result[DAMAGE_PROP_NAME][0], curDamage[0]), max(result[DAMAGE_PROP_NAME][1], curDamage[1]))

    return result


def getEquipmentParameters(eqpDescr):
    params = dict()
    eqDescrType = type(eqpDescr)
    if eqDescrType is artefacts.RageArtillery:
        shellDescr = vehicles.getItemByCompactDescr(eqpDescr.shellCompactDescr)
        params.update({'damage': (shellDescr.armorDamage[0],) * 2,
         'piercingPower': eqpDescr.piercingPower,
         'caliber': shellDescr.caliber,
         'shotsNumberRange': eqpDescr.shotsNumber,
         'areaRadius': eqpDescr.areaRadius,
         'artDelayRange': eqpDescr.delay})
    elif eqDescrType is artefacts.RageBomber:
        shellDescr = vehicles.getItemByCompactDescr(eqpDescr.shellCompactDescr)
        params.update({'bombDamage': (shellDescr.armorDamage[0],) * 2,
         'piercingPower': eqpDescr.piercingPower,
         'bombsNumberRange': eqpDescr.bombsNumber,
         'areaSquare': eqpDescr.areaLength * eqpDescr.areaWidth,
         'flyDelayRange': eqpDescr.delay})
    elif eqDescrType is artefacts.AttackArtilleryFortEquipment:
        params.update({'maxDamage': eqpDescr.maxDamage,
         'commonDelay': eqpDescr.delay,
         'areaRadius': eqpDescr.areaRadius,
         'duration': eqpDescr.duration})
    elif eqDescrType in (artefacts.FortConsumableInspire, artefacts.ConsumableInspire):
        params.update({'crewRolesFactor': max(eqpDescr.increaseFactors['crewRolesFactor'] * 100 - 100, 0),
         'inactivationDelay': eqpDescr.inactivationDelay,
         'commonAreaRadius': eqpDescr.radius,
         'duration': eqpDescr.duration})
    return params


def getGunDescriptors(gunDescr, vehicleDescr):
    descriptors = []
    for gun in vehicleDescr.turret.guns:
        if gun.id[1] == gunDescr.id[1]:
            descriptors.append(gun)

    if not descriptors:
        for vTurrets in vehicleDescr.type.turrets:
            for turret in vTurrets:
                for gun in turret.guns:
                    if gun.id[1] == gunDescr.id[1]:
                        descriptors.append(gun)

    return descriptors


def getShellDescriptors(shellDescriptor, vehicleDescr):
    descriptors = []
    shellInNationID = shellDescriptor.id[1]
    for shot in vehicleDescr.gun.shots:
        if shot.shell.id[1] == shellInNationID:
            descriptors.append(shot)

    return descriptors


def getOptionalDeviceWeight(itemDescr, vehicleDescr):
    weight = 0
    index = None
    if vehicleDescr is not None:
        if itemDescr in vehicleDescr.optionalDevices:
            index = vehicleDescr.optionalDevices.index(itemDescr)
            vehicleDescr.removeOptionalDevice(index)
        mods = itemDescr.weightOnVehicle(vehicleDescr)
        weight = math.ceil(vehicleDescr.physics['weight'] * mods[0] + mods[1])
        if index is not None:
            vehicleDescr.installOptionalDevice(itemDescr.compactDescr, index)
    return (weight, weight)
