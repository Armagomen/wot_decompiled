# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/physics_shared.py
import BigWorld
import Math
import math
import collections
from items import vehicles
from items.components.component_constants import KMH_TO_MS
from items.vehicles import VEHICLE_PHYSICS_TYPE, VehicleDescriptor, VehicleDescrType
from constants import IS_CLIENT, IS_EDITOR, SERVER_TICK_LENGTH
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
import copy
from gun_rotation_shared import encodeRestrictedValueToUint, decodeRestrictedValueFromUint
from typing import Any
G = 9.81
GRAVITY_FACTOR = 1.25
WEIGHT_SCALE = 0.001
GRAVITY_FACTOR_SCALED = GRAVITY_FACTOR * WEIGHT_SCALE
PHYSICAL_INF = 1000000000
SUSP_COMPRESSION_MIN = 0.85
SUSP_COMPRESSION_MIN_MASS = 60.0
SUSP_COMPRESSION_MAX = 0.88
SUSP_COMPRESSION_MAX_MASS = 30.0
BODY_HEIGHT = 1.4
ROLLER_CONTACT_IGNORE_ANGLE = 25
ROLLER_HORIZONTAL_SURFACE_ANGLE = 35
SIDE_MOVEMENT_THRESHOLD = SERVER_TICK_LENGTH * 0.05
_SIMULATION_Y_BOUND = 1000.0
FREEZE_ANG_ACCEL_EPSILON = 0.35
FREEZE_ACCEL_EPSILON = 0.4
FREEZE_VEL_EPSILON = 0.15
FREEZE_ANG_VEL_EPSILON = 0.06
WIDTH_LONG = 6.2
WIDTH_VERY_LONG = 7.0
CLEARANCE_RATIO_LONG = 5.0
NUM_SPRINGS_LONG = 5
NUM_SPRINGS_NORMAL = 5
CMY_MIN = -0.15
CMY_MID = -0.2
CMY_MAX = -0.3
DYN_RATIO_MIN = 9.5
DYN_RATIO_MID = 13.0
DYN_RATIO_MAX = 21.0
CLEARANCE = 1.75
CLEARANCE_MIN = 0.55
CLEARANCE_MAX = 0.6
HARD_RATIO_MIN = 0.5
CLEARANCE_TO_LENGTH_MIN = 0.085
HARD_RATIO_MAX = 0.52
CLEARANCE_TO_LENGTH_MAX = 0.112
TRACK_LENGTH_MIN = 0.6
TRACK_LENGTH_MAX = 0.64
VEHICLE_ON_OBSTACLE_COLLISION_BOX_MIN_HEIGHT = 1.1
_LOG_INIT_PARAMS = False
RESTITUTION = 0.5
FRICTION_RATIO = 1.0
NUM_ITERATIONS = 10
NUM_ITERATIONS_ACCURATE = 40
MID_SOLVING_ITERATIONS = 4
NUM_SUBSTEPS_IN_STANDARD_MODE = 2
USE_SSE_SOLVER_IN_STANDARD_MODE = False
NUM_SUBSTEPS_IN_DETAILED_MODE = 3
USE_SSE_SOLVER_IN_DETAILED_MODE = False
NUM_SUBSTEPS = NUM_SUBSTEPS_IN_STANDARD_MODE
WARMSTARTING_VEHICLE_VEHICLE = False
WARMSTARTING_VEHICLE_STATICS = False
WARMSTARTING_THRESHOLD = 0.1
USE_PSEUDO_CONTACTS = True
ALLOWED_PENETRATION = 0.01
CONTACT_PENETRATION = 0.1
TRACKS_PENETRATION = 0.01
CONTACT_ENERGY_POW = 3.0
CONTACT_ENERGY_POW2 = 0.75
SLOPE_FRICTION_FUNC_DEF = Math.Vector3(tuple((math.pi * ang / 180.0 for ang in (34.0, 50.0, 70.0))))
SLOPE_FRICTION_FUNC_VAL = Math.Vector3(0.4, 2.0, 5.0)
SLOPE_FRICTION_MODELS_FUNC_VAL = Math.Vector3(0.4, 0.45, 0.5)
CONTACT_FRICTION_TERRAIN = 1.0
CONTACT_FRICTION_STATICS = 0.05
CONTACT_FRICTION_EXTRA = 0.3
CONTACT_FRICTION_DESTRUCTIBLES = 1.0
CONTACT_FRICTION_VEHICLES = 0.3
VEHICLE_ON_BODY_DEFAULT_FRICTION = 0.5
ROLLER_REACTION_COEFF_FOR_STATIC = 0.2
ROLLER_FRICTION_GAIN_MIN = 0.05
ROLLER_FRICTION_GAIN_MAX = 0.25
ROLLER_FRICTION_ANGLE_MIN = 20.0
ROLLER_FRICTION_ANGLE_MAX = 45.0
ANCHOR_MAX_REACTION_FACTOR = 0.5
ANCHOR_CONST_FRACTION = 0.0
ANCHOR_VEL_FACTOR = 0.0
ARENA_BOUNDS_FRICTION_HOR = 0.2
ARENA_BOUNDS_FRICTION_VERT = 1.0
_ALLOWER_RPM_EXCESS_UNBOUNDED = 1.4
_ABSOLUTE_SPEED_LIMIT = 25
ENGINE_RADIUS = 0.020000000000000004
g_confUpdaters = []

def _cosDeg(angle):
    return math.cos(math.radians(angle))


def _sinDeg(angle):
    return math.sin(math.radians(angle))


