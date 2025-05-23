# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/gun_marker_ctrl.py
import logging
import math
import typing
from collections import namedtuple
import BattleReplay
import BigWorld
import GUI
import Math
import constants
import aih_constants
from Vehicle import Vehicle as VehicleEntity
from DestructibleEntity import DestructibleEntity
from AvatarInputHandler import AimingSystems
from AvatarInputHandler import aih_global_binding
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from math_utils import almostZero
from items.components.component_constants import MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS, MODERN_HE_DAMAGE_ABSORPTION_FACTOR
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus
from gui.shared.events import GunMarkerEvent
from gui.shared import EVENT_BUS_SCOPE
_MARKER_TYPE = aih_constants.GUN_MARKER_TYPE
_MARKER_FLAG = aih_constants.GUN_MARKER_FLAG
_SHOT_RESULT = aih_constants.SHOT_RESULT
_BINDING_ID = aih_global_binding.BINDING_ID
_IS_EXTENDED_GUN_MARKER_ENABLED = True
_BASE_PIERCING_PERCENT = 100.0
_ENABLED_MAX_PROJECTION_CHECK = True
_MAX_PROJECTION_ANGLE = math.radians(60.0)
_MAX_PROJECTION_ANGLE_COS = math.cos(_MAX_PROJECTION_ANGLE)
_logger = logging.getLogger(__name__)

def _computePiercingPowerAtDistImpl(dist, maxDist, val1, val2, arg1=constants.PIERCING_POWER_INTERPOLATION_DIST_FIRST, arg2=constants.PIERCING_POWER_INTERPOLATION_DIST_LAST):
    if dist <= arg1:
        return val1
    if arg1 == arg2:
        return val1
    if dist < maxDist:
        power = val1 + (val2 - val1) * (dist - arg1) / (arg2 - arg1)
        if power > 0.0:
            return power
        return 0.0


def _computePiercingPowerRandomizationImpl(piercingPowerRandomization, minimum, maximum):
    minPP = _BASE_PIERCING_PERCENT * (1.0 - piercingPowerRandomization * minimum)
    maxPP = _BASE_PIERCING_PERCENT * (1.0 + piercingPowerRandomization * maximum)
    return (minPP, maxPP)


def useServerGunMarker():
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying:
        return False
    settingsCore = dependency.instance(ISettingsCore)
    return settingsCore.getSetting('useServerAim')


def useClientGunMarker():
    return constants.HAS_DEV_RESOURCES or not useServerGunMarker()


def useDefaultGunMarkers():
    from gui import GUI_SETTINGS
    return not constants.HAS_DEV_RESOURCES or GUI_SETTINGS.useDefaultGunMarkers


def createGunMarker(isStrategic):
    factory = _GunMarkersDPFactory()
    if isStrategic:
        clientMarker = _SPGGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientSPGProvider())
        serverMarker = _SPGGunMarkerController(_MARKER_TYPE.SERVER, factory.getServerSPGProvider())
        dualAccMarker = _EmptyGunMarkerController(_MARKER_TYPE.UNDEFINED, None)
    else:
        clientMarker = _DefaultGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientProvider())
        serverMarker = _DefaultGunMarkerController(_MARKER_TYPE.SERVER, factory.getServerProvider())
        dualAccMarker = _DualAccMarkerController(_MARKER_TYPE.DUAL_ACC, factory.getDualAccuracyProvider())
    return _GunMarkersDecorator(clientMarker, serverMarker, dualAccMarker)


def createArtyHit(artyEquipmentUDO, areaRadius):
    factory = _GunMarkersDPFactory()
    return _ArtyHitMarkerController(_MARKER_TYPE.CLIENT, factory.getClientSPGProvider(), artyEquipmentUDO, areaRadius, interval=0.0 if BattleReplay.g_replayCtrl.isPlaying else 0.1)


def createArcadeArtilleryHit(artyEquipmentUDO, areaRadius):
    factory = _GunMarkersDPFactory()
    return _ArcadeArtilleryHitMarkerController(_MARKER_TYPE.CLIENT, factory.getClientSPGProvider(), artyEquipmentUDO, areaRadius, interval=0.0 if BattleReplay.g_replayCtrl.isPlaying else 0.1)


if _IS_EXTENDED_GUN_MARKER_ENABLED:

    def createShotResultResolver():
        return _CrosshairShotResults


else:

    def createShotResultResolver():
        return _StandardShotResult


