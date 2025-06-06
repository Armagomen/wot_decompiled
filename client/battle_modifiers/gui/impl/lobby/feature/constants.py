# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/lobby/feature/constants.py
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext.constants_ext import UseType, PhysicalType, GameplayImpact
from battle_modifiers.gui.impl.gen.view_models.views.lobby.feature.modifier_model import ModType, ModPhysType, ModUseType, ModGameplayImpact
MOD_TYPE_MAP = {BattleParams.FAKE_MODIFIER: ModType.FAKE_MODIFIER,
 BattleParams.VEHICLE_HEALTH: ModType.VEHICLE_HEALTH,
 BattleParams.GRAVITY_FACTOR: ModType.GRAVITY_FACTOR,
 BattleParams.DISP_FACTOR_CHASSIS_MOVEMENT: ModType.DISP_FACTOR_CHASSIS_MOVEMENT,
 BattleParams.DISP_FACTOR_CHASSIS_ROTATION: ModType.DISP_FACTOR_CHASSIS_ROTATION,
 BattleParams.TURRET_ROTATION_SPEED: ModType.TURRET_ROTATION_SPEED,
 BattleParams.GUN_ROTATION_SPEED: ModType.GUN_ROTATION_SPEED,
 BattleParams.RELOAD_TIME: ModType.RELOAD_TIME,
 BattleParams.TWIN_GUN_RELOAD_TIME: ModType.TWIN_GUN_RELOAD_TIME,
 BattleParams.CLIP_INTERVAL: ModType.CLIP_INTERVAL,
 BattleParams.BURST_INTERVAL: ModType.BURST_INTERVAL,
 BattleParams.AUTORELOAD_TIME: ModType.AUTORELOAD_TIME,
 BattleParams.AIMING_TIME: ModType.AIMING_TIME,
 BattleParams.SHOT_DISPERSION_RADIUS: ModType.SHOT_DISPERSION_RADIUS,
 BattleParams.DISP_FACTOR_TURRET_ROTATION: ModType.DISP_FACTOR_TURRET_ROTATION,
 BattleParams.DISP_FACTOR_AFTER_SHOT: ModType.DISP_FACTOR_AFTER_SHOT,
 BattleParams.DISP_FACTOR_WHILE_GUN_DAMAGED: ModType.DISP_FACTOR_WHILE_GUN_DAMAGED,
 BattleParams.SHELL_GRAVITY: ModType.SHELL_GRAVITY,
 BattleParams.SHELL_SPEED: ModType.SHELL_SPEED,
 BattleParams.DAMAGE_RANDOMIZATION: ModType.DAMAGE_RANDOMIZATION,
 BattleParams.PIERCING_POWER_RANDOMIZATION: ModType.PIERCING_POWER_RANDOMIZATION,
 BattleParams.NORMALIZATION_ANGLE: ModType.NORMALIZATION_ANGLE,
 BattleParams.RICOCHET_ANGLE: ModType.RICOCHET_ANGLE,
 BattleParams.ENGINE_POWER: ModType.ENGINE_POWER,
 BattleParams.ENGINE_FIRE_FACTOR: ModType.ENGINE_FIRE_FACTOR,
 BattleParams.FW_MAX_SPEED: ModType.FW_MAX_SPEED,
 BattleParams.BK_MAX_SPEED: ModType.BK_MAX_SPEED,
 BattleParams.ROTATION_SPEED_ON_STILL: ModType.ROTATION_SPEED_ON_STILL,
 BattleParams.ROTATION_SPEED_ON_MOVE: ModType.ROTATION_SPEED_ON_MOVE,
 BattleParams.INVISIBILITY_ON_STILL: ModType.INVISIBILITY_ON_STILL,
 BattleParams.INVISIBILITY_ON_MOVE: ModType.INVISIBILITY_ON_MOVE,
 BattleParams.VISION_RADIUS: ModType.VISION_RADIUS,
 BattleParams.RADIO_DISTANCE: ModType.RADIO_DISTANCE,
 BattleParams.BATTLE_LENGTH: ModType.BATTLE_LENGTH,
 BattleParams.VEHICLE_RAMMING_DAMAGE: ModType.VEHICLE_RAMMING_DAMAGE,
 BattleParams.VEHICLE_PRESSURE_DAMAGE: ModType.VEHICLE_PRESSURE_DAMAGE,
 BattleParams.TURRET_RAMMING_DAMAGE: ModType.TURRET_RAMMING_DAMAGE,
 BattleParams.TURRET_PRESSURE_DAMAGE: ModType.TURRET_PRESSURE_DAMAGE,
 BattleParams.ENV_HULL_DAMAGE: ModType.ENV_HULL_DAMAGE,
 BattleParams.ENV_CHASSIS_DAMAGE: ModType.ENV_CHASSIS_DAMAGE,
 BattleParams.ENV_TANKMAN_DAMAGE_CHANCE: ModType.ENV_TANKMAN_DAMAGE_CHANCE,
 BattleParams.ENV_MODULE_DAMAGE_CHANCE: ModType.ENV_MODULE_DAMAGE_CHANCE,
 BattleParams.REPAIR_SPEED: ModType.REPAIR_SPEED,
 BattleParams.VISION_MIN_RADIUS: ModType.VISION_MIN_RADIUS,
 BattleParams.VISION_MAX_RADIUS: ModType.VISION_MAX_RADIUS,
 BattleParams.VISION_TIME: ModType.VISION_TIME,
 BattleParams.EQUIPMENT_COOLDOWN: ModType.EQUIPMENT_COOLDOWN,
 BattleParams.INVISIBILITY_FACTOR_AT_SHOT: ModType.INVISIBILITY_FACTOR_AT_SHOT,
 BattleParams.VEHICLE_AOI_RADIUS: ModType.VEHICLE_AOI_RADIUS,
 BattleParams.DEVICE_DAMAGE_FIRST: ModType.DEVICE_DAMAGE_FIRST}