def getDefaultChassisXPhysicsCfg():
    return {'wheelRadius': 0.4,
     'wheelRestitution': 0.9,
     'wheelPenetration': 0.02,
     'wheelUsePseudoContacts': True,
     'wheelFwdInertiaFactor': 3.0,
     'sideFrictionConstantRatio': 0.0,
     'flatSideFriction': True,
     'wheelDetachOnRoll': False,
     'trackToBeLockedDelay': 1.0,
     'trackGaugeFactor': 0.96,
     'slopeResistTerrain': (1.5, _cosDeg(15.0), _sinDeg(29.0)),
     'slopeResistStaticObject': (1.5, _cosDeg(15.0), _sinDeg(29.0)),
     'slopeResistDynamicObject': (1.5, _cosDeg(15.0), _sinDeg(20.0)),
     'slopeGripLngTerrain': (_cosDeg(27.5),
                             1.0,
                             _cosDeg(32.0),
                             0.1),
     'slopeGripSdwTerrain': (_cosDeg(24.5),
                             1.0,
                             _cosDeg(29.0),
                             0.1),
     'slopeGripLngStaticObject': (_cosDeg(27.5),
                                  1.0,
                                  _cosDeg(32.0),
                                  0.1),
     'slopeGripSdwStaticObject': (_cosDeg(24.5),
                                  1.0,
                                  _cosDeg(29.0),
                                  0.1),
     'slopeGripLngDynamicObject': (_cosDeg(20.0),
                                   1.0,
                                   _cosDeg(25.0),
                                   0.1),
     'slopeGripSdwDynamicObject': (_cosDeg(20.0),
                                   1.0,
                                   _cosDeg(25.0),
                                   0.1),
     'stiffnessFactors': (1.0, 1.0, 1.0, 1.0, 1.0),
     'angVelocityFactor': 1.0,
     'angVelocityFactor0': 1.0,
     'gimletGoalWOnSpot': 1.0,
     'gimletGoalWOnMove': 1.0,
     'isRotationAroundCenter': False,
     'centerRotationFwdSpeed': 1.0,
     'movementRevertSpeed': 1.0,
     'fwLagRatio': 1.0,
     'bkLagRatio': 1.0,
     'rotFritionFactor': 1.0,
     'comFrictionYOffs': 1.0,
     'comSideFriction': 1.0,
     'pushStop': 1.0,
     'gimletPushOnSpotInit': 1.0,
     'gimletPushOnSpotFinal': 1.0,
     'gimletPushOnMoveInit': 1.0,
     'gimletPushOnMoveFinal': 1.0,
     'gimletVelScaleMin': 1.0,
     'gimletVelScaleMax': 1.0,
     'pushRotOnSpotFixedPeriod': 1.0,
     'pushRotOnMoveFixedPeriod': 1.0,
     'pushRotOnSpotGrowPeriod': 1.0,
     'pushRotOnMoveGrowPeriod': 1.0,
     'bodyHeight': 2.5,
     'hullCOMShiftY': -0.25,
     'hullInertiaFactors': (1.0, 1.0, 1.0),
     'clearance': 0.25,
     'rotationByLockChoker': 1.0,
     'chassisMassFraction': 0.3,
     'wheelSinkageResistFactor': 0.2,
     'wheelInertiaFactor': 1.5,
     'stiffness0': 1.0,
     'stiffness1': 1.0,
     'damping': 0.2,
     'brake': 1000.0,
     'rotationBrake': 1000.0,
     'roadWheelPositions': (-2.5, -1.25, 0.0, 1.25, 2.5),
     'brokenTrackLosses': {'enginePowerLoss': (0.0,),
                           'fwMaxSpeedLoss': (0.0,),
                           'bkMaxSpeedLoss': (0.0,),
                           'rotationSpeedLoss': (0.0,)}}


def getDeafultVehicleModelXPhysicsCfg():
    return {'hullSize': (0.0, 0.0, 0.0),
     'hullBoxOffsetZ': 0.0,
     'turretTopPos': (0.0, 0.0, 0.0),
     'turretTopWidth': 0.0}


def getDefaultWheeledVehicleModelXPhysicsCfg():
    return dict(getDeafultVehicleModelXPhysicsCfg(), **{'wheelSize': (0.0, 0.0, 0.0)})


def getDefaultWheeledChassisXPhysicsCfg():
    return dict(getDefaultChassisXPhysicsCfg(), **{'axleSteeringLockAngles': (0.0, 0.0, 0.0, 30.0),
     'axleSteeringAngles': (0.0, 0.0, 0.0, 15.0),
     'axleSteeringSpeed': (0.0, 0.0, 0.0, 90.0),
     'brokenWheelPowerLoss': (0.0, 0.0, 0.0, 0.0),
     'brokenWheelSpeedLoss': (0.0, 0.0, 0.0, 0.0),
     'brokenWheelRotationSpeedLoss': (0.0, 0.0, 0.0, 0.0),
     'fwdFrictionOnAxisModifiers': (1.0, 1.0, 1.0, 1.0),
     'sideFrictionOnAxisModifiers': (1.0, 1.0, 1.0, 1.0),
     'sideFrictionConstantRatioOnAxis': (0.0, 0.0, 0.0, 0.0),
     'sinkageResistOnAxis': (0.0, 0.0, 0.0, 0.0),
     'axleIsLeading': (True,
                       True,
                       True,
                       True),
     'axleCanBeRised': (False,
                        True,
                        True,
                        False),
     'wheelRiseHeight': 0.2,
     'wheelRiseSpeed': 1.0,
     'enableRail': True,
     'handbrakeBrakeForce': 10.0,
     'brokenWheelRollingFrictionModifier': 1.0,
     'noSignalBrakeForce': 10.0,
     'afterDeathBrakeForce': 10.0,
     'afterDeathMinSpeedForImpulse': 29.0,
     'afterDeathImpulse': 1.0,
     'jumpingFactor': 30.0,
     'jumpingMinForce': 70.0,
     'slowTurnChocker': 0.5,
     'airPitchReduction': 0.0,
     'wheelToHullRollTransmission': 1.0,
     'steeringSpeedInTurnMultiplier': 1.0,
     'burnout': {'preparationTime': 3.0,
                 'activityTime': 1.0,
                 'engineDamageMin': 100.0,
                 'engineDamageMax': 200.0,
                 'warningMaxHealth': 100.0,
                 'warningMaxHealthCritEngine': 50.0,
                 'power': 1.0,
                 'impulse': 0.0},
     'isWheeledOnSpotRotation': False})


def getDefaultTankVehicleXPhysicsShapeCfg():
    return dict(getDefaultVehicleXPhysicsShapeCfg(), **{'modelShape': getDeafultVehicleModelXPhysicsCfg(),
     'crashedModelShape': getDeafultVehicleModelXPhysicsCfg()})


def getDefaultWheeledVehicleXPhysicsShapeCfg():
    return dict(getDefaultVehicleXPhysicsShapeCfg(), **{'wheelZPenetration': 0.8,
     'wheelXOffset': 0.0,
     'terrBoardAngle': 20.0,
     'terrFrontChamferFraction': 0.75,
     'modelShape': getDefaultWheeledVehicleModelXPhysicsCfg(),
     'crashedModelShape': getDefaultWheeledVehicleModelXPhysicsCfg()})


def getDefaultVehicleXPhysicsShapeCfg():
    return {'useComplexForm': False,
     'isParametricShape': True,
     'terrAftChamferFraction': 0.5,
     'terrFrontChamferFraction': 0.5,
     'terrBoardAngle': 0.0,
     'tankAftChamferFraction': 0.25,
     'tankFrontChamferFraction': 0.25,
     'tankBoardAngle': 0.0,
     'auxClearance': 0.8}


