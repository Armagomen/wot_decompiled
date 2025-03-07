# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_cache.py
import itertools
import math
import sys
from collections import namedtuple
from functools import partial
import typing
import nations
import persistent_data_cache_common as pdc
from constants import BonusTypes
from gui.shared.items_parameters import calcGunParams, calcShellParams, getEquipmentParameters, isAutoReloadGun, isAutoShootGun, isDualGun, isDualAccuracy, isTwinGun
from gui.shared.items_parameters import xml_reader
from gui.shared.utils.decorators import debugTime
from items import vehicles, ITEM_TYPES, EQUIPMENT_TYPES
from items.vehicles import getVehicleType
from gui.shared.utils import GUN_NORMAL, GUN_CAN_BE_CLIP, GUN_CLIP, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD, GUN_DUAL_GUN, GUN_CAN_BE_DUAL_GUN, GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT, GUN_TWIN_GUN, GUN_CAN_BE_TWIN_GUN
from post_progression_common import ACTION_TYPES
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
PrecachedShell = namedtuple('PrecachedShell', 'guns params')
PrecachedEquipment = namedtuple('PrecachedEquipment', 'nations params')
PrecachedOptionalDevice = namedtuple('PrecachedOptionalDevice', 'weight nations')
PrecachedChassis = namedtuple('PrecachedChassis', 'isHydraulic, isWheeled, hasAutoSiege, isTrackWithinTrack, isWheeledOnSpotRotation')
PrecachedEngine = namedtuple('PrecachedEngine', 'hasTurboshaftEngine, hasRocketAcceleration')

class _PrecachedEngineTypes(object):
    DEFAULT = PrecachedEngine(hasTurboshaftEngine=False, hasRocketAcceleration=False)
    TURBOSHAFT = PrecachedEngine(hasTurboshaftEngine=True, hasRocketAcceleration=False)
    ROCKET_ACCELERATION = PrecachedEngine(hasTurboshaftEngine=False, hasRocketAcceleration=True)


class _PrecachedChassisTypes(object):
    DEFAULT = PrecachedChassis(isHydraulic=False, isWheeled=False, hasAutoSiege=False, isTrackWithinTrack=False, isWheeledOnSpotRotation=False)
    HYDRAULIC = PrecachedChassis(isHydraulic=True, isWheeled=False, hasAutoSiege=False, isTrackWithinTrack=False, isWheeledOnSpotRotation=False)
    WHEELED = PrecachedChassis(isHydraulic=False, isWheeled=True, hasAutoSiege=False, isTrackWithinTrack=False, isWheeledOnSpotRotation=False)
    HYDRAULIC_WHEELED = PrecachedChassis(isHydraulic=True, isWheeled=True, hasAutoSiege=False, isTrackWithinTrack=False, isWheeledOnSpotRotation=False)
    ON_SPOT_ROTATION_WHEELED = PrecachedChassis(isHydraulic=False, isWheeled=True, hasAutoSiege=False, isTrackWithinTrack=False, isWheeledOnSpotRotation=True)
    HYDRAULIC_AUTO_SIEGE = PrecachedChassis(isHydraulic=True, isWheeled=False, hasAutoSiege=True, isTrackWithinTrack=False, isWheeledOnSpotRotation=False)
    TRACK_WITHIN_TRACK = PrecachedChassis(isHydraulic=False, isWheeled=False, hasAutoSiege=False, isTrackWithinTrack=True, isWheeledOnSpotRotation=False)
    ALL = (DEFAULT,
     HYDRAULIC,
     WHEELED,
     HYDRAULIC_WHEELED,
     HYDRAULIC_AUTO_SIEGE,
     TRACK_WITHIN_TRACK,
     ON_SPOT_ROTATION_WHEELED)
    MAP = dict((((pC.isHydraulic,
      pC.isWheeled,
      pC.hasAutoSiege,
      pC.isTrackWithinTrack,
      pC.isWheeledOnSpotRotation), pC) for pC in ALL))


def isHydraulicChassis(vDescr):
    return vDescr.hasHydraulicChassis or vDescr.isWheeledVehicle or vDescr.hasAutoSiegeMode if vDescr.hasSiegeMode else False


def isTrackWithinTrackChassis(vChassis):
    return vChassis.isTrackWithinTrack


