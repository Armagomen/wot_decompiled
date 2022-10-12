# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/__init__.py
import logging.handlers
import math
from functools import wraps

import BigWorld
import Math
import math_utils
from Math import Vector3
from ProjectileMover import collideDynamicAndStatic, collideVehiclesAndStaticScene, EntityCollisionData
from math_utils import MatrixProviders
from vehicle_systems.tankStructure import TankPartNames

import ShadowEffect

_logger = logging.getLogger(__name__)
SPG_MINIMAL_AIMING_RADIUS = 15.0
SPG_MINIMAL_AIMING_RADIUS_SQ = SPG_MINIMAL_AIMING_RADIUS * SPG_MINIMAL_AIMING_RADIUS
SHOT_POINT_PLANAR_DEFAULT_MIN_DISTANCE = 50.0

class CollisionStrategy(object):
    COLLIDE_DYNAMIC_AND_STATIC = 0
    COLLIDE_VEHICLES_AND_STATIC_SCENE = 1

    @classmethod
    def getCollisionFunction(cls, collisionStrategy):
        if collisionStrategy == CollisionStrategy.COLLIDE_DYNAMIC_AND_STATIC:
            return collideDynamicAndStatic
        elif collisionStrategy == CollisionStrategy.COLLIDE_VEHICLES_AND_STATIC_SCENE:
            return collideVehiclesAndStaticScene
        else:
            _logger.error('CollisionStrategy: getCollisionFunction: Unknown strategy %i.', collisionStrategy)
            return None


class IAimingSystem(object):
    matrix = property(lambda self: self._matrix)

    def __init__(self):
        self._matrix = math_utils.createIdentityMatrix()

    @property
    def aimMatrix(self):
        return self._matrix

    def destroy(self):
        pass

    def enable(self, targetPos):
        pass

    def disable(self):
        pass

    def getDesiredShotPoint(self):
        pass

    def handleMovement(self, dx, dy):
        pass

    def update(self, deltaTime):
        pass

    def getShotPoint(self):
        return None

    def getZoom(self):
        return None

    def setAimingLimits(self, distances):
        pass


def getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw=0.0, overrideTurretLocalZ=None):
    turretOffset = getTurretJointOffset(vehicleTypeDescriptor)
    if overrideTurretLocalZ is not None:
        turretOffset.z = overrideTurretLocalZ
    turretJointMat = math_utils.createRTMatrix(Vector3(turretYaw, 0, 0), turretOffset)
    turretJointMat.postMultiply(vehicleMatrix)
    return turretJointMat


def getTurretJointOffset(vehicleTypeDescriptor):
    return vehicleTypeDescriptor.chassis.hullPosition + vehicleTypeDescriptor.hull.turretPositions[0]


def getGunJointMat(vehicleTypeDescriptor, turretMatrix, gunPitch, overrideTurretLocalZ=None):
    gunOffset = Vector3(vehicleTypeDescriptor.activeGunShotPosition)
    if overrideTurretLocalZ is not None:
        offset = getTurretJointOffset(vehicleTypeDescriptor)
        yOffset = math.tan(gunPitch) * offset.z
        gunOffset.y += yOffset
    gunMat = math_utils.createRTMatrix(Vector3(0, gunPitch, 0), gunOffset)
    gunMat.postMultiply(turretMatrix)
    return gunMat


def getPlayerTurretMats(turretYaw=0.0, gunPitch=0.0, overrideTurretLocalZ=None):
    player = BigWorld.player()
    if player.isObserver() and player.getVehicleAttached() is not None:
        vehicleTypeDescriptor = player.getVehicleAttached().typeDescriptor
    else:
        vehicleTypeDescriptor = player.vehicleTypeDescriptor
    isPitchHullAimingAvailable = vehicleTypeDescriptor.isPitchHullAimingAvailable
    vehicleMatrix = player.inputHandler.steadyVehicleMatrixCalculator.outputMProv
    correctGunPitch = gunPitch
    if isPitchHullAimingAvailable:
        vehicleMatrix = player.inputHandler.steadyVehicleMatrixCalculator.stabilisedMProv
        correctGunPitch = 0.0
    turretMat = getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw, overrideTurretLocalZ)
    gunMat = getGunJointMat(vehicleTypeDescriptor, turretMat, correctGunPitch, overrideTurretLocalZ)
    if not isPitchHullAimingAvailable:
        return (turretMat, gunMat)
    else:
        turretMatTranslation = turretMat.translation
        gunMatTranslation = gunMat.translation
        vehicleMatrix = player.inputHandler.steadyVehicleMatrixCalculator.outputMProv
        turretMat = getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw)
        gunMat = getGunJointMat(vehicleTypeDescriptor, turretMat, gunPitch)
        if overrideTurretLocalZ is not None:
            gunMatTranslation += _calculateGunPointOffsetFromHullCenter(vehicleTypeDescriptor, vehicleMatrix, player.inputHandler.steadyVehicleMatrixCalculator.stabilisedMProv, gunPitch, overrideTurretLocalZ)
        turretMat.translation = turretMatTranslation
        gunMat.translation = gunMatTranslation
        return (turretMat, gunMat)