def getDefaultVehicleXPhysicsCfg():
    return {'mode_index': 0,
     'gravity': 9.81,
     'hullCOMShiftY': 0.0,
     'clearance': 0.7,
     'overspeedResistBaseFactor': 0.5,
     'allowedRPMExcessUnbounded': 1.4,
     'absoluteSpeedLimit': 25.0,
     'hasCrashedModel': False,
     'engine': {'engineTorque': ((500.0, 2.0),
                                 (1000.0, 3.0),
                                 (2000.0, 2.5),
                                 (2500.0, 2.0)),
                'smplEngPower': 800.0,
                'smplMinRPM': 150.0,
                'smplEnginePower': 1.0,
                'rotationChoker': 1.0,
                'smplFwMaxSpeed': 15.0,
                'smplBkMaxSpeed': 10.0,
                'powerFactor': 1.0,
                'rotationFactor': 1.0,
                'engineLoses': (0.5, 0.8),
                'engineInertia': 0.02,
                'idleChoker': 0.2,
                'idleRPM': 800.0,
                'startRPM': 1000.0},
     'comFrictionYOffs': 0.7,
     'smplFwMaxSpeed': 10.0,
     'smplBkMaxSpeed': 5.5,
     'pushStop': 0.3,
     'rail': {'railFactorInContact': 0.5},
     'anchor': {'anchorMaxReactionFactor': ANCHOR_MAX_REACTION_FACTOR,
                'anchorConstFraction': ANCHOR_CONST_FRACTION,
                'anchorVelFactor': ANCHOR_VEL_FACTOR},
     'gimlet': {'pushInContact': 2.5},
     'gimletVelScaleMin': 1.0,
     'gimletVelScaleMax': 5.0,
     'pushRotOnSpotFixedPeriod': 0.2,
     'pushRotOnMoveFixedPeriod': 0.2,
     'pushRotOnSpotGrowPeriod': 2.0,
     'pushRotOnMoveGrowPeriod': 2.0,
     'swingCompensator': {'enable': True,
                          'collisionExtend': 0.2,
                          'stiffnesFactor0': 1.0,
                          'stiffnesFactor1': 1.0,
                          'dampingFactor': 1.0,
                          'maxPitchDeviation': 0.1,
                          'maxRollDeviation': 0.1,
                          'restitution': 0.8,
                          'stabilisationCenter': (0.0, 0.0, 0.0)},
     'powerFactor': 1.0,
     'angVelocityFactor': 1.0,
     'angVelocityFactor0': 1.0,
     'gimletGoalWOnSpot': 0.0,
     'gimletGoalWOnMove': 0.0,
     'rotationFactor': 1.0,
     'hullAiming': {'pitch': {'correctionCenterZ': 0.0,
                              'correctionSpeed': 0.3,
                              'pitchMin': -0.2,
                              'pitchMax': 0.2,
                              'correctionStiffness': 30.0,
                              'correctionDamping': 0.25,
                              'correctionScale': 0.5},
                    'yaw': {'gimletForce': 4.0,
                            'stiffness': 8000.0,
                            'damping': 400.0,
                            'preciseRestitution': 0.3,
                            'dampingYawDist': 0.03,
                            'preciseYawDist': 0.03}},
     'hullInertiaFactors': (1.0, 1.0, 1.8),
     'engineLoses': (0.5, 0.8),
     'enableStabilization': True,
     'modes': {'siegeMode': {'mode_index': 1,
                             'engine': {'smplEnginePower': 1.0},
                             'powerFactor': 1.0,
                             'angVelocityFactor': 1.0,
                             'angVelocityFactor0': 1.0,
                             'gimletGoalWOnSpot': 0.0,
                             'gimletGoalWOnMove': 0.0,
                             'rotationFactor': 1.0}}}


def getDefaultTankXPhysicsCfg():
    return dict(getDefaultVehicleXPhysicsCfg(), **{'vehiclePhysicsType': VEHICLE_PHYSICS_TYPE.TANK,
     'shape': getDefaultTankVehicleXPhysicsShapeCfg(),
     'chassis': getDefaultChassisXPhysicsCfg()})


def getDefaultWheeledTechXPhysicsCfg():
    return dict(getDefaultVehicleXPhysicsCfg(), **{'vehiclePhysicsType': VEHICLE_PHYSICS_TYPE.WHEELED_TECH,
     'shape': getDefaultWheeledVehicleXPhysicsShapeCfg(),
     'chassis': getDefaultWheeledChassisXPhysicsCfg()})


def getAppliedGravityMultiplier(physics, typeDesc):
    baseCfg = typeDesc.type.xphysics['detailed']
    baseGravityFactor = baseCfg['gravityFactor']
    gravityMultiplier = physics.gravity / baseGravityFactor / G
    return gravityMultiplier


def init():
    updateCommonConf()


def updateCommonConf():
    BigWorld.wg_setupPhysicsParam('CONTACT_ENERGY_POW', CONTACT_ENERGY_POW)
    BigWorld.wg_setupPhysicsParam('CONTACT_ENERGY_POW2', CONTACT_ENERGY_POW2)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_FUNC_DEF', SLOPE_FRICTION_FUNC_DEF)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_FUNC_VAL', SLOPE_FRICTION_FUNC_VAL)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_MODELS_FUNC_VAL', SLOPE_FRICTION_MODELS_FUNC_VAL)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_TERRAIN', CONTACT_FRICTION_TERRAIN)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_STATICS', CONTACT_FRICTION_STATICS)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_EXTRA', CONTACT_FRICTION_EXTRA)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_DESTRUCTIBLES', CONTACT_FRICTION_DESTRUCTIBLES)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_VEHICLES', CONTACT_FRICTION_VEHICLES)
    BigWorld.wg_setupPhysicsParam('VEHICLE_ON_BODY_DEFAULT_FRICTION', VEHICLE_ON_BODY_DEFAULT_FRICTION)
    BigWorld.wg_setupPhysicsParam('ROLLER_REACTION_COEFF_FOR_STATIC', ROLLER_REACTION_COEFF_FOR_STATIC)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_GAIN_MIN', ROLLER_FRICTION_GAIN_MIN)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_GAIN_MAX', ROLLER_FRICTION_GAIN_MAX)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_ANGLE_MIN', ROLLER_FRICTION_ANGLE_MIN)
    BigWorld.wg_setupPhysicsParam('ROLLER_FRICTION_ANGLE_MAX', ROLLER_FRICTION_ANGLE_MAX)
    BigWorld.wg_setupPhysicsParam('ARENA_BOUNDS_FRICTION_HOR', ARENA_BOUNDS_FRICTION_HOR)
    BigWorld.wg_setupPhysicsParam('ARENA_BOUNDS_FRICTION_VERT', ARENA_BOUNDS_FRICTION_VERT)
    BigWorld.wg_setupPhysicsParam('USE_PSEUDO_CONTACTS', USE_PSEUDO_CONTACTS)
    BigWorld.wg_setupPhysicsParam('CONTACT_PENETRATION', CONTACT_PENETRATION)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_VEHICLE_VEHICLE', WARMSTARTING_VEHICLE_VEHICLE)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_VEHICLE_STATICS', WARMSTARTING_VEHICLE_STATICS)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_THRESHOLD', WARMSTARTING_THRESHOLD)