class PrecachedGun(namedtuple('PrecachedGun', ('clipVehicles', 'autoReloadVehicles', 'autoShootVehicles', 'dualGunVehicles', 'twinGunVehicles', 'dualAccuracyVehicles', 'params', 'turretsByVehicles'))):

    @property
    def clipVehiclesNames(self):
        if self.clipVehicles is not None:
            return [ getVehicleType(cd).userString for cd in self.clipVehicles ]
        else:
            return []

    def hasDualAccuracy(self, vehicleCD):
        return self.dualAccuracyVehicles is not None and vehicleCD in self.dualAccuracyVehicles

    def getReloadingType(self, vehicleCD=None):
        reloadingType = GUN_NORMAL
        if vehicleCD is None:
            if self.autoReloadVehicles:
                reloadingType = GUN_CAN_BE_AUTO_RELOAD
            elif self.autoShootVehicles:
                reloadingType = GUN_CAN_BE_AUTO_SHOOT
            elif self.clipVehicles:
                reloadingType = GUN_CAN_BE_CLIP
            elif self.dualGunVehicles:
                reloadingType = GUN_CAN_BE_DUAL_GUN
            elif self.twinGunVehicles:
                reloadingType = GUN_CAN_BE_TWIN_GUN
        elif self.autoReloadVehicles and vehicleCD in self.autoReloadVehicles:
            reloadingType = GUN_AUTO_RELOAD
        elif self.autoShootVehicles and vehicleCD in self.autoShootVehicles:
            reloadingType = GUN_AUTO_SHOOT
        elif self.clipVehicles is not None and vehicleCD in self.clipVehicles:
            reloadingType = GUN_CLIP
        elif self.dualGunVehicles and vehicleCD in self.dualGunVehicles:
            reloadingType = GUN_DUAL_GUN
        elif self.twinGunVehicles and vehicleCD in self.twinGunVehicles:
            reloadingType = GUN_TWIN_GUN
        return reloadingType

    def getTurretsForVehicle(self, vehicleCD):
        return self.turretsByVehicles.get(vehicleCD, ())


def _getVehicleSuitablesByType(vehicleType, itemTypeId, turretPID=0):
    result = []
    if itemTypeId == ITEM_TYPES.vehicleChassis:
        result = vehicleType.chassis
    elif itemTypeId == ITEM_TYPES.vehicleEngine:
        result = vehicleType.engines
    elif itemTypeId == ITEM_TYPES.vehicleRadio:
        result = vehicleType.radios
    elif itemTypeId == ITEM_TYPES.vehicleFuelTank:
        result = vehicleType.fuelTanks
    elif itemTypeId == ITEM_TYPES.vehicleTurret:
        result = vehicleType.turrets[turretPID]
    elif itemTypeId == ITEM_TYPES.vehicleGun:
        for turret in vehicleType.turrets[turretPID]:
            for gun in turret.guns:
                result.append(gun)

    elif itemTypeId == ITEM_TYPES.shell:
        for turret in vehicleType.turrets[turretPID]:
            for gun in turret.guns:
                for shot in gun.shots:
                    result.append(shot.shell)

    else:
        raise SoftException('Type ID {} is not supported'.format(itemTypeId))
    return result


class VehicleDescrsCache(object):
    __slots__ = ('_local',)

    def __init__(self):
        super(VehicleDescrsCache, self).__init__()
        self._local = {}

    def clear(self):
        self._local.clear()

    def load(self):
        vehilesList = vehicles.g_list.getList
        for nationID in nations.INDICES.itervalues():
            self._local[nationID] = [ vehicles.VehicleDescr(typeID=(nationID, cd)) for cd in vehilesList(nationID).iterkeys() ]

    def generator(self, nationID=None):
        if nationID is None:
            nationIDs = nations.INDICES.values()
        else:
            nationIDs = (nationID,)
        for nextID in nationIDs:
            if nextID not in self._local:
                continue
            for descr in self._local[nextID]:
                yield descr

        return


ParamsCacheData = namedtuple('ParamsCacheData', 'cache, wheeledChassisParams, noCamouflageVehicles, vehiclesCache')

def _readCache(vehiclesCache):
    if vehiclesCache is None:
        vehiclesCache = VehicleDescrsCache()
    data = ParamsCacheData({}, {}, [], vehiclesCache)
    vehiclesCache.load()
    _precacheOptionalDevices(data)
    _precacheGuns(data)
    _precacheShells(data)
    _precacheEquipments(data)
    _precacheChassis(data)
    _getVehiclesWithoutCamouflage(data)
    _precacheEngines(data)
    vehiclesCache.clear()
    del vehiclesCache
    coefficients, bonuses = xml_reader.read()
    return (coefficients,
     bonuses,
     data.cache,
     data.wheeledChassisParams,
     tuple(data.noCamouflageVehicles))