class _StandardShotResult(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def getShotResult(cls, hitPoint, collision, _, excludeTeam=0, piercingMultiplier=1):
        if collision is None:
            return _SHOT_RESULT.UNDEFINED
        else:
            entity = collision.entity
            if entity.health <= 0 or entity.publicInfo['team'] == excludeTeam:
                return _SHOT_RESULT.UNDEFINED
            player = BigWorld.player()
            if player is None:
                return _SHOT_RESULT.UNDEFINED
            vDesc = player.getVehicleDescriptor()
            ppDesc = vDesc.shot.piercingPower
            maxDist = vDesc.shot.maxDistance
            dist = (hitPoint - player.getOwnVehiclePosition()).length
            constantsModification = cls.__sessionProvider.arenaVisitor.modifiers.getConstantsModification()
            piercingPower = _computePiercingPowerAtDistImpl(dist, maxDist, ppDesc[0] * piercingMultiplier, ppDesc[1] * piercingMultiplier, constantsModification.PIERCING_POWER_INTERPOLATION_DIST_FIRST, constantsModification.PIERCING_POWER_INTERPOLATION_DIST_LAST)
            piercingPercent = 1000.0
            if piercingPower > 0.0:
                armor = collision.armor
                piercingPercent = 100.0 + (armor - piercingPower) / piercingPower * 100.0
            if piercingPercent >= 150:
                result = _SHOT_RESULT.NOT_PIERCED
            elif 90 < piercingPercent < 150:
                result = _SHOT_RESULT.LITTLE_PIERCED
            else:
                result = _SHOT_RESULT.GREAT_PIERCED
            return result


class _CrosshairShotResults(object):
    _PP_RANDOM_ADJUSTMENT_MAX = 0.5
    _PP_RANDOM_ADJUSTMENT_MIN = 0.5
    _MAX_HIT_ANGLE_BOUND = math.pi / 2.0 - 1e-05
    _CRIT_ONLY_SHOT_RESULT = _SHOT_RESULT.NOT_PIERCED
    _VEHICLE_TRACE_BACKWARD_LENGTH = 0.1
    _VEHICLE_TRACE_FORWARD_LENGTH = 20.0
    shellExtraData = namedtuple('shellExtraData', ('hasNormalization', 'mayRicochet', 'checkCaliberForRicochet', 'jetLossPPByDist'))
    _SHELL_EXTRA_DATA = {constants.SHELL_TYPES.ARMOR_PIERCING: shellExtraData(True, True, True, 0.0),
     constants.SHELL_TYPES.ARMOR_PIERCING_CR: shellExtraData(True, True, True, 0.0),
     constants.SHELL_TYPES.ARMOR_PIERCING_HE: shellExtraData(True, False, False, 0.0),
     constants.SHELL_TYPES.HOLLOW_CHARGE: shellExtraData(False, True, False, 0.5),
     constants.SHELL_TYPES.HIGH_EXPLOSIVE: shellExtraData(False, False, False, 0.0)}
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def _getAllCollisionDetails(cls, hitPoint, direction, entity):
        startPoint = hitPoint - direction * cls._VEHICLE_TRACE_BACKWARD_LENGTH
        endPoint = hitPoint + direction * cls._VEHICLE_TRACE_FORWARD_LENGTH
        return entity.collideSegmentExt(startPoint, endPoint)

    @classmethod
    def _computePiercingPowerAtDist(cls, ppDesc, dist, maxDist, piercingMultiplier):
        constantsModification = cls.__sessionProvider.arenaVisitor.modifiers.getConstantsModification()
        return _computePiercingPowerAtDistImpl(dist, maxDist, ppDesc[0] * piercingMultiplier, ppDesc[1] * piercingMultiplier, constantsModification.PIERCING_POWER_INTERPOLATION_DIST_FIRST, constantsModification.PIERCING_POWER_INTERPOLATION_DIST_LAST)

    @classmethod
    def _computePiercingPowerRandomization(cls, shell):
        piercingPowerRandomization = shell.piercingPowerRandomization
        return _computePiercingPowerRandomizationImpl(piercingPowerRandomization, cls._PP_RANDOM_ADJUSTMENT_MIN, cls._PP_RANDOM_ADJUSTMENT_MAX)

    @classmethod
    def _shouldRicochet(cls, shell, hitAngleCos, matInfo):
        if not matInfo.mayRicochet:
            return False
        shellExtraData = cls._SHELL_EXTRA_DATA[shell.kind]
        if not shellExtraData.mayRicochet:
            return False
        armor = matInfo.armor
        if armor == 0:
            return False
        if hitAngleCos <= shell.type.ricochetAngleCos:
            if not matInfo.checkCaliberForRichet:
                return True
            if not shellExtraData.checkCaliberForRicochet:
                return True
            if armor * 3 >= shell.caliber:
                return True
        return False

    @classmethod
    def _computePenetrationArmor(cls, shell, hitAngleCos, matInfo):
        armor = matInfo.armor
        if not matInfo.useHitAngle:
            return armor
        normalizationAngle = 0.0
        shellExtraData = cls._SHELL_EXTRA_DATA[shell.kind]
        if shellExtraData.hasNormalization:
            normalizationAngle = shell.type.normalizationAngle
        if normalizationAngle > 0.0 and hitAngleCos < 1.0:
            if matInfo.checkCaliberForHitAngleNorm:
                if shell.caliber > armor * 2 > 0:
                    normalizationAngle *= 1.4 * shell.caliber / (armor * 2)
            hitAngle = math.acos(hitAngleCos) - normalizationAngle
            if hitAngle < 0.0:
                hitAngleCos = 1.0
            else:
                if hitAngle > cls._MAX_HIT_ANGLE_BOUND:
                    hitAngle = cls._MAX_HIT_ANGLE_BOUND
                hitAngleCos = math.cos(hitAngle)
        if hitAngleCos < 1e-05:
            hitAngleCos = 1e-05
        return armor / hitAngleCos

    @classmethod
    def getShotResult(cls, hitPoint, collision, direction, excludeTeam=0, piercingMultiplier=1):
        if collision is None:
            cls.__sendDebugInfo([])
            return _SHOT_RESULT.UNDEFINED
        else:
            entity = collision.entity
            if not isinstance(entity, (VehicleEntity, DestructibleEntity)):
                cls.__sendDebugInfo([])
                return _SHOT_RESULT.UNDEFINED
            if entity.health <= 0 or entity.publicInfo['team'] == excludeTeam:
                cls.__sendDebugInfo([])
                return _SHOT_RESULT.UNDEFINED
            player = BigWorld.player()
            if player is None:
                cls.__sendDebugInfo([])
                return _SHOT_RESULT.UNDEFINED
            vDesc = player.getVehicleDescriptor()
            shell = vDesc.shot.shell
            shellKind = shell.kind
            ppDesc = vDesc.shot.piercingPower
            maxDist = vDesc.shot.maxDistance
            dist = (hitPoint - player.getOwnVehiclePosition()).length
            fullPiercingPower = cls._computePiercingPowerAtDist(ppDesc, dist, maxDist, piercingMultiplier)
            collisionsDetails = cls._getAllCollisionDetails(hitPoint, direction, entity)
            if collisionsDetails is None:
                cls.__sendDebugInfo([])
                return _SHOT_RESULT.UNDEFINED
            minPP, maxPP = cls._computePiercingPowerRandomization(shell)
            return cls.__shotResultModernHE(collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity) if shellKind == constants.SHELL_TYPES.HIGH_EXPLOSIVE and shell.type.mechanics == constants.SHELL_MECHANICS_TYPE.MODERN else cls.__shotResultDefault(collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity)

    @classmethod
    def __shotResultModernHE(cls, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity):
        result = _SHOT_RESULT.NOT_PIERCED
        ignoredMaterials = set()
        piercingPower = fullPiercingPower
        dispersion = round(piercingPower) * shell.piercingPowerRandomization
        minPiercingPower = round(round(piercingPower) - dispersion)
        maxPiercingPower = round(round(piercingPower) + dispersion)
        explosionDamageAbsorption = 0
        debugPiercingsList = []
        for cDetails in collisionsDetails:
            if not cls.__isDestructibleComponent(entity, cDetails.compName):
                return result
            matInfo = cDetails.matInfo
            if matInfo is not None and (cDetails.compName, matInfo.kind) not in ignoredMaterials:
                hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
                piercingPercent = 1000.0
                penetrationArmor = 0
                if fullPiercingPower > 0.0:
                    penetrationArmor = cls._computePenetrationArmor(shell, hitAngleCos, matInfo)
                    piercingPercent = 100.0 + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                if matInfo.vehicleDamageFactor:
                    piercingPower -= penetrationArmor
                    minPiercingPower = round(minPiercingPower - penetrationArmor)
                    maxPiercingPower = round(maxPiercingPower - penetrationArmor)
                    if piercingPercent <= minPP and explosionDamageAbsorption == 0:
                        result = _SHOT_RESULT.GREAT_PIERCED
                    else:
                        result = _SHOT_RESULT.LITTLE_PIERCED
                    cls.__collectDebugPiercingData(debugPiercingsList, penetrationArmor, hitAngleCos, minPiercingPower, maxPiercingPower, piercingPercent, matInfo, result)
                    cls.__sendDebugInfo(debugPiercingsList, minPP, maxPP, fullPiercingPower)
                    return result
                if shell.type.shieldPenetration:
                    shieldPenetration = penetrationArmor * MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
                    piercingPower -= shieldPenetration
                    minPiercingPower = round(minPiercingPower - shieldPenetration)
                    maxPiercingPower = round(maxPiercingPower - shieldPenetration)
                    explosionDamageAbsorption += penetrationArmor * MODERN_HE_DAMAGE_ABSORPTION_FACTOR
                if piercingPercent > maxPP or not shell.type.shieldPenetration or explosionDamageAbsorption >= shell.type.maxDamage:
                    cls.__collectDebugPiercingData(debugPiercingsList, penetrationArmor, hitAngleCos, minPiercingPower, maxPiercingPower, piercingPercent, matInfo, _SHOT_RESULT.NOT_PIERCED)
                    cls.__sendDebugInfo(debugPiercingsList, minPP, maxPP, fullPiercingPower)
                    return _SHOT_RESULT.NOT_PIERCED
                if matInfo.extra and piercingPercent <= maxPP:
                    cls.__collectDebugPiercingData(debugPiercingsList, penetrationArmor, hitAngleCos, minPiercingPower, maxPiercingPower, piercingPercent, matInfo, cls._CRIT_ONLY_SHOT_RESULT)
                    result = cls._CRIT_ONLY_SHOT_RESULT
                if matInfo.collideOnceOnly:
                    ignoredMaterials.add((cDetails.compName, matInfo.kind))

        cls.__sendDebugInfo(debugPiercingsList, minPP, maxPP, fullPiercingPower)
        return result

    @classmethod
    def __shotResultDefault(cls, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity):
        result = _SHOT_RESULT.NOT_PIERCED
        isJet = False
        jetStartDist = None
        piercingPower = fullPiercingPower
        dispersion = round(piercingPower) * shell.piercingPowerRandomization
        minPiercingPower = round(round(piercingPower) - dispersion)
        maxPiercingPower = round(round(piercingPower) + dispersion)
        ignoredMaterials = set()
        debugPiercingsList = []
        for cDetails in collisionsDetails:
            if not cls.__isDestructibleComponent(entity, cDetails.compName):
                break
            if isJet:
                jetDist = cDetails.dist - jetStartDist
                if jetDist > 0.0:
                    lossByDist = 1.0 - jetDist * cls._SHELL_EXTRA_DATA[shell.kind].jetLossPPByDist
                    piercingPower *= lossByDist
                    minPiercingPower = round(minPiercingPower * lossByDist)
                    maxPiercingPower = round(maxPiercingPower * lossByDist)
            if cDetails.matInfo is None:
                result = cls._CRIT_ONLY_SHOT_RESULT
            else:
                matInfo = cDetails.matInfo
                if (cDetails.compName, matInfo.kind) in ignoredMaterials:
                    continue
                if matInfo.armor is None:
                    result = _SHOT_RESULT.UNDEFINED
                    _logger.error('Unconfigured/default material/armor for material kind %d', matInfo.kind)
                    continue
                hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
                piercingPercent = 1000.0
                if not isJet and cls._shouldRicochet(shell, hitAngleCos, matInfo):
                    cls.__collectDebugPiercingData(debugPiercingsList, None, hitAngleCos, minPiercingPower, maxPiercingPower, piercingPercent, matInfo, _SHOT_RESULT.NOT_PIERCED)
                    break
                penetrationArmor = 0
                if piercingPower > 0.0:
                    penetrationArmor = cls._computePenetrationArmor(shell, hitAngleCos, matInfo)
                    piercingPercent = 100.0 + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                    piercingPower -= penetrationArmor
                    minPiercingPower = round(minPiercingPower - penetrationArmor)
                    maxPiercingPower = round(maxPiercingPower - penetrationArmor)
                if matInfo.vehicleDamageFactor:
                    if minPP < piercingPercent < maxPP:
                        result = _SHOT_RESULT.LITTLE_PIERCED
                    elif piercingPercent <= minPP:
                        result = _SHOT_RESULT.GREAT_PIERCED
                    cls.__collectDebugPiercingData(debugPiercingsList, penetrationArmor, hitAngleCos, minPiercingPower, maxPiercingPower, piercingPercent, matInfo, result)
                    break
                else:
                    debugResut = _SHOT_RESULT.NOT_PIERCED
                    if minPP < piercingPercent < maxPP:
                        debugResut = _SHOT_RESULT.LITTLE_PIERCED
                    elif piercingPercent <= minPP:
                        debugResut = _SHOT_RESULT.GREAT_PIERCED
                    if matInfo.extra:
                        if piercingPercent <= maxPP:
                            result = cls._CRIT_ONLY_SHOT_RESULT
                    cls.__collectDebugPiercingData(debugPiercingsList, penetrationArmor, hitAngleCos, minPiercingPower, maxPiercingPower, piercingPercent, matInfo, debugResut)
                if matInfo.collideOnceOnly:
                    ignoredMaterials.add((cDetails.compName, matInfo.kind))
            if piercingPower <= 0.0:
                break
            if cls._SHELL_EXTRA_DATA[shell.kind].jetLossPPByDist > 0.0:
                isJet = True
                mInfo = cDetails.matInfo
                armor = mInfo.armor if mInfo is not None else 0.0
                jetStartDist = cDetails.dist + armor * 0.001

        cls.__sendDebugInfo(debugPiercingsList, minPP, maxPP, fullPiercingPower)
        return result

    @classmethod
    def __isDestructibleComponent(cls, entity, componentID):
        return entity.isDestructibleComponent(componentID) if isinstance(entity, DestructibleEntity) else True

    @classmethod
    def __collectDebugPiercingData(cls, piercingList, penetrationArmor, hitAngleCos, minPPower, maxPPower, piercingPercent, matInfo, result):
        if constants.IS_DEVELOPMENT:
            piercingList.append({'penetrationArmor': penetrationArmor,
             'angle': math.degrees(math.acos(hitAngleCos)),
             'minPPowerLeft': minPPower,
             'maxPPowerLeft': maxPPower,
             'piercingPercent': piercingPercent,
             'matInfo': matInfo,
             'result': result})

    @classmethod
    def __sendDebugInfo(cls, piercingData, minPP=None, maxPP=None, fullPP=None):
        if constants.IS_DEVELOPMENT:
            g_eventBus.handleEvent(GunMarkerEvent(GunMarkerEvent.UPDATE_PIERCING_DATA, ctx={'piercingData': piercingData,
             'minPP': minPP,
             'maxPP': maxPP,
             'fullPP': fullPP}), scope=EVENT_BUS_SCOPE.BATTLE)


def _setupGunMarkerSizeLimits(dataProvider, scale=None):
    if scale is None:
        settingsCore = dependency.instance(ISettingsCore)
        scale = settingsCore.interfaceScale.get()
    limits = (aih_constants.GUN_MARKER_MIN_SIZE * scale, min(GUI.screenResolution()))
    dataProvider.sizeConstraint = limits
    return limits


class IGunMarkerController(object):

    def create(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def update(self, markerType, position, direction, size, sizeOffset, relaxTime, collData):
        raise NotImplementedError

    def setFlag(self, positive, bit):
        raise NotImplementedError

    def getPosition(self):
        raise NotImplementedError

    def setPosition(self, position):
        raise NotImplementedError

    def setVisible(self, flag):
        raise NotImplementedError

    def onRecreateDevice(self):
        raise NotImplementedError

    def getSizes(self):
        raise NotImplementedError

    def setSizes(self, newSizes):
        raise NotImplementedError


class _GunMarkersDPFactory(object):
    __clientDataProvider = aih_global_binding.bindRW(_BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER)
    __serverDataProvider = aih_global_binding.bindRW(_BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER)
    __clientSPGDataProvider = aih_global_binding.bindRW(_BINDING_ID.CLIENT_SPG_GUN_MARKER_DATA_PROVIDER)
    __serverSPGDataProvider = aih_global_binding.bindRW(_BINDING_ID.SERVER_SPG_GUN_MARKER_DATA_PROVIDER)
    __dualAccDataProvider = aih_global_binding.bindRW(_BINDING_ID.DUAL_ACC_GUN_MARKER_DATA_PROVIDER)

    def getClientProvider(self):
        if self.__clientDataProvider is None:
            self.__clientDataProvider = self._makeDefaultProvider()
        return self.__clientDataProvider

    def getServerProvider(self):
        if self.__serverDataProvider is None:
            self.__serverDataProvider = self._makeDefaultProvider()
        return self.__serverDataProvider

    def getClientSPGProvider(self):
        if self.__clientSPGDataProvider is None:
            self.__clientSPGDataProvider = self._makeSPGProvider()
        return self.__clientSPGDataProvider

    def getServerSPGProvider(self):
        if self.__serverSPGDataProvider is None:
            self.__serverSPGDataProvider = self._makeSPGProvider()
        return self.__serverSPGDataProvider

    def getDualAccuracyProvider(self):
        if self.__dualAccDataProvider is None:
            self.__dualAccDataProvider = self._makeDefaultProvider()
        return self.__dualAccDataProvider

    @staticmethod
    def _makeDefaultProvider():
        dataProvider = GUI.WGGunMarkerDataProvider()
        dataProvider.positionMatrixProvider = Math.MatrixAnimation()
        dataProvider.setStartSizes(_setupGunMarkerSizeLimits(dataProvider)[0], 0.0)
        return dataProvider

    @staticmethod
    def _makeSPGProvider():
        dataProvider = GUI.WGSPGGunMarkerDataProvider(aih_constants.SPG_GUN_MARKER_ELEMENTS_COUNT, aih_constants.SPG_GUN_MARKER_ELEMENTS_RATE)
        dataProvider.positionMatrixProvider = Math.MatrixAnimation()
        dataProvider.maxTime = 7.0
        dataProvider.serverTickLength = constants.SERVER_TICK_LENGTH
        dataProvider.sizeScaleRate = aih_constants.SPG_GUN_MARKER_SCALE_RATE
        dataProvider.sizeConstraint = (aih_constants.SPG_GUN_MARKER_MIN_SIZE, aih_constants.SPG_GUN_MARKER_MAX_SIZE)
        dataProvider.setRelaxTime(constants.SERVER_TICK_LENGTH)
        return dataProvider


class _GunMarkersDecorator(IGunMarkerController):
    __gunMarkersFlags = aih_global_binding.bindRW(_BINDING_ID.GUN_MARKERS_FLAGS)
    __clientState = aih_global_binding.bindRW(_BINDING_ID.CLIENT_GUN_MARKER_STATE)
    __serverState = aih_global_binding.bindRW(_BINDING_ID.SERVER_GUN_MARKER_STATE)
    __dualAccState = aih_global_binding.bindRW(_BINDING_ID.DUAL_ACC_GUN_MARKER_STATE)

    def __init__(self, clientMarker, serverMarker, dualAccMarker):
        super(_GunMarkersDecorator, self).__init__()
        self.__clientMarker = clientMarker
        self.__serverMarker = serverMarker
        self.__dualAccMarker = dualAccMarker

    def create(self):
        self.__clientMarker.create()
        self.__serverMarker.create()
        self.__dualAccMarker.create()

    def destroy(self):
        self.__clientMarker.destroy()
        self.__serverMarker.destroy()
        self.__dualAccMarker.destroy()

    def enable(self):
        self.__clientMarker.enable()
        self.__clientMarker.setPosition(self.__clientState[0])
        self.__serverMarker.enable()
        self.__serverMarker.setPosition(self.__serverState[0])
        self.__dualAccMarker.enable()
        self.__dualAccMarker.setPosition(self.__dualAccState[0])

    def disable(self):
        self.__clientMarker.disable()
        self.__serverMarker.disable()
        self.__dualAccMarker.disable()

    def reset(self):
        self.__clientMarker.reset()
        self.__serverMarker.reset()
        self.__dualAccMarker.reset()

    def onRecreateDevice(self):
        self.__clientMarker.onRecreateDevice()
        self.__serverMarker.onRecreateDevice()
        self.__dualAccMarker.onRecreateDevice()

    def getPosition(self, markerType=_MARKER_TYPE.CLIENT):
        if markerType == _MARKER_TYPE.CLIENT:
            return self.__clientMarker.getPosition()
        if markerType == _MARKER_TYPE.SERVER:
            return self.__serverMarker.getPosition()
        if markerType == _MARKER_TYPE.DUAL_ACC:
            return self.__dualAccMarker.getPosition()
        _logger.warning('Gun maker control is not found by type: %d', markerType)
        return Math.Vector3()

    def setPosition(self, position, markerType=_MARKER_TYPE.CLIENT):
        if markerType == _MARKER_TYPE.CLIENT:
            self.__clientMarker.setPosition(position)
        elif markerType == _MARKER_TYPE.SERVER:
            self.__serverMarker.setPosition(position)
        elif markerType == _MARKER_TYPE.DUAL_ACC:
            self.__dualAccMarker.setPosition(position)
        else:
            _logger.warning('Gun maker control is not found by type: %d', markerType)

    def setFlag(self, positive, bit):
        if positive:
            self.__gunMarkersFlags |= bit
            if bit == _MARKER_FLAG.SERVER_MODE_ENABLED:
                self.__serverMarker.setPosition(self.__clientMarker.getPosition())
                self.__serverMarker.setSizes(self.__clientMarker.getSizes())
        else:
            self.__gunMarkersFlags &= ~bit

    def update(self, markerType, position, direction, size, sizeOffset, relaxTime, collData):
        if markerType == _MARKER_TYPE.CLIENT:
            self.__clientState = (position, direction, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                self.__clientMarker.update(markerType, position, direction, size, sizeOffset, relaxTime, collData)
        elif markerType == _MARKER_TYPE.SERVER:
            self.__serverState = (position, direction, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.SERVER_MODE_ENABLED:
                self.__serverMarker.update(markerType, position, direction, size, sizeOffset, relaxTime, collData)
        elif markerType == _MARKER_TYPE.DUAL_ACC:
            self.__dualAccState = (position, direction, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                self.__dualAccMarker.update(markerType, position, direction, size, sizeOffset, relaxTime, collData)
        else:
            _logger.warning('Gun maker control is not found by type: %d', markerType)

    def setVisible(self, flag):
        pass

    def getSizes(self):
        pass

    def setSizes(self, newSizes):
        pass


class _GunMarkerController(IGunMarkerController):
    _gunMarkersFlags = aih_global_binding.bindRW(_BINDING_ID.GUN_MARKERS_FLAGS)

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(_GunMarkerController, self).__init__()
        self._gunMarkerType = gunMakerType
        self._dataProvider = dataProvider
        self._enabledFlag = enabledFlag
        self._position = Math.Vector3()

    def create(self):
        pass

    def destroy(self):
        self._dataProvider = None
        return

    def enable(self):
        if self._enabledFlag != _MARKER_FLAG.UNDEFINED:
            self.setFlag(True, self._enabledFlag)

    def disable(self):
        if self._enabledFlag != _MARKER_FLAG.UNDEFINED:
            self.setFlag(False, self._enabledFlag)

    def reset(self):
        pass

    def update(self, markerType, position, direction, size, sizeOffset, relaxTime, collData):
        if self._gunMarkerType == markerType:
            self._position = position
        else:
            _logger.warning('Position can not be defined, type of marker does not equal: required = %d, received = %d', self._gunMarkerType, markerType)

    def setFlag(self, positive, bit):
        if positive:
            self._gunMarkersFlags |= bit
        else:
            self._gunMarkersFlags &= ~bit

    def onRecreateDevice(self):
        pass

    def getPosition(self):
        return self._position

    def setPosition(self, position):
        self._position = position
        positionMatrix = Math.Matrix()
        positionMatrix.setTranslate(position)
        self._updateMatrixProvider(positionMatrix)

    def setVisible(self, flag):
        pass

    def getSizes(self):
        pass

    def setSizes(self, newSizes):
        pass

    def _updateMatrixProvider(self, positionMatrix, relaxTime=0.0):
        animationMatrix = self._dataProvider.positionMatrixProvider
        animationMatrix.keyframes = ((0.0, Math.Matrix(animationMatrix)), (relaxTime, positionMatrix))
        animationMatrix.time = 0.0


class _EmptyGunMarkerController(_GunMarkerController):

    def setPosition(self, position):
        pass

    def update(self, markerType, position, direction, size, sizeOffset, relaxTime, collData):
        pass


class _DefaultGunMarkerController(_GunMarkerController):
    settingsCore = dependency.descriptor(ISettingsCore)
    _OFFSET_DEFAULT_INERTNESS = 1.0
    _OFFSET_SLOWDOWN_INERTNESS = 0.7

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(_DefaultGunMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=enabledFlag)
        self.__currentSize = self.__currentSizeOffset = 0.0
        self.__offsetInertness = self._OFFSET_DEFAULT_INERTNESS
        self.__screenRatio = 0.0

    def create(self):
        self.settingsCore.interfaceScale.onScaleChanged += self.__onScaleChanged

    def destroy(self):
        self.settingsCore.interfaceScale.onScaleChanged -= self.__onScaleChanged
        super(_DefaultGunMarkerController, self).destroy()

    def enable(self):
        super(_DefaultGunMarkerController, self).enable()
        self.__offsetInertness = self._OFFSET_DEFAULT_INERTNESS
        self.__updateScreenRatio()

    def update(self, markerType, pos, direction, size, sizeOffset, relaxTime, collData):
        super(_DefaultGunMarkerController, self).update(markerType, pos, direction, size, sizeOffset, relaxTime, collData)
        positionMatrix = Math.Matrix()
        positionMatrix.setTranslate(pos)
        self._updateMatrixProvider(positionMatrix, relaxTime)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            s = self._replayReader(replayCtrl)()
            if s != -1.0:
                size = s
        elif replayCtrl.isRecording:
            if replayCtrl.isServerAim and self._gunMarkerType == _MARKER_TYPE.SERVER:
                self._replayWriter(replayCtrl)(size)
            elif self._gunMarkerType in (_MARKER_TYPE.CLIENT, _MARKER_TYPE.DUAL_ACC):
                self._replayWriter(replayCtrl)(size)
        positionMatrixForScale = BigWorld.checkAndRecalculateIfPositionInExtremeProjection(positionMatrix)
        worldMatrix = _makeWorldMatrix(positionMatrixForScale)
        self.__currentSize = BigWorld.markerHelperScale(worldMatrix, size) * self.__screenRatio
        self.__currentSizeOffset = BigWorld.markerHelperScale(worldMatrix, sizeOffset) * self.__screenRatio
        self._dataProvider.updateSizes(self.__currentSize, self.__currentSizeOffset, relaxTime, self.__offsetInertness)
        if self.__offsetInertness == self._OFFSET_DEFAULT_INERTNESS:
            self.__offsetInertness = self._OFFSET_SLOWDOWN_INERTNESS

    def getSizes(self):
        return (self.__currentSize, self.__currentSizeOffset)

    def setSizes(self, newSizes):
        self.__currentSize, self.__currentSizeOffset = newSizes
        self._dataProvider.setStartSizes(*newSizes)

    def onRecreateDevice(self):
        self.__updateScreenRatio()

    def _replayReader(self, replayCtrl):
        return replayCtrl.getArcadeGunMarkerSize

    def _replayWriter(self, replayCtrl):
        return replayCtrl.setArcadeGunMarkerSize

    def __updateScreenRatio(self):
        self.__screenRatio = GUI.screenResolution()[0] * 0.5

    def __onScaleChanged(self, scale):
        _setupGunMarkerSizeLimits(self._dataProvider, scale=scale)

    def __checkAndRecalculateIfPositionInExtremeProjection(self, positionMatrix):
        if not _ENABLED_MAX_PROJECTION_CHECK:
            return positionMatrix
        camera = BigWorld.camera()
        cameraDirection = camera.direction
        cameraPosition = camera.position
        shotDirection = positionMatrix.applyToOrigin() - cameraPosition
        shotDistance = shotDirection.length
        shotDirection.normalise()
        dotProduct = cameraDirection.dot(shotDirection)
        if -_MAX_PROJECTION_ANGLE_COS < dotProduct < _MAX_PROJECTION_ANGLE_COS:
            rotationMatrix = Math.Matrix()
            rotationMatrix.setRotateY(_MAX_PROJECTION_ANGLE_COS)
            rotationMatrix.postMultiply(BigWorld.camera().invViewMatrix)
            newShotDirection = rotationMatrix.applyToAxis(2)
            newShotPosition = cameraPosition + shotDistance * newShotDirection
            positionMatrix = Math.Matrix()
            positionMatrix.setTranslate(newShotPosition)
        return positionMatrix


class _DualAccMarkerController(_DefaultGunMarkerController):

    def _replayReader(self, replayCtrl):
        return replayCtrl.getDualAccMarkerSize

    def _replayWriter(self, replayCtrl):
        return replayCtrl.setDualAccMarkerSize


class _SPGGunMarkerController(_GunMarkerController):
    _BIG_RELAX_TIME = 9999
    __slots__ = ('_size', '_gunRotator', '_shotSpeed', '_shotGravity')

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(_SPGGunMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=enabledFlag)
        self._size = 0.0
        self._gunRotator = None
        self._shotSpeed = 0
        self._shotGravity = 0
        self.__defaultRelaxTime = constants.SERVER_TICK_LENGTH
        return

    def enable(self):
        super(_SPGGunMarkerController, self).enable()
        player = BigWorld.player()
        self._gunRotator = player.gunRotator
        shotDescr = player.getVehicleDescriptor().shot
        self._shotSpeed = shotDescr.speed
        self._shotGravity = shotDescr.gravity
        self.__defaultRelaxTime = self.__getCurrentRelaxTime()
        player.onGunShotChanged += self.__onGunShotChanged

    def disable(self):
        if not almostZero(self.__getCurrentRelaxTime() - self.__defaultRelaxTime):
            self._dataProvider.setRelaxTime(self.__defaultRelaxTime)
        player = BigWorld.player()
        if player is not None:
            player.onGunShotChanged -= self.__onGunShotChanged
        self._gunRotator = None
        self._shotSpeed = 0.0
        self._shotGravity = 0.0
        super(_SPGGunMarkerController, self).disable()
        return

    def update(self, markerType, position, direction, size, sizeOffset, relaxTime, collData):
        super(_SPGGunMarkerController, self).update(markerType, position, direction, size, sizeOffset, relaxTime, collData)
        positionMatrix = Math.createTranslationMatrix(position)
        self._updateMatrixProvider(positionMatrix, relaxTime)
        self._size = size + sizeOffset
        self._update()

    def reset(self):
        self._dataProvider.reset()
        self._update()

    def _getCurrentShotInfo(self):
        gunMat = AimingSystems.getPlayerGunMat(self._gunRotator.turretYaw, self._gunRotator.gunPitch)
        position = gunMat.translation
        velocity = gunMat.applyVector(Math.Vector3(0, 0, self._shotSpeed))
        return (position, velocity, Math.Vector3(0, -self._shotGravity, 0))

    def _updateDispersionData(self):
        dispersionAngle = self._gunRotator.dispersionAngle
        isServerAim = self._gunMarkerType == _MARKER_TYPE.SERVER
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            d, s = replayCtrl.getSPGGunMarkerParams()
            if d != -1.0 and s != -1.0:
                dispersionAngle = d
        elif replayCtrl.isRecording:
            if replayCtrl.isServerAim and isServerAim:
                replayCtrl.setSPGGunMarkerParams(dispersionAngle, 0.0)
            elif not isServerAim:
                replayCtrl.setSPGGunMarkerParams(dispersionAngle, 0.0)
        self._dataProvider.setupConicDispersion(dispersionAngle)

    def _update(self):
        pos3d, vel3d, gravity3d = self._getCurrentShotInfo()
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            self.__updateRelaxTime()
        self._updateDispersionData()
        self._dataProvider.update(pos3d, vel3d, gravity3d, self._size)

    def __onGunShotChanged(self):
        shotDescr = BigWorld.player().getVehicleDescriptor().shot
        self._shotSpeed = shotDescr.speed
        self._shotGravity = shotDescr.gravity

    def __updateRelaxTime(self):
        currentRelaxTime = self.__getCurrentRelaxTime()
        relaxTime = self.__defaultRelaxTime
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            replaySpeed = replayCtrl.playbackSpeed
            if 0.0 < replaySpeed < 1.0:
                relaxTime = relaxTime / replaySpeed
            if not almostZero(relaxTime - currentRelaxTime):
                self._dataProvider.setRelaxTime(relaxTime)

    def __getCurrentRelaxTime(self):
        relaxTime = self._dataProvider.relaxTime
        return 1.0 / relaxTime if not almostZero(relaxTime) else self._BIG_RELAX_TIME


class _ArtyHitMarkerController(_SPGGunMarkerController):

    def __init__(self, gunMakerType, dataProvider, artyEquipmentUDO, areaRadius, interval=0.1):
        super(_ArtyHitMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.ARTY_HIT_ENABLED)
        self.__artyEquipmentUDO = artyEquipmentUDO
        self.__areaRadius = areaRadius
        self.__interval = interval
        self.__delayer = CallbackDelayer()
        self.__trajectoryDrawer = BigWorld.wg_trajectory_drawer()

    def create(self):
        super(_ArtyHitMarkerController, self).create()
        self.__trajectoryDrawer.setColors(Math.Vector4(0, 255, 0, 255), Math.Vector4(255, 0, 0, 255), Math.Vector4(128, 128, 128, 255))
        self.__trajectoryDrawer.setIgnoredIDs([BigWorld.player().playerVehicleID])

    def destroy(self):
        self.__artyEquipmentUDO = None
        if self.__trajectoryDrawer is not None:
            self.__trajectoryDrawer.visible = False
            self.__trajectoryDrawer = None
        if self.__delayer is not None:
            self.__delayer.destroy()
            self.__delayer = None
        super(_ArtyHitMarkerController, self).destroy()
        return

    def enable(self):
        super(_ArtyHitMarkerController, self).enable()
        self.__delayer.delayCallback(self.__interval, self.__tick)
        self.__trajectoryDrawer.setParams(1000.0, Math.Vector3(0, -self.__artyEquipmentUDO.gravity, 0), (0, 0))

    def disable(self):
        self.__delayer.stopCallback(self.__tick)
        super(_ArtyHitMarkerController, self).disable()

    def setVisible(self, flag):
        self.__trajectoryDrawer.visible = flag

    def getPointsInside(self, positions):
        return self._dataProvider.getPointsInside(positions)

    def _getCurrentShotInfo(self):
        launchPosition = self._position + self.__artyEquipmentUDO.position
        launchVelocity = self.__artyEquipmentUDO.launchVelocity
        gravity = Math.Vector3(0, -self.__artyEquipmentUDO.gravity, 0)
        return (launchPosition, launchVelocity, gravity)

    def _updateDispersionData(self):
        self._dataProvider.setupFlatRadialDispersion(self.__areaRadius)

    def __tick(self):
        self.__trajectoryDrawer.update(self._position, self._position + self.__artyEquipmentUDO.position, self.__artyEquipmentUDO.launchVelocity, self.__interval)
        return self.__interval


class _ArcadeArtilleryHitMarkerController(_SPGGunMarkerController):

    def __init__(self, gunMakerType, dataProvider, artyEquipmentUDO, areaRadius, interval=0.1):
        super(_ArcadeArtilleryHitMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.ARTY_HIT_ENABLED)
        self.__artyEquipmentUDO = artyEquipmentUDO
        self.__areaRadius = areaRadius
        self.__interval = interval

    def destroy(self):
        self.__artyEquipmentUDO = None
        super(_ArcadeArtilleryHitMarkerController, self).destroy()
        return

    def getPointsInside(self, positions):
        return self._dataProvider.getPointsInside(positions)

    def _getCurrentShotInfo(self):
        launchPosition = self._position + self.__artyEquipmentUDO.position
        launchVelocity = self.__artyEquipmentUDO.launchVelocity
        gravity = Math.Vector3(0, -self.__artyEquipmentUDO.gravity, 0)
        return (launchPosition, launchVelocity, gravity)

    def _updateDispersionData(self):
        self._dataProvider.setupFlatRadialDispersion(self.__areaRadius)


def _makeWorldMatrix(positionMatrix):
    sr = GUI.screenResolution()
    aspect = sr[0] / sr[1]
    return BigWorld.makeWorldMatrix(aspect, positionMatrix)


def _calcScale(worldMatrix, size):
    pointMat = Math.Matrix()
    pointMat.set(BigWorld.camera().matrix)
    transl = Math.Matrix()
    transl.setTranslate(Math.Vector3(size, 0, 0))
    pointMat.postMultiply(transl)
    pointMat.postMultiply(BigWorld.camera().invViewMatrix)
    p = pointMat.applyToOrigin()
    pV4 = worldMatrix.applyV4Point(Math.Vector4(p[0], p[1], p[2], 1))
    oV4 = worldMatrix.applyV4Point(Math.Vector4(0, 0, 0, 1))
    pV3 = Math.Vector3(pV4[0], pV4[1], pV4[2]).scale(1.0 / pV4[3])
    oV3 = Math.Vector3(oV4[0], oV4[1], oV4[2]).scale(1.0 / oV4[3])
    return math.fabs(pV3[0] - oV3[0]) + math.fabs(pV3[1] - oV3[1])