def updateConf():
    for e in BigWorld.entities.values():
        if e.className == 'Vehicle':
            initVehiclePhysicsServer(e.mover.physics, e.typeDescriptor)

    updateCommonConf()
    for updater in g_confUpdaters:
        updater()


def updatePhysicsCfg(baseCfg, typeDesc, cfg):
    if typeDesc.type.xphysics['detailed'] != baseCfg:
        typeDesc.type.xphysics['detailed'].update(baseCfg)
    engName = typeDesc.engine.name
    engCfg = baseCfg['engines'].get(engName)
    if engCfg:
        cfg.setdefault('engine', {}).update(engCfg)
    chsName = typeDesc.chassis.name
    chsCfg = baseCfg['chassis'].get(chsName)
    if chsCfg:
        cfg.setdefault('chassis', {}).update(chsCfg)
    fakeGearBox = baseCfg.get('fakegearbox')
    if fakeGearBox is not None:
        cfg['fakegearbox'] = fakeGearBox
    swingCompensator = baseCfg.get('swingCompensator')
    if swingCompensator is not None:
        cfg.setdefault('swingCompensator', {}).update(swingCompensator)
    return


def applyVehDescrMiscFactors(typeDescr, mode):
    mode['engine']['smplFwMaxSpeed'] += KMH_TO_MS * typeDescr.miscAttrs['forwardMaxSpeedKMHTerm']
    mode['engine']['smplBkMaxSpeed'] += KMH_TO_MS * typeDescr.miscAttrs['backwardMaxSpeedKMHTerm']
    onStillRotationSpeedFactor = typeDescr.miscAttrs['onStillRotationSpeedFactor']
    onMoveRotationSpeedFactor = typeDescr.miscAttrs['onMoveRotationSpeedFactor']
    if not typeDescr.isWheeledVehicle:
        mode['chassis']['gimletGoalWOnSpot'] *= onStillRotationSpeedFactor
        mode['chassis']['angVelocityFactor0'] *= onStillRotationSpeedFactor
        mode['chassis']['gimletGoalWOnMove'] *= onMoveRotationSpeedFactor
        mode['chassis']['angVelocityFactor'] *= onMoveRotationSpeedFactor
    else:
        factor = mode['chassis']['axleSteeringAngles']
        mode['chassis']['axleSteeringAngles'] = tuple((fi * onMoveRotationSpeedFactor for fi in factor))
        factor = mode['chassis']['axleSteeringSpeed']
        mode['chassis']['axleSteeringSpeed'] = tuple((fi * onMoveRotationSpeedFactor for fi in factor))
        mode['chassis']['slowTurnChocker'] *= onStillRotationSpeedFactor
        mode['chassis']['centerRotationFwdSpeed'] *= typeDescr.miscAttrs['centerRotationFwdSpeedFactor']


def configurePhysics(physics, baseCfg, typeDescr, gravityFactor, updateSiegeModeFromCfg):
    vehiclePhysicsType = typeDescr.type.xphysics['detailed'].get('vehiclePhysicsType', VEHICLE_PHYSICS_TYPE.TANK)
    isTank = vehiclePhysicsType == VEHICLE_PHYSICS_TYPE.TANK
    cfg = getDefaultTankXPhysicsCfg() if isTank else getDefaultWheeledTechXPhysicsCfg()
    if typeDescr.hasSiegeMode:
        defaultVehicleDescr = typeDescr.defaultVehicleDescr
        siegeVehicleDescr = typeDescr.siegeVehicleDescr
    else:
        defaultVehicleDescr = typeDescr
    try:
        cfg['fakegearbox'] = typeDescr.type.xphysics['detailed']['fakegearbox']
    except:
        cfg['fakegearbox'] = _DEFAULT_FAKE_GEARBOX_SETTINGS

    if baseCfg:
        updatePhysicsCfg(baseCfg, defaultVehicleDescr, cfg)
        if typeDescr.hasSiegeMode:
            if updateSiegeModeFromCfg and 'siegeMode' in baseCfg.get('modes', {}):
                siegeBaseCfg = baseCfg['modes']['siegeMode']
            else:
                siegeBaseCfg = siegeVehicleDescr.type.xphysics['detailed']
            updatePhysicsCfg(siegeBaseCfg, siegeVehicleDescr, cfg['modes']['siegeMode'])
    cfg = __buildConfigurations(cfg)
    for name, mode in cfg['modes'].iteritems():
        applyVehDescrMiscFactors(typeDescr, mode)
        configurePhysicsMode(mode, typeDescr, gravityFactor)

    if not physics.configure(cfg):
        LOG_ERROR('configureXPhysics: configure failed')
    physics.centerOfMass = Math.Vector3((0.0, cfg['modes']['normal']['clearance'] + cfg['modes']['normal']['bodyHeight'] * 0.5 + cfg['modes']['normal']['hullCOMShiftY'], physics.hullCOMZ))
    physics.isFrozen = False
    physics.movementSignals = 0
    physics.freezeAccelEpsilon = FREEZE_ACCEL_EPSILON
    physics.freezeAngAccelEpsilon = FREEZE_ANG_ACCEL_EPSILON
    physics.freezeVelEpsilon = FREEZE_VEL_EPSILON
    physics.freezeAngVelEpsilon = FREEZE_ANG_VEL_EPSILON
    physics.simulationYBound = _SIMULATION_Y_BOUND
    return cfg