def _precacheEquipments(data):
    data.cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.equipment] = {}
    for eqpDescr in vehicles.g_cache.equipments().itervalues():
        equipmentNations = set()
        for vDescr in data.vehiclesCache.generator():
            if not eqpDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                continue
            nation, _ = vDescr.type.id
            equipmentNations.add(nation)

        data.cache[nations.NONE_INDEX][ITEM_TYPES.equipment][eqpDescr.compactDescr] = PrecachedEquipment(nations=equipmentNations, params=getEquipmentParameters(eqpDescr))


def _precacheOptionalDevices(data):
    data.cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.optionalDevice] = {}
    for deviceDescr in vehicles.g_cache.optionalDevices().itervalues():
        wmin, wmax = sys.maxint, -1
        deviceNations = set()
        for vDescr in data.vehiclesCache.generator():
            if not deviceDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                continue
            nation, _ = vDescr.type.id
            deviceNations.add(nation)
            mods = deviceDescr.weightOnVehicle(vDescr)
            weightOnVehicle = math.ceil(vDescr.physics['weight'] * mods[0] + mods[1])
            wmin, wmax = min(wmin, weightOnVehicle), max(wmax, weightOnVehicle)

        data.cache[nations.NONE_INDEX][ITEM_TYPES.optionalDevice][deviceDescr.compactDescr] = PrecachedOptionalDevice(weight=(wmin, wmax), nations=deviceNations)


def _precacheGuns(data):
    descriptors = []
    curVehicleTurretsCDs = []
    getter = vehicles.g_cache.guns
    for nationIdx in nations.INDICES.itervalues():
        data.cache.setdefault(nationIdx, {})[ITEM_TYPES.vehicleGun] = {}
        for g in getter(nationIdx).itervalues():
            del descriptors[:]
            turretsIntCDs = {}
            clipVehiclesList = set()
            autoReloadVehsList = set()
            autoShootVehsList = set()
            dualGunVehsList = set()
            dualAccuracyVehsList = set()
            twinGunVehsList = set()
            for vDescr in data.vehiclesCache.generator(nationIdx):
                del curVehicleTurretsCDs[:]
                vehCD = vDescr.type.compactDescr
                for vTurrets in vDescr.type.turrets:
                    for turret in vTurrets:
                        for gun in turret.guns:
                            if gun.id[1] == g.id[1]:
                                descriptors.append(gun)
                                if len(vDescr.hull.fakeTurrets['lobby']) != len(vDescr.turrets):
                                    curVehicleTurretsCDs.append(turret.compactDescr)
                                if gun.clip[0] > 1:
                                    clipVehiclesList.add(vehCD)
                                if isAutoReloadGun(gun):
                                    autoReloadVehsList.add(vehCD)
                                if isAutoShootGun(gun):
                                    autoShootVehsList.add(vehCD)
                                if isDualGun(gun):
                                    dualGunVehsList.add(vehCD)
                                if isDualAccuracy(gun):
                                    dualAccuracyVehsList.add(vehCD)
                                if isTwinGun(gun):
                                    twinGunVehsList.add(vehCD)

                if curVehicleTurretsCDs:
                    turretsIntCDs[vDescr.type.compactDescr] = tuple(curVehicleTurretsCDs)

            data.cache[nationIdx][ITEM_TYPES.vehicleGun][g.compactDescr] = PrecachedGun(clipVehicles=clipVehiclesList if clipVehiclesList else None, autoReloadVehicles=frozenset(autoReloadVehsList) if autoReloadVehsList else None, autoShootVehicles=frozenset(autoShootVehsList) if autoShootVehsList else None, dualGunVehicles=frozenset(dualGunVehsList) if dualGunVehsList else None, dualAccuracyVehicles=frozenset(dualAccuracyVehsList) if dualAccuracyVehsList else None, twinGunVehicles=frozenset(twinGunVehsList) if twinGunVehsList else None, params=calcGunParams(g, descriptors), turretsByVehicles=turretsIntCDs)

    return