PHYS_TYPE_MAP = {PhysicalType.UNDEFINED: ModPhysType.UNDEFINED,
 PhysicalType.SECONDS: ModPhysType.SECONDS,
 PhysicalType.MINUTES: ModPhysType.MINUTES,
 PhysicalType.MILLIMETERS: ModPhysType.MILLIMETERS,
 PhysicalType.METERS: ModPhysType.METERS,
 PhysicalType.METERS_PER_SECOND: ModPhysType.METERS_PER_SECOND,
 PhysicalType.KILOMETERS_PER_HOUR: ModPhysType.KILOMETERS_PER_HOUR,
 PhysicalType.METER_PER_SECOND_SQUARED: ModPhysType.METER_PER_SECOND_SQUARED,
 PhysicalType.DEGREES: ModPhysType.DEGREES,
 PhysicalType.RADIANS: ModPhysType.RADIANS,
 PhysicalType.DEGREES_PER_SECOND: ModPhysType.DEGREES_PER_SECOND,
 PhysicalType.RADIANS_PER_SECOND: ModPhysType.RADIANS_PER_SECOND,
 PhysicalType.HIT_POINTS: ModPhysType.HIT_POINTS,
 PhysicalType.HORSEPOWER: ModPhysType.HORSEPOWER,
 PhysicalType.PROBABILITY: ModPhysType.PROBABILITY,
 PhysicalType.DEVIATION: ModPhysType.DEVIATION,
 PhysicalType.LOGIC: ModPhysType.LOGIC}
USE_TYPE_MAP = {UseType.UNDEFINED: ModUseType.UNDEFINED,
 UseType.VAL: ModUseType.VAL,
 UseType.MUL: ModUseType.MUL,
 UseType.ADD: ModUseType.ADD}
GAMEPLAY_IMPACT_MAP = {GameplayImpact.UNDEFINED: ModGameplayImpact.UNDEFINED,
 GameplayImpact.POSITIVE: ModGameplayImpact.POSITIVE,
 GameplayImpact.NEGATIVE: ModGameplayImpact.NEGATIVE}