def __computeModelShape(cfg, modelShapeCfg, typeDesc, boundingBoxes):
    bmin, bmax, _ = boundingBoxes['chassis']
    sizeX = bmax[0] - bmin[0]
    bminHull, bmaxHull, _ = boundingBoxes['hull']
    if typeDesc.type.useHullZSize:
        sizeZ = bmaxHull[2] - bminHull[2]
    else:
        sizeZ = bmax[2] - bmin[2]
    if typeDesc.type.useHullZOffset:
        offsZ = (bmaxHull[2] + bminHull[2]) * 0.5
    else:
        offsZ = (bmin[2] + bmax[2]) * 0.5
    modelShapeCfg['hullSize'] = Math.Vector3((sizeX, cfg['bodyHeight'], sizeZ))
    modelShapeCfg['hullBoxOffsetZ'] = offsZ
    if typeDesc.isWheeledVehicle:
        wheelBbMin, wheelBbMax, _ = typeDesc.chassis.wheels.wheels[0].hitTester.bbox
        wheelSize = wheelBbMax - wheelBbMin
        modelShapeCfg['wheelSize'] = wheelSize
    turretMin, turretMax, _ = boundingBoxes['turret']
    _, gunMax, _ = boundingBoxes['gun']
    hullPos = typeDesc.chassis.hullPosition
    turretPos = typeDesc.hull.turretPositions[0]
    topPos = hullPos + turretPos
    turretTopOffset = max(turretMax[1], typeDesc.turret.gunPosition[1] + gunMax[1])
    topPos.y += turretTopOffset - cfg['clearance'] - cfg['bodyHeight']
    topPos.y = max(0.1, topPos.y * 0.8)
    topPos.y += cfg['bodyHeight'] * 0.5
    modelShapeCfg['turretTopPos'] = topPos
    modelShapeCfg['turretTopWidth'] = max(sizeX * 0.25, (turretMax[0] - turretMin[0]) * 0.7)


def configureModelShapePhysics(cfg, typeDesc):
    chassisDescr = typeDesc.chassis
    normalBBoxes = {'chassis': chassisDescr.bboxManager.normalBBox}
    crashedBBoxes = {'chassis': chassisDescr.bboxManager.crashedBBox}
    isCrashedModelValid = crashedBBoxes['chassis'] is not None
    htManagers = [('hull', typeDesc.hull.hitTesterManager), ('turret', typeDesc.turret.hitTesterManager), ('gun', typeDesc.gun.hitTesterManager)]
    if typeDesc.isWheeledVehicle:
        htManagers.append(('wheel', chassisDescr.wheels.wheels[0].hitTesterManager))
    for name, htManager in htManagers:
        normalBBoxes[name] = htManager.modelHitTester.bbox
        if htManager.crashedModelHitTester:
            crashedBBoxes[name] = htManager.crashedModelHitTester.bbox
        isCrashedModelValid = False

    cfg['hasCrashedModel'] = isCrashedModelValid
    __computeModelShape(cfg, cfg['shape']['modelShape'], typeDesc, normalBBoxes)
    if isCrashedModelValid:
        __computeModelShape(cfg, cfg['shape']['crashedModelShape'], typeDesc, crashedBBoxes)
    return


def updatePhysics(physics, typeDesc, isSoftUpdate=False, gravityMultiplier=1.0):
    baseCfg = typeDesc.type.xphysics['detailed']
    gravityFactor = baseCfg['gravityFactor'] * gravityMultiplier
    updateSiegeModeFromCfg = False
    vehiclePhysicsType = typeDesc.type.xphysics['detailed'].get('vehiclePhysicsType', VEHICLE_PHYSICS_TYPE.TANK)
    isTank = vehiclePhysicsType == VEHICLE_PHYSICS_TYPE.TANK
    cfg = copy.deepcopy(getDefaultTankXPhysicsCfg() if isTank else getDefaultWheeledTechXPhysicsCfg())
    if typeDesc.hasSiegeMode:
        defaultVehicleDescr = typeDesc.defaultVehicleDescr
        siegeVehicleDescr = typeDesc.siegeVehicleDescr
    else:
        defaultVehicleDescr = typeDesc
    try:
        cfg['fakegearbox'] = typeDesc.type.xphysics['detailed']['fakegearbox']
    except:
        cfg['fakegearbox'] = _DEFAULT_FAKE_GEARBOX_SETTINGS

    updatePhysicsCfg(baseCfg, defaultVehicleDescr, cfg)
    if typeDesc.hasSiegeMode:
        if updateSiegeModeFromCfg and 'modes' in baseCfg and 'siegeMode' in baseCfg['modes']:
            siegeBaseCfg = baseCfg['modes']['siegeMode']
        else:
            siegeBaseCfg = siegeVehicleDescr.type.xphysics['detailed']
        updatePhysicsCfg(siegeBaseCfg, siegeVehicleDescr, cfg['modes']['siegeMode'])
    cfg = __buildConfigurations(cfg)
    for name, mode in cfg['modes'].iteritems():
        if isSoftUpdate:
            applyVehDescrMiscFactors(typeDesc, mode)
        configurePhysicsMode(mode, typeDesc, gravityFactor)

    if not isSoftUpdate:
        oldMatrix = Math.Matrix(physics.matrix)
        inversedMatrix = Math.Matrix(oldMatrix)
        inversedMatrix.invert()
        oldCoM = physics.centerOfMass
        newCoM = Math.Vector3((0.0, cfg['modes']['normal']['clearance'] + cfg['modes']['normal']['bodyHeight'] * 0.5 + cfg['modes']['normal']['hullCOMShiftY'], physics.hullCOMZ))
        compression = inversedMatrix.applyPoint(physics.currentCenterOfMass).y / oldCoM.y
        dy = (newCoM.y - oldCoM.y) * compression
        physics.centerOfMass = newCoM
        newMatrix = Math.Matrix()
        newMatrix.setTranslate(oldMatrix.applyToAxis(1) * dy)
        newMatrix.preMultiply(oldMatrix)
        physics.matrix = newMatrix
    physics.isFrozen = False
    physics.updateSettings(cfg)
    return cfg