def _precacheShells(data):
    descriptors = []
    gunsCDs = []
    gunsGetter = vehicles.g_cache.guns
    shellsGetter = vehicles.g_cache.shells
    for nationIdx in nations.INDICES.values():
        data.cache.setdefault(nationIdx, {})[ITEM_TYPES.shell] = {}
        for sDescr in shellsGetter(nationIdx).itervalues():
            del descriptors[:]
            del gunsCDs[:]
            for gDescr in gunsGetter(nationIdx).itervalues():
                for shot in gDescr.shots:
                    if shot.shell.id[1] == sDescr.id[1]:
                        if gDescr.compactDescr not in gunsCDs:
                            gunsCDs.append(gDescr.compactDescr)
                            descriptors.append(shot)

            data.cache[nationIdx][ITEM_TYPES.shell][sDescr.compactDescr] = PrecachedShell(guns=tuple(gunsCDs), params=calcShellParams(descriptors))


def _precacheChassis(data):
    getter = vehicles.g_cache.chassis
    chassisItemType = ITEM_TYPES.vehicleChassis
    processedItems = set()
    for nationIdx in nations.INDICES.itervalues():
        data.cache.setdefault(nationIdx, {})[chassisItemType] = {}
        cachedChassisByNation = data.cache[nationIdx][chassisItemType]
        for vDescr in data.vehiclesCache.generator(nationIdx):
            for vChs in vDescr.type.chassis:
                chassisCD = vChs.compactDescr
                cachedChassisByNation[chassisCD] = _PrecachedChassisTypes.MAP[isHydraulicChassis(vDescr), vDescr.isWheeledVehicle, vDescr.hasAutoSiegeMode, isTrackWithinTrackChassis(vChs), vDescr.isWheeledOnSpotRotation]
                processedItems.add(chassisCD)
                if vDescr.isWheeledVehicle:
                    chassisPhysics = vDescr.type.xphysics['chassis'][vChs.name]
                    data.wheeledChassisParams[chassisCD] = chassisPhysics['axleSteeringLockAngles']

        for chs in getter(nationIdx).itervalues():
            if chs.compactDescr not in processedItems:
                cachedChassisByNation[chs.compactDescr] = _PrecachedChassisTypes.DEFAULT


def _precacheEngines(data):
    getter = vehicles.g_cache.engines
    engineItemType = ITEM_TYPES.vehicleEngine
    processedItems = set()
    for nationIdx in nations.INDICES.itervalues():
        data.cache.setdefault(nationIdx, {})[engineItemType] = {}
        cachedEngineByNation = data.cache[nationIdx][engineItemType]
        for vDescr in data.vehiclesCache.generator(nationIdx):
            for vEng in vDescr.type.engines:
                engineCD = vEng.compactDescr
                if vDescr.hasTurboshaftEngine:
                    cachedEngineByNation[engineCD] = _PrecachedEngineTypes.TURBOSHAFT
                elif vDescr.hasRocketAcceleration:
                    cachedEngineByNation[engineCD] = _PrecachedEngineTypes.ROCKET_ACCELERATION
                else:
                    cachedEngineByNation[engineCD] = _PrecachedEngineTypes.DEFAULT
                processedItems.add(engineCD)

        for eng in getter(nationIdx).itervalues():
            if eng.compactDescr not in processedItems:
                cachedEngineByNation[eng.compactDescr] = _PrecachedEngineTypes.DEFAULT


def _getVehiclesWithoutCamouflage(data):
    deniedVehicles = {}
    allowedVehicles = set()
    customization = vehicles.g_cache.customization
    for nationID in nations.INDICES.itervalues():
        deniedVehicles.clear()
        allowedVehicles.clear()
        restrictedCamouflages = 0
        camouflages = customization(nationID)['camouflages']
        totalCount = len(camouflages)
        for camouflage in camouflages.itervalues():
            currentAllowed = camouflage.get('allow', ())
            for vehCD in camouflage.get('deny', ()):
                deniedVehicles[vehCD] = deniedVehicles.get(vehCD, 0) + 1

            allowedVehicles.update(currentAllowed)
            if currentAllowed:
                restrictedCamouflages += 1

        for vehCD, count in deniedVehicles.iteritems():
            if vehCD not in allowedVehicles and count + restrictedCamouflages >= totalCount:
                data.noCamouflageVehicles.append(vehCD)