def getPlayerGunMat(turretYaw=0.0, gunPitch=0.0, overrideTurretLocalZ=None):
    return getPlayerTurretMats(turretYaw, gunPitch, overrideTurretLocalZ)[1]


def getCenteredPlayerGunMat(turretYaw=0.0, gunPitch=0.0):
    return getPlayerTurretMats(turretYaw, gunPitch, 0.0)[1]


def getTurretMatrixProvider(vehicleTypeDescriptor, vehicleMatrixProvider, turretYawMatrixProvider):
    turretOffset = vehicleTypeDescriptor.chassis.hullPosition + vehicleTypeDescriptor.hull.turretPositions[0]
    return MatrixProviders.product(turretYawMatrixProvider, MatrixProviders.product(math_utils.createTranslationMatrix(turretOffset), vehicleMatrixProvider))


def getGunMatrixProvider(vehicleTypeDescriptor, turretMatrixProvider, gunPitchMatrixProvider):
    gunOffset = vehicleTypeDescriptor.activeGunShotPosition
    return MatrixProviders.product(gunPitchMatrixProvider, MatrixProviders.product(math_utils.createTranslationMatrix(gunOffset), turretMatrixProvider))


def getTurretYawGunPitch(vehTypeDescr, vehicleMatrix, targetPos, compensateGravity=False):
    turretOffs = vehTypeDescr.hull.turretPositions[0] + vehTypeDescr.chassis.hullPosition
    gunOffs = vehTypeDescr.activeGunShotPosition
    speed = vehTypeDescr.shot.speed
    gravity = vehTypeDescr.shot.gravity if not compensateGravity else 0.0
    return BigWorld.wg_getShotAngles(turretOffs, gunOffs, vehicleMatrix, speed, gravity, 0.0, 0.0, targetPos, False)


def _calculateGunPointOffsetFromHullCenter(vehicleTypeDescriptor, steadyMatrix, stabilisedMatrix, gunPitch, overrideTurretLocalZ):
    turretOffset = getTurretJointOffset(vehicleTypeDescriptor)
    hullLocal = Math.Matrix(steadyMatrix)
    hullLocal.invert()
    hullLocal.preMultiply(stabilisedMatrix)
    projectedOffset = math.cos(hullLocal.pitch) * abs(turretOffset.z - overrideTurretLocalZ)
    upVector = Math.Matrix(steadyMatrix).applyToAxis(1)
    upOffsetGunPitch = math.tan(-gunPitch) * projectedOffset
    upOffsetHullPitch = math.tan(hullLocal.pitch) * projectedOffset
    return upVector * (upOffsetGunPitch + upOffsetHullPitch)


def _getDesiredShotPointUncached(start, direction, onlyOnGround, isStrategicMode, terrainOnlyCheck, shotDistance):
    end = start + direction.scale(shotDistance)
    if isStrategicMode:
        if terrainOnlyCheck:
            return __collideTerrainOnly(start, end)
        point1 = __collideStaticOnly(start, end)
        point2 = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), skipGun=isStrategicMode)
        if point1 is None or point2 is None:
            point = None
        else:
            direction = Math.Vector3(point2[0]) - Math.Vector3(point1[0])
            point = (Math.Vector3(point1[0]) + direction.scale(0.5), None)
    else:
        point = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), skipGun=isStrategicMode)
    if point is not None:
        return point[0]
    else:
        return shootInSkyPoint(start, direction) if not onlyOnGround else None


g_desiredShotPoint = math_utils.VectorConstant.Vector3Zero
g_frameStamp = -1
__disableShotPointCache = False

def disableShotPointCache(f):

    def wrapped(*args, **kwargs):
        __disableShotPointCache = True
        f(*args, **kwargs)
        __disableShotPointCache = False

    return wrapped


def getDesiredShotPoint(start, direction, onlyOnGround=False, isStrategicMode=False, terrainOnlyCheck=False, shotDistance=10000.0):
    global g_desiredShotPoint
    global g_frameStamp
    currentFrameStamp = BigWorld.wg_getFrameTimestamp()
    if g_frameStamp == currentFrameStamp and not __disableShotPointCache:
        return g_desiredShotPoint
    g_frameStamp = currentFrameStamp
    g_desiredShotPoint = _getDesiredShotPointUncached(start, direction, onlyOnGround, isStrategicMode, terrainOnlyCheck, shotDistance)
    return g_desiredShotPoint