def configurePhysicsMode(cfg, typeDesc, gravityFactor):
    cfg['angVelocityFactor'] = cfg['chassis']['angVelocityFactor']
    cfg['angVelocityFactor0'] = cfg['chassis']['angVelocityFactor0']
    cfg['axleCount'] = cfg['chassis']['axleCount']
    if cfg['vehiclePhysicsType'] == VEHICLE_PHYSICS_TYPE.WHEELED_TECH:
        for key in ('axleSteeringLockAngles', 'axleSteeringAngles', 'axleSteeringSpeed', 'fwdFrictionOnAxisModifiers', 'sideFrictionOnAxisModifiers', 'sideFrictionConstantRatioOnAxis', 'sinkageResistOnAxis', 'axleIsLeading', 'axleCanBeRised', 'wheelRiseHeight', 'wheelRiseSpeed', 'enableRail', 'handbrakeBrakeForce', 'brokenWheelRollingFrictionModifier', 'noSignalBrakeForce', 'afterDeathBrakeForce', 'afterDeathMinSpeedForImpulse', 'afterDeathImpulse', 'jumpingFactor', 'jumpingMinForce', 'slowTurnChocker', 'airPitchReduction', 'wheelToHullRollTransmission', 'steeringSpeedInTurnMultiplier', 'isWheeledOnSpotRotation'):
            cfg[key] = cfg['chassis'][key]

    cfg['gimletGoalWOnSpot'] = cfg['chassis']['gimletGoalWOnSpot']
    cfg['gimletGoalWOnMove'] = cfg['chassis']['gimletGoalWOnMove']
    cfg['isRotationAroundCenter'] = cfg['chassis']['isRotationAroundCenter']
    cfg['centerRotationFwdSpeed'] = cfg['chassis']['centerRotationFwdSpeed']
    cfg['movementRevertSpeed'] = cfg['chassis']['movementRevertSpeed']
    cfg['fwLagRatio'] = cfg['chassis']['fwLagRatio']
    cfg['bkLagRatio'] = cfg['chassis']['bkLagRatio']
    cfg['rotFritionFactor'] = cfg['chassis']['rotFritionFactor']
    cfg['comFrictionYOffs'] = cfg['chassis']['comFrictionYOffs']
    cfg['comSideFriction'] = cfg['chassis']['comSideFriction']
    cfg['pushStop'] = cfg['chassis']['pushStop']
    cfg['gimletPushOnSpotInit'] = cfg['chassis']['gimletPushOnSpotInit']
    cfg['gimletPushOnSpotFinal'] = cfg['chassis']['gimletPushOnSpotFinal']
    cfg['gimletPushOnMoveInit'] = cfg['chassis']['gimletPushOnMoveInit']
    cfg['gimletPushOnMoveFinal'] = cfg['chassis']['gimletPushOnMoveFinal']
    cfg['gimletVelScaleMin'] = cfg['chassis']['gimletVelScaleMin']
    cfg['gimletVelScaleMax'] = cfg['chassis']['gimletVelScaleMax']
    cfg['pushRotOnSpotFixedPeriod'] = cfg['chassis']['pushRotOnSpotFixedPeriod']
    cfg['pushRotOnMoveFixedPeriod'] = cfg['chassis']['pushRotOnMoveFixedPeriod']
    cfg['pushRotOnSpotGrowPeriod'] = cfg['chassis']['pushRotOnSpotGrowPeriod']
    cfg['pushRotOnMoveGrowPeriod'] = cfg['chassis']['pushRotOnMoveGrowPeriod']
    cfg['smplFwMaxSpeed'] = cfg['engine']['smplFwMaxSpeed']
    cfg['smplBkMaxSpeed'] = cfg['engine']['smplBkMaxSpeed']
    cfg['powerFactor'] = cfg['engine']['powerFactor']
    cfg['rotationFactor'] = cfg['engine']['rotationFactor']
    cfg['bodyHeight'] = cfg['chassis']['bodyHeight']
    cfg['hullCOMShiftY'] = cfg['chassis']['hullCOMShiftY']
    cfg['hullInertiaFactors'] = cfg['chassis']['hullInertiaFactors']
    cfg['clearance'] = cfg['chassis']['clearance']
    cfg['fullMass'] = typeDesc.physics['weight'] * WEIGHT_SCALE
    selfDrivenMaxSpeed = max(cfg['smplFwMaxSpeed'], cfg['smplBkMaxSpeed'])
    speedLimit = min(cfg['absoluteSpeedLimit'], selfDrivenMaxSpeed * cfg['allowedRPMExcessUnbounded'])
    cfg['allowedRPMExcess'] = max(1.0, speedLimit / selfDrivenMaxSpeed)
    cfg['overspeedResistFactor'] = cfg['overspeedResistBaseFactor'] / selfDrivenMaxSpeed
    cfg['useComplexForm'] = typeDesc.type.name == 'sweden:S11_Strv_103B'
    configureModelShapePhysics(cfg, typeDesc)
    if typeDesc.isWheeledVehicle:
        cfg['shape']['wheelXOffset'] = max((abs(wheel.position.x) for wheel in typeDesc.chassis.wheels.wheels))
    cfg['shape']['useComplexForm'] = typeDesc.type.name == 'sweden:S11_Strv_103B'
    cfg['gravity'] = cfg['gravity'] * gravityFactor
    cfg['engine']['engineTorque'] = tuple(((arg, val * gravityFactor) for arg, val in cfg['engine']['engineTorque']))
    cfg['pushHB'] = cfg.get('gimletPushOnSpotFinal', 0.0)
    cfg['engine']['smplEngJoinRatio'] = ENGINE_RADIUS / cfg['chassis']['wheelRadius']
    applyRotationAndPowerFactors(cfg)
    cfg['siegeModeAvailable'] = typeDesc.hasSiegeMode
    cfg['isWheeledVehicle'] = typeDesc.isWheeledVehicle
    hullAimingParams = typeDesc.type.hullAimingParams
    hullAimingParamsPitch = hullAimingParams['pitch']
    hullAimingPitchCfg = cfg['hullAiming']['pitch']
    hullAimingPitchCfg['correctionCenterZ'] = hullAimingParamsPitch['wheelCorrectionCenterZ']
    hullAimingPitchCfg['correctionSpeed'] = hullAimingParamsPitch['wheelsCorrectionSpeed']
    hullAimingPitchCfg['pitchMin'] = -hullAimingParamsPitch['wheelsCorrectionAngles']['pitchMax']
    hullAimingPitchCfg['pitchMax'] = -hullAimingParamsPitch['wheelsCorrectionAngles']['pitchMin']
    cfg['enableStabilization'] = cfg['swingCompensator']['enable']
    cfg['gimlet']['wPushedRot'] = cfg['wPushedRot']
    cfg['gimlet']['wPushedDiag'] = cfg['wPushedDiag']
    cfg['gimlet']['wPushedHB'] = cfg['wPushedHB']
    cfg['gimlet']['pushHB'] = cfg['pushHB']
    cfg['gimlet']['pushStop'] = cfg['pushStop']
    cfg['gimlet']['gimletPushOnSpotInit'] = cfg['gimletPushOnSpotInit']
    cfg['gimlet']['gimletPushOnSpotFinal'] = cfg['gimletPushOnSpotFinal']
    cfg['gimlet']['gimletPushOnMoveInit'] = cfg['gimletPushOnMoveInit']
    cfg['gimlet']['gimletPushOnMoveFinal'] = cfg['gimletPushOnMoveFinal']
    cfg['gimlet']['gimletVelScaleMin'] = cfg['gimletVelScaleMin']
    cfg['gimlet']['gimletVelScaleMax'] = cfg['gimletVelScaleMax']
    cfg['gimlet']['pushRotOnSpotFixedPeriod'] = cfg['pushRotOnSpotFixedPeriod']
    cfg['gimlet']['pushRotOnMoveFixedPeriod'] = cfg['pushRotOnMoveFixedPeriod']
    cfg['gimlet']['pushRotOnSpotGrowPeriod'] = cfg['pushRotOnSpotGrowPeriod']
    cfg['gimlet']['pushRotOnMoveGrowPeriod'] = cfg['pushRotOnMoveGrowPeriod']
    cfg['engine']['rotationByLockChoker'] = cfg['chassis']['rotationByLockChoker']
    del cfg['chassis']['rotationByLockChoker']
    cfg['engine']['engVelMax'] = cfg['smplFwMaxSpeed'] / cfg['chassis']['wheelRadius'] / cfg['engine']['smplEngJoinRatio']
    cfg['engine']['engVelBkMax'] = cfg['smplBkMaxSpeed'] / cfg['chassis']['wheelRadius'] / cfg['engine']['smplEngJoinRatio']
    cfg['engine']['engVelRot'] = cfg['smplRotSpeed'] / cfg['chassis']['wheelRadius'] / cfg['engine']['smplEngJoinRatio']
    cfg['chassis']['chassisMass'] = cfg['fullMass'] * cfg['chassis']['chassisMassFraction']
    cfg['chassis']['hullAiming'] = cfg['hullAiming']