class _ParamsCache(object):
    __slots__ = ('__cache', '__simplifiedParamsCoefficients', '__bonuses', '__noCamouflageVehicles', '__wheeledChassisParams')

    def __init__(self):
        super(_ParamsCache, self).__init__()
        self.__cache = {}
        self.__simplifiedParamsCoefficients = {}
        self.__bonuses = {}
        self.__noCamouflageVehicles = ()
        self.__wheeledChassisParams = {}

    @debugTime
    def init(self, vehiclesCache=None):
        self.__simplifiedParamsCoefficients, self.__bonuses, self.__cache, self.__wheeledChassisParams, self.__noCamouflageVehicles = pdc.load('gui_items_params_cache', partial(_readCache, vehiclesCache))

    def getGunReloadingSystemType(self, itemCD, vehicleCD=None):
        return self.getPrecachedParameters(itemCD).getReloadingType(vehicleCD)

    def isChassisHydraulic(self, itemCD):
        return self.getPrecachedParameters(itemCD).isHydraulic

    def isChassisWheeled(self, itemCD):
        return self.getPrecachedParameters(itemCD).isWheeled

    def isChassisWheeledOnSpotRotation(self, itemCD):
        return self.getPrecachedParameters(itemCD).isWheeledOnSpotRotation

    def isTrackWithinTrack(self, itemCD):
        return self.getPrecachedParameters(itemCD).isTrackWithinTrack

    def isChassisAutoSiege(self, itemCD):
        return self.getPrecachedParameters(itemCD).hasAutoSiege

    def getWheeledChassisAxleLockAngles(self, itemCD):
        return self.__wheeledChassisParams.get(itemCD)

    def hasDualAccuracy(self, itemCD, vehicleCD=None):
        return self.getPrecachedParameters(itemCD).hasDualAccuracy(vehicleCD)

    def hasTurboshaftEngine(self, itemCD):
        return self.getPrecachedParameters(itemCD).hasTurboshaftEngine

    def hasRocketAcceleration(self, itemCD):
        return self.getPrecachedParameters(itemCD).hasRocketAcceleration

    def getSimplifiedCoefficients(self):
        return self.__simplifiedParamsCoefficients

    def getBonuses(self):
        return self.__bonuses

    def getPrecachedParameters(self, typeCompactDescr, default=None):
        itemTypeID, nationID, _ = vehicles.parseIntCompactDescr(typeCompactDescr)
        return self.__cache.get(nationID, {}).get(itemTypeID, {}).get(typeCompactDescr, default)

    def getComponentVehiclesNames(self, typeCompactDescr):
        itemTypeIdx, nationIdx, _ = vehicles.parseIntCompactDescr(typeCompactDescr)
        getter = vehicles.g_cache.vehicle
        result = []
        for itemID in vehicles.g_list.getList(nationIdx).iterkeys():
            vehicleType = getter(nationIdx, itemID)
            components = _getVehicleSuitablesByType(vehicleType, itemTypeIdx)
            filtered = [ item for item in components if item.compactDescr == typeCompactDescr ]
            if filtered:
                result.append(vehicleType.userString)

        return result

    def getCompatibleArtefacts(self, vehicle):
        compatibles = []
        receivedBaseMod = {}
        lockedBaseMod = {}
        for step in vehicle.postProgression.iterOrderedSteps():
            action = step.action
            if action.actionType == ACTION_TYPES.MODIFICATION and not step.isRestricted():
                if step.isReceived():
                    receivedBaseMod[action.getLocName()] = action.getTechName()
                elif action.getLocName() not in lockedBaseMod and action.getLocName() not in receivedBaseMod:
                    lockedBaseMod[action.getLocName()] = action.getTechName()
            if action.actionType == ACTION_TYPES.PAIR_MODIFICATION and not step.isRestricted():
                for subAction in action.modifications:
                    compatibles.append((subAction.getTechName(), BonusTypes.PAIR_MODIFICATION))

        for baseMod in itertools.chain(receivedBaseMod.itervalues(), lockedBaseMod.itervalues()):
            compatibles.append((baseMod, BonusTypes.BASE_MODIFICATION))

        for item in itertools.chain(vehicles.g_cache.equipments().itervalues(), vehicles.g_cache.optionalDevices().itervalues()):
            if item.checkCompatibilityWithVehicle(vehicle.descriptor)[0]:
                itemTypeName = item.itemTypeName
                if itemTypeName == 'equipment':
                    if item.equipmentType == EQUIPMENT_TYPES.battleBoosters:
                        itemTypeName = 'battleBooster'
                compatibles.append((item.name, itemTypeName))

        return compatibles

    def getVehiclesWithoutCamouflage(self):
        return self.__noCamouflageVehicles


g_paramsCache = _ParamsCache()