def _trackcalls(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        return func(*args, **kwargs)

    wrapper.has_been_called = False
    return wrapper


def getShotTargetInfo(vehicle, preferredTargetPoint, gunRotator):
    shotPos, shotVec, gravity = gunRotator.getShotParams(preferredTargetPoint, True)
    minBounds, maxBounds = BigWorld.player().arena.getArenaBB()
    endPos, direction, _, _ = getCappedShotTargetInfos(shotPos, shotVec, gravity, vehicle.typeDescriptor.shot, vehicle.id, minBounds, maxBounds, CollisionStrategy.COLLIDE_VEHICLES_AND_STATIC_SCENE)
    return (endPos, direction)


def getCappedShotTargetInfos(shotPos, shotVec, gravity, shotDescr, vehicleID, minBounds, maxBounds, collisionStrategy):
    endPos, direction, collData, usedMaxDistance = BigWorld.wg_getCappedShotTargetInfos(BigWorld.player().spaceID,
                                                                                        shotPos, shotVec, gravity,
                                                                                        shotDescr.maxDistance,
                                                                                        vehicleID, minBounds, maxBounds,
                                                                                        collisionStrategy)
    if collData is not None:
        collData = EntityCollisionData(*collData)
    return (endPos,
            direction,
            collData,
            usedMaxDistance)


@_trackcalls
def shootInSkyPointHelper():
    vehicle = BigWorld.player().vehicle
    if vehicle is not None and vehicle.inWorld and vehicle.isStarted and not vehicle.isTurretDetached:
        compoundModel = vehicle.appearance.compoundModel
        shotPos = Math.Vector3(compoundModel.node(TankPartNames.GUN).position)
        shotDesc = vehicle.typeDescriptor.shot
    else:
        vType = BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['vehicleType']
        shotPos = BigWorld.player().getOwnVehiclePosition()
        shotPos += vType.hull.turretPositions[0] + vType.activeGunShotPosition
        shotDesc = vType.shot
    return (shotPos, shotDesc.maxDistance)


@_trackcalls
def shootInSkyPoint(startPos, direction):
    dirFromCam = direction
    start = startPos
    dirFromCam.normalise()
    vehicle = BigWorld.player().vehicle
    if vehicle is not None and vehicle.inWorld and vehicle.isStarted and not vehicle.isTurretDetached:
        compoundModel = vehicle.appearance.compoundModel
        shotPos = Math.Vector3(compoundModel.node(TankPartNames.GUN).position)
        shotDesc = vehicle.typeDescriptor.shot
    else:
        vType = BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['vehicleType']
        shotPos = BigWorld.player().getOwnVehiclePosition()
        shotPos += vType.hull.turretPositions[0] + vType.activeGunShotPosition
        shotDesc = vType.shot
    dirAtCam = shotPos - start
    dirAtCam.normalise()
    cosAngle = dirAtCam.dot(dirFromCam)
    a = shotDesc.maxDistance
    b = shotPos.distTo(start)
    quadraticSubEquation = b * b * (cosAngle * cosAngle - 1) + a * a
    if quadraticSubEquation >= 0:
        dist = b * cosAngle + math.sqrt(quadraticSubEquation)
        if dist < 0.0:
            dist = shotDesc.maxDistance
    else:
        _logger.info("The point at distance from vehicle's gun can't be calculated. The maximum distance is set.")
        dist = shotDesc.maxDistance
    finalPoint = start + dirFromCam.scale(dist)
    _, intersecPoint = BigWorld.player().arena.collideWithSpaceBB(start, finalPoint)
    if intersecPoint is not None:
        finalPoint = intersecPoint
    return finalPoint


def __collideTerrainOnly(start, end):
    waterHeight = BigWorld.wg_collideWater(start, end, False)
    resultWater = None
    if waterHeight != -1:
        resultWater = start - Math.Vector3(0, waterHeight, 0)
    testResTerrain = BigWorld.wg_collideSegment(BigWorld.player().spaceID, start, end, 128, 8)
    result = testResTerrain.closestPoint if testResTerrain is not None else None
    if resultWater is not None:
        distance = (result - start).length
        if distance - waterHeight < 0.2:
            return result
        return resultWater
    else:
        return result


def __collideStaticOnly(startPoint, endPoint):
    res = None
    testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, 128)
    if testRes is not None:
        res = (testRes.closestPoint, None)
    return res


def getVehicleAngles(vehicleDescriptor):
    gunLimits = vehicleDescriptor.gun.pitchLimits
    gunAngleMin = gunLimits['minPitch'][0][1]
    gunAngleMax = gunLimits['maxPitch'][0][1]
    hullAngleMin = vehicleDescriptor.type.hullAimingParams['pitch']['wheelsCorrectionAngles']['pitchMin']
    hullAngleMax = vehicleDescriptor.type.hullAimingParams['pitch']['wheelsCorrectionAngles']['pitchMax']
    return (gunAngleMin,
            gunAngleMax,
            hullAngleMin,
            hullAngleMax)