def applyRotationAndPowerFactors(cfg):
    try:
        cfg['engine']['smplEnginePower'] = cfg['engine']['smplEnginePower'] * cfg['powerFactor']
        cfg['angVelocityFactor'] = cfg['angVelocityFactor'] * cfg['rotationFactor']
        arm = cfg['shape']['modelShape']['hullSize'][0]
        cfg['smplRotSpeed'] = arm * cfg['angVelocityFactor0'] * cfg['rotationFactor']
        cfg['gimletGoalWOnSpot'] = cfg['gimletGoalWOnSpot'] * cfg['rotationFactor']
        cfg['gimletGoalWOnMove'] = cfg['gimletGoalWOnMove'] * cfg['rotationFactor']
        cfg['wPushedRot'] = cfg['gimletGoalWOnSpot']
        cfg['wPushedHB'] = cfg['wPushedRot'] * 0.98
        cfg['wPushedDiag'] = cfg['gimletGoalWOnMove']
    except:
        LOG_CURRENT_EXCEPTION()


def initVehiclePhysicsServer(physics, typeDesc):
    baseCfg = typeDesc.type.xphysics['detailed']
    gravityFactor = baseCfg['gravityFactor']
    configurePhysics(physics, baseCfg, typeDesc, gravityFactor, False)


def initVehiclePhysicsForced(physics, typeDesc, forcedCfg):
    baseCfg = forcedCfg
    gravityFactor = forcedCfg['gravityFactor']
    configurePhysics(physics, baseCfg, typeDesc, gravityFactor, True)


def initVehiclePhysicsEditor(physics, typeDesc):
    initVehiclePhysicsServer(physics, typeDesc)
    initVehiclePhysicsClient(physics, typeDesc)


def initVehiclePhysicsClient(physics, typeDesc):
    physDescr = typeDesc.physics
    hullMin, hullMax, _ = typeDesc.hull.hitTester.bbox
    hullCenter = (hullMin + hullMax) * 0.5
    hullY = hullCenter.y + typeDesc.chassis.hullPosition.y
    hullHeight = hullMax.y - hullMin.y
    bmin, bmax, _ = typeDesc.chassis.hitTester.bbox
    chassisCenter = (bmin + bmax) * 0.5
    blen = bmax[2] - bmin[2]
    width = bmax[0] - bmin[0]
    height = bmax[1] - bmin[1]
    if blen == 0.0 and width == 0.0 and height == 0.0:
        LOG_ERROR('Invalid bounding box for', typeDesc.name)
        blen = width = height = 1.0
    srcEnginePower = physDescr['enginePower']
    srcMass = physDescr['weight']
    fullMass = physDescr['weight'] * WEIGHT_SCALE
    clearance = (typeDesc.chassis.hullPosition.y + hullMin.y) * CLEARANCE
    clearance = _clamp(CLEARANCE_MIN * height, clearance, CLEARANCE_MAX * height)
    suspCompression = _computeSuspCompression(fullMass)
    carringSpringLength = clearance / suspCompression
    cmShift = _computeCenterOfMassShift(srcMass, srcEnginePower)
    if not IS_EDITOR:
        physics.centerOfMass = Math.Vector3((0.0, hullY + cmShift * hullHeight, 0.0))
    chassisMaxY = bmax[1]
    hullPosY = typeDesc.chassis.hullPosition[1]
    hullMaxY = hullPosY + hullMax[1]
    turretPosY = typeDesc.hull.turretPositions[0][1]
    turretMaxY = hullPosY + turretPosY + typeDesc.turret.hitTester.bbox[1][1]
    commonBoxMaxY = max(chassisMaxY, hullMaxY, turretMaxY)
    gunPosY = hullPosY + turretPosY + typeDesc.turret.gunPosition[1]
    hullUpperBound = typeDesc.chassis.hullPosition.y + hullMax.y
    boxHeight = min(commonBoxMaxY, gunPosY, hullUpperBound * BODY_HEIGHT) - clearance
    boxHeight = max(chassisMaxY * 0.7, boxHeight, VEHICLE_ON_OBSTACLE_COLLISION_BOX_MIN_HEIGHT)
    globalBoxY = clearance + boxHeight / 2
    boxCenter = Math.Vector3(chassisCenter)
    boxCenter[1] = globalBoxY - physics.centerOfMass.y
    physics.removeAllDamperSprings()
    if clearance != 0.0:
        clearanceRatio = width / clearance
    else:
        LOG_ERROR('Clearance is null')
        clearanceRatio = CLEARANCE_RATIO_LONG
    if width < WIDTH_VERY_LONG and (width < WIDTH_LONG or clearanceRatio < CLEARANCE_RATIO_LONG):
        carrierSpringPairs = NUM_SPRINGS_NORMAL
    else:
        carrierSpringPairs = NUM_SPRINGS_LONG
    length = carringSpringLength
    hullAimingLength = carringSpringLength
    trackLen = _computeTrackLength(clearance, blen)
    indent = boxHeight / 2
    hardRatio = _computeHardRatio(clearance, blen)
    if (IS_CLIENT or IS_EDITOR) and typeDesc.isPitchHullAimingAvailable:
        springExtendMultiplier = 2.0
        hardRatio = 0
        hullAngleMin = typeDesc.type.hullAimingParams['pitch']['wheelsCorrectionAngles']['pitchMin']
        hullAngleMax = typeDesc.type.hullAimingParams['pitch']['wheelsCorrectionAngles']['pitchMax']
        backSpringLength = blen * math.sin(abs(hullAngleMax)) * springExtendMultiplier
        frontSpringLength = blen * math.sin(abs(hullAngleMin)) * springExtendMultiplier
        hullAimingLength = max(backSpringLength, frontSpringLength)
    if (IS_CLIENT or IS_EDITOR) and typeDesc.hasSiegeMode and typeDesc.isPitchHullAimingAvailable:
        springsLengthList = tuple((length for _ in xrange(0, carrierSpringPairs)))
        hullAimingSpringsLengthList = tuple((hullAimingLength for _ in xrange(0, carrierSpringPairs)))
        for descriptor in [typeDesc.defaultVehicleDescr, typeDesc.siegeVehicleDescr]:
            if descriptor.chassis.suspensionSpringsLength is not None:
                break
            hullAimingEnabled = descriptor.type.hullAimingParams['pitch']['isEnabled']
            descriptor.chassis.suspensionSpringsLength = {'left': hullAimingSpringsLengthList if hullAimingEnabled else springsLengthList,
             'right': hullAimingSpringsLengthList if hullAimingEnabled else springsLengthList}

    stepZ = trackLen / (carrierSpringPairs - 1)
    begZ = -trackLen * 0.5
    leftX = -width * 0.45
    rightX = width * 0.45
    y = -boxHeight / 2 + boxCenter.y
    for i in xrange(0, carrierSpringPairs):
        mountPoint = Math.Vector3((leftX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         length,
         indent,
         True,
         hardRatio))
        mountPoint = Math.Vector3((rightX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         length,
         indent,
         False,
         hardRatio))

    if _LOG_INIT_PARAMS:
        LOG_DEBUG('initVehiclePhysics: clearance %f' % (clearance / height))
        LOG_DEBUG('initVehiclePhysics: clearanceRatio %f' % (clearance / blen))
        LOG_DEBUG('initVehiclePhysics: cmShift %f' % cmShift)
        LOG_DEBUG('initVehiclePhysics: suspCompression: %f' % suspCompression)
    return


def computeBarrelLocalPoint(vehDescr, turretYaw, gunPitch):
    maxGunZ = vehDescr.gun.hitTester.bbox[1][2]
    m = Math.Matrix()
    m.setRotateX(gunPitch)
    pt = m.applyVector((0.0, 0.0, maxGunZ)) + vehDescr.activeGunShotPosition
    m.setRotateY(turretYaw)
    pt = m.applyVector(pt)
    pt += vehDescr.hull.turretPositions[vehDescr.activeTurretPosition]
    pt += vehDescr.chassis.hullPosition
    return pt


def linearInterpolate(arg, argMin, argMax, valMin, valMax):
    argRange = argMax - argMin
    narg = (arg - argMin) / argRange
    narg = _clamp(0.0, narg, 1.0)
    valRange = valMax - valMin
    val = narg * valRange + valMin
    return val


def _computeCenterOfMassShift(mass, enginePower):
    dr = enginePower / mass
    cmy = _powerCurve(dr, DYN_RATIO_MIN, DYN_RATIO_MID, DYN_RATIO_MAX, CMY_MIN, CMY_MID, CMY_MAX)
    return cmy


def _computeSuspCompression(mass):
    suspCompression = linearInterpolate(mass, SUSP_COMPRESSION_MIN_MASS, SUSP_COMPRESSION_MAX_MASS, SUSP_COMPRESSION_MIN, SUSP_COMPRESSION_MAX)
    return suspCompression


def _computeTrackLength(clearance, length):
    r = clearance / length
    lenRatio = linearInterpolate(r, CLEARANCE_TO_LENGTH_MIN, CLEARANCE_TO_LENGTH_MAX, TRACK_LENGTH_MAX, TRACK_LENGTH_MIN)
    return lenRatio * length


def _computeHardRatio(clearance, length):
    r = clearance / length
    return linearInterpolate(r, CLEARANCE_TO_LENGTH_MIN, CLEARANCE_TO_LENGTH_MAX, HARD_RATIO_MIN, HARD_RATIO_MAX)


def _powerCurve(arg, argMin, argMid, argMax, valMin, valMid, valMax):
    argRange = argMax - argMin
    narg = (arg - argMin) / argRange
    narg = _clamp(0.0, narg, 1.0)
    nargMid = (argMid - argMin) / argRange
    valRange = valMax - valMin
    nvalMid = (valMid - valMin) / valRange
    pow = math.log(nvalMid, nargMid)
    nval = math.pow(narg, pow)
    val = nval * valRange + valMin
    return val


def _clamp(minBound, arg, maxBound):
    return max(minBound, min(maxBound, arg))


TRACK_SCROLL_LIMITS = (-15.0, 30.0)

def encodeTrackScrolling(leftScroll, rightScroll):
    return encodeRestrictedValueToUint(leftScroll, 8, *TRACK_SCROLL_LIMITS) | encodeRestrictedValueToUint(rightScroll, 8, *TRACK_SCROLL_LIMITS) << 8


def decodeTrackScrolling(code):
    return (decodeRestrictedValueFromUint((code & 255), 8, *TRACK_SCROLL_LIMITS), decodeRestrictedValueFromUint((code >> 8), 8, *TRACK_SCROLL_LIMITS))


def __deepUpdate(orig_dict, new_dict):
    if orig_dict is new_dict:
        return
    for key, val in new_dict.iteritems():
        if isinstance(val, collections.Mapping):
            tmp = __deepUpdate(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        orig_dict[key] = new_dict[key]

    return orig_dict


def __buildConfigurations(configuration):
    configurations = {'normal': configuration}
    modes = configuration.get('modes')
    if modes is not None:
        del configurations['normal']['modes']
        for key, value in modes.iteritems():
            basic = copy.deepcopy(configuration)
            modified = __deepUpdate(basic, value)
            configurations[key] = modified

    return {'vehiclePhysicsType': configuration['vehiclePhysicsType'],
     'modes': configurations}


def getShootTimeCorrection(roundTripTime):
    return min(0.3, roundTripTime + SERVER_TICK_LENGTH * 0.5)


_DEFAULT_FAKE_GEARBOX_SETTINGS = {'fwdgears': {'switchSpeed': (2, 5, 15),
              'switchHysteresis': (1, 2, 3),
              'lowRpm': (0.2, 0.2, 0.2),
              'highRpm': (0.9, 0.9, 0.9)},
 'bkwdgears': {'switchSpeed': (2, 5, 15),
               'switchHysteresis': (1, 2, 3),
               'lowRpm': (0.2, 0.2, 0.2),
               'highRpm': (0.9, 0.9, 0.9)}}

def setTrackBitToBitMask(bitMask, trackPairIdx, isLeft):
    idx = trackPairIdx * 2 + (not isLeft)
    return bitMask | 1 << idx
