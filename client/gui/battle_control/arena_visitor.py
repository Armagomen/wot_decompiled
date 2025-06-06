# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_visitor.py
import functools
import weakref
import BigWorld
import win_points
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from battle_modifiers_common import BattleParams, BattleModifiers
from constants import ARENA_GUI_TYPE as _GUI_TYPE, ARENA_GUI_TYPE_LABEL as _GUI_TYPE_LABEL, ARENA_BONUS_TYPE as _BONUS_TYPE, ARENA_PERIOD as _PERIOD, QUEUE_TYPE, TEAMS_IN_ARENA, VISIBILITY
from gui import GUI_SETTINGS
from gui.shared.utils.functions import getArenaImage
from skeletons.gui.battle_session import IClientArenaVisitor

def _getClientArena(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        arena = avatar.arena
    except AttributeError:
        arena = None

    return arena


def createByAvatar(avatar=None):
    return _ClientArenaVisitor.createByArena(arena=_getClientArena(avatar=avatar))


def createByArena(arena=None):
    return _ClientArenaVisitor.createByArena(arena=arena)


def createSkeleton(arenaType=None, guiType=_GUI_TYPE.UNKNOWN, bonusType=_BONUS_TYPE.UNKNOWN):
    return _ClientArenaVisitor.createSkeleton(arenaType=arenaType, guiType=guiType, bonusType=bonusType)


class catch_attribute_exception(object):

    def __init__(self, default=None):
        super(catch_attribute_exception, self).__init__()
        self.__default = default

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AttributeError:
                return self.__default

        return wrapper


class _ClientArenaSkeleton(object):
    arenaUniqueID = 0
    guiType = _GUI_TYPE.UNKNOWN
    bonusType = _BONUS_TYPE.UNKNOWN
    bonusCapsOverrides = None
    arenaType = None
    componentSystem = None
    battleModifiers = BattleModifiers()
    period = _PERIOD.IDLE
    periodEndTime = 0
    periodLength = 0
    periodAdditionalInfo = None
    positions = {}
    vehicles = {}
    statistics = {}
    extraData = {}
    viewPoints = []
    isFogOfWarEnabled = False


class _ArenaTypeSkeleton(object):
    id = 0
    name = ''
    geometryName = ''
    gameplayName = ''
    maxTeamsInArena = TEAMS_IN_ARENA.MIN_TEAMS
    teamBasePositions = []
    teamLowLevelSpawnPoints = []
    teamSpawnPoints = []
    controlPoints = []
    flagSpawnPoints = []
    flagAbsorptionPoints = []
    resourcePoints = []
    repairPoints = {}
    soloTeamNumbers = []
    squadTeamNumbers = []
    boundingBox = ((0, 0), (0, 0))
    minimap = ''
    minimapLayers = {}
    overviewmap = ''
    winPointsSettings = None
    battleCountdownTimerSound = ''
    roundLength = 0
    battleEndingSoonTime = 0
    battleEndWarningAppearTime = 0
    battleEndWarningDuration = 0
    vehicleCamouflageKind = 0


class IArenaVisitor(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError


class _ArenaTypeVisitor(IArenaVisitor):
    __slots__ = ('_arenaType',)

    def __init__(self, arenaType=None):
        super(_ArenaTypeVisitor, self).__init__()
        if arenaType is not None:
            self._arenaType = weakref.proxy(arenaType)
        else:
            self._arenaType = _ArenaTypeSkeleton()
        return

    def clear(self):
        self._arenaType = None
        return

    def isSoloTeam(self, team):
        return team in self.getSoloTeamNumbers()

    def isSquadTeam(self, team):
        return team in self.getSquadTeamNumbers()

    def getTeamBasePositionsIterator(self):
        positions = self.getTeamBasePositions() or []
        for team, teamBasePoints in enumerate(positions, 1):
            for index, (_, point) in enumerate(teamBasePoints.items(), 1):
                if len(teamBasePoints) > 1:
                    number = index
                else:
                    number = 0
                yield (team, (point[0], 0, point[1]), number)

    def getControlPointsIterator(self):
        controlPoints = self.getControlPoints() or []
        for index, point in enumerate(controlPoints, 2):
            if len(controlPoints) > 1:
                number = index
            else:
                number = 0
            yield ((point[0], 0, point[1]), number)

    def getWinPointsCosts(self, isSolo=False, forVehicle=True):
        costKill, costFlags, costDamage = 0, set(), set()
        settings = self.getWinPointsSettings()
        winPointsCache = win_points.g_cache
        if settings is not None and winPointsCache is not None:
            winPoints = win_points.g_cache[settings]
            costKill = winPoints.pointsForKill(isSolo, forVehicle)
            costFlags = set(winPoints.pointsForFlag(isSolo))
            costDamage = winPoints.pointsForDamage(isSolo, forVehicle)
        return (costKill, costFlags, costDamage)

    def getWinPointsCAP(self):
        settings = self.getWinPointsSettings()
        winPointsCache = win_points.g_cache
        if settings is not None and winPointsCache is not None:
            pointsCAP = win_points.g_cache[settings].pointsCAP
        else:
            pointsCAP = 0
        return pointsCAP

    @catch_attribute_exception(default=_ArenaTypeSkeleton.id)
    def getID(self):
        return self._arenaType.id

    @catch_attribute_exception(default=_ArenaTypeSkeleton.name)
    def getName(self):
        return self._arenaType.name

    @catch_attribute_exception(default=_ArenaTypeSkeleton.geometryName)
    def getGeometryName(self):
        return self._arenaType.geometryName

    @catch_attribute_exception(default=_ArenaTypeSkeleton.gameplayName)
    def getGamePlayName(self):
        return self._arenaType.gameplayName

    @catch_attribute_exception(default=_ArenaTypeSkeleton.teamBasePositions)
    def getTeamBasePositions(self):
        return self._arenaType.teamBasePositions

    @catch_attribute_exception(default=_ArenaTypeSkeleton.teamLowLevelSpawnPoints)
    def getTeamLowLevelSpawnPoints(self):
        return self._arenaType.teamLowLevelSpawnPoints

    @catch_attribute_exception(default=_ArenaTypeSkeleton.teamSpawnPoints)
    def getTeamSpawnPoints(self):
        return self._arenaType.teamSpawnPoints

    @catch_attribute_exception(default=_ArenaTypeSkeleton.controlPoints)
    def getControlPoints(self):
        return self._arenaType.controlPoints

    @catch_attribute_exception(default=_ArenaTypeSkeleton.maxTeamsInArena)
    def getMaxTeamsOnArena(self):
        return self._arenaType.maxTeamsInArena

    def getTeamsOnArenaRange(self):
        return range(1, self.getMaxTeamsOnArena() + 1)

    @catch_attribute_exception(default=_ArenaTypeSkeleton.soloTeamNumbers)
    def getSoloTeamNumbers(self):
        return self._arenaType.soloTeamNumbers

    @catch_attribute_exception(default=_ArenaTypeSkeleton.squadTeamNumbers)
    def getSquadTeamNumbers(self):
        return self._arenaType.squadTeamNumbers

    @catch_attribute_exception(default=_ArenaTypeSkeleton.boundingBox)
    def getBoundingBox(self):
        return self._arenaType.boundingBox

    @catch_attribute_exception(default=_ArenaTypeSkeleton.minimap)
    def getMinimapTexture(self):
        return self._arenaType.minimap

    @catch_attribute_exception(default=_ArenaTypeSkeleton.minimapLayers)
    def getMinimapLayers(self):
        return self._arenaType.minimapLayers

    @catch_attribute_exception(default=_ArenaTypeSkeleton.overviewmap)
    def getOverviewMapTexture(self):
        return self._arenaType.overviewmap

    @catch_attribute_exception(default=_ArenaTypeSkeleton.winPointsSettings)
    def getWinPointsSettings(self):
        return self._arenaType.winPointsSettings

    @catch_attribute_exception(default=_ArenaTypeSkeleton.battleCountdownTimerSound)
    def getCountdownTimerSound(self):
        return self._arenaType.battleCountdownTimerSound

    @catch_attribute_exception(default=_ArenaTypeSkeleton.roundLength)
    def getTypeRoundLength(self):
        return self._arenaType.roundLength

    @catch_attribute_exception(default=_ArenaTypeSkeleton.battleEndingSoonTime)
    def getBattleEndingSoonTime(self):
        return self._arenaType.battleEndingSoonTime

    @catch_attribute_exception(default=_ArenaTypeSkeleton.battleEndWarningAppearTime)
    def getBattleEndWarningAppearTime(self):
        return self._arenaType.battleEndWarningAppearTime

    @catch_attribute_exception(default=_ArenaTypeSkeleton.battleEndWarningDuration)
    def getBattleEndWarningDuration(self):
        return self._arenaType.battleEndWarningDuration

    @catch_attribute_exception(default=_ArenaTypeSkeleton.vehicleCamouflageKind)
    def getVehicleCamouflageKind(self):
        return self._arenaType.vehicleCamouflageKind


class _ArenaGuiTypeVisitor(IArenaVisitor):
    __slots__ = ('_guiType',)

    def __init__(self, guiType=_GUI_TYPE.UNKNOWN):
        super(_ArenaGuiTypeVisitor, self).__init__()
        self._guiType = guiType

    @property
    def guiType(self):
        return self._guiType

    def clear(self):
        self._guiType = _GUI_TYPE.UNKNOWN

    def isRandomBattle(self):
        return self._guiType in (_GUI_TYPE.EPIC_RANDOM, _GUI_TYPE.RANDOM)

    def isBattleChatSupported(self):
        return self._guiType in _GUI_TYPE.BATTLE_CHAT_SETTING_SUPPORTED

    def isEventBattle(self):
        return self._guiType == _GUI_TYPE.EVENT_BATTLES

    def isTrainingBattle(self):
        return self._guiType in (_GUI_TYPE.TRAINING, _GUI_TYPE.EPIC_RANDOM_TRAINING)

    def isEpicRandomBattle(self):
        return self._guiType in (_GUI_TYPE.EPIC_RANDOM, _GUI_TYPE.EPIC_RANDOM_TRAINING)

    def isRankedBattle(self):
        return self._guiType == _GUI_TYPE.RANKED

    def isInEpicRange(self):
        return self._guiType in _GUI_TYPE.EPIC_RANGE

    def isEpicBattle(self):
        return self._guiType == _GUI_TYPE.EPIC_BATTLE

    def isBattleRoyale(self):
        return self._guiType == _GUI_TYPE.BATTLE_ROYALE

    def isMapbox(self):
        return self._guiType == _GUI_TYPE.MAPBOX

    def isWinback(self):
        return self._guiType == _GUI_TYPE.WINBACK

    def isMapsTraining(self):
        return self._guiType == _GUI_TYPE.MAPS_TRAINING

    def isStrongholdRange(self):
        return self._guiType in _GUI_TYPE.STRONGHOLD_RANGE

    def hasLabel(self):
        return self._guiType != _GUI_TYPE.UNKNOWN and self._guiType in _GUI_TYPE_LABEL.LABELS

    def getLabel(self):
        return _GUI_TYPE_LABEL.LABELS[self._guiType] if self._guiType in _GUI_TYPE_LABEL.LABELS else ''


class _ArenaBonusTypeVisitor(IArenaVisitor):
    __slots__ = ('_bonusType', '_specificOverrides')

    def __init__(self, bonusType=_BONUS_TYPE.UNKNOWN, specificOverrides=None):
        super(_ArenaBonusTypeVisitor, self).__init__()
        self._specificOverrides = specificOverrides
        self._bonusType = bonusType

    def clear(self):
        self._bonusType = _BONUS_TYPE.UNKNOWN
        self._specificOverrides = None
        return

    def hasBonusCap(self, bonusCap):
        return _CAPS.checkAny(self._bonusType, bonusCap, specificOverrides=self._specificOverrides)

    def hasAnyBonusCap(self, *caps):
        return _CAPS.checkAny(self._bonusType, specificOverrides=self._specificOverrides, *caps)

    def hasRage(self):
        return self.hasAnyBonusCap(_CAPS.RAGE_MECHANICS)

    def hasRespawns(self):
        return self.hasAnyBonusCap(_CAPS.RESPAWN)

    def isSquadSupported(self):
        return self.hasAnyBonusCap(_CAPS.SQUADS)

    def isDynSquadsSupported(self):
        return self.hasAnyBonusCap(_CAPS.DYN_SQUADS)

    def canTakeSquadXP(self):
        return self.hasAnyBonusCap(_CAPS.SQUAD_XP)

    def hasHealthBar(self):
        return self.hasAnyBonusCap(_CAPS.TEAM_HEALTH_BAR)

    def hasGameEndMessage(self):
        return self.hasAnyBonusCap(_CAPS.VICTORY_DEFEAT_MESSAGE)

    def hasCustomAllyDamageEffect(self):
        return self.hasAnyBonusCap(_CAPS.CUSTOM_ALLY_DAMAGE_EFFECT)

    def hasSectors(self):
        return self.hasAnyBonusCap(_CAPS.SECTOR_MECHANICS)

    def hasDestructibleEntities(self):
        return self.hasAnyBonusCap(_CAPS.DESTRUCTIBLE_ENTITIES)

    def hasStepRepairPoints(self):
        return self.hasAnyBonusCap(_CAPS.STEP_REPAIR_MECHANIC)

    def hasPlayerRanks(self):
        return self.hasAnyBonusCap(_CAPS.PLAYER_RANK_MECHANICS)

    def hasInBattleUpgrade(self):
        return self.hasAnyBonusCap(_CAPS.IN_BATTLE_UPGRADES)

    def hasDogTag(self):
        return self.hasAnyBonusCap(_CAPS.DOG_TAG)

    def isFriendlyFireMode(self):
        return self.hasAnyBonusCap(_CAPS.NO_ALLY_DAMAGE)

    def hasBattleNotifier(self):
        return self.hasAnyBonusCap(_CAPS.BATTLE_NOTIFIER)

    def hasPointsOfInterest(self):
        return self.hasAnyBonusCap(_CAPS.POINTS_OF_INTEREST)

    def hasSwitchSetups(self):
        return self.hasAnyBonusCap(_CAPS.SWITCH_SETUPS)

    def hasCommendationsMessages(self):
        return self.hasAnyBonusCap(_CAPS.COMMENDATIONS_MESSAGES)

    def hasLiveTags(self):
        return self.hasAnyBonusCap(_CAPS.COMMENDATIONS_LIVE_TAGS)


class _ArenaExtraDataVisitor(IArenaVisitor):
    __slots__ = ('_extra',)

    def __init__(self, extra=None):
        super(_ArenaExtraDataVisitor, self).__init__()
        if extra is None:
            self._extra = {}
        else:
            self._extra = extra
        return

    @property
    def queueType(self):
        return self._extra.get('queueType', QUEUE_TYPE.UNKNOWN)

    def isLowLevelBattle(self):
        return 0 < self._extra.get('battleLevel', 0) < 4

    def isMapsInDevelopmentEnabled(self):
        return self._extra.get('isRandomEventsAllowed', False)

    def getValue(self, key, default=None):
        return self._extra.get(key, default)

    def clear(self):
        self._extra = None
        return


class _ArenaVehiclesVisitor(IArenaVisitor):
    __slots__ = ('_vehicles',)

    def __init__(self, vehicles=None):
        super(_ArenaVehiclesVisitor, self).__init__()
        if vehicles is None:
            self._vehicles = {}
        else:
            self._vehicles = vehicles
        return

    def clear(self):
        self._vehicles = None
        return

    def getVehicleInfo(self, vehicleID):
        try:
            info = self._vehicles[vehicleID]
        except KeyError:
            info = {}

        return info

    def getVehicleExtras(self, vehicleID):
        try:
            extras = self._vehicles[vehicleID]['vehicleType'].extras[:]
        except (AttributeError, KeyError):
            extras = None

        return extras


class _ArenaModifiersVisitor(IArenaVisitor):
    __slots__ = ('_modifiers', '_shellData')

    def __init__(self, modifiers=None):
        super(_ArenaModifiersVisitor, self).__init__()
        self._modifiers = BattleModifiers() if modifiers is None else modifiers
        return

    def clear(self):
        self._modifiers = None
        return

    def getConstantsModification(self):
        return self._modifiers.getConstantsModification()


class _ClientArenaVisitor(IClientArenaVisitor):
    __slots__ = ('__weakref__', '_arena', '_canSubscribe', '_gui', '_bonus', '_type', '_extra', '_vehicles', '_modifiers')

    def __init__(self, arena, canSubscribe):
        super(_ClientArenaVisitor, self).__init__()
        self._arena = arena
        self._canSubscribe = canSubscribe
        self._type = _ArenaTypeVisitor(arenaType=self.getArenaType())
        self._gui = _ArenaGuiTypeVisitor(guiType=self.getArenaGuiType())
        self._extra = _ArenaExtraDataVisitor(extra=self.getArenaExtraData())
        self._vehicles = _ArenaVehiclesVisitor(vehicles=self.getArenaVehicles())
        self._modifiers = _ArenaModifiersVisitor(modifiers=self.getArenaModifiers())
        self._bonus = _ArenaBonusTypeVisitor(bonusType=self.getArenaBonusType(), specificOverrides=self.getArenaBonusCapsOverrides())

    @classmethod
    def createByArena(cls, arena=None):
        if arena is not None:
            arena = weakref.proxy(arena)
            canSubscribe = True
        else:
            arena = _ClientArenaSkeleton()
            canSubscribe = False
        return cls(arena, canSubscribe)

    @classmethod
    def createSkeleton(cls, arenaType=None, guiType=_GUI_TYPE.UNKNOWN, bonusType=_BONUS_TYPE.UNKNOWN):
        arena = _ClientArenaSkeleton()
        arena.arenaType = arenaType
        arena.guiType = guiType
        arena.bonusType = bonusType
        return cls(arena, False)

    def clear(self):
        self._arena = None
        self._gui.clear()
        self._bonus.clear()
        self._type.clear()
        self._extra.clear()
        self._vehicles.clear()
        return

    @property
    def gui(self):
        return self._gui

    @property
    def bonus(self):
        return self._bonus

    @property
    def type(self):
        return self._type

    @property
    def extra(self):
        return self._extra

    @property
    def vehicles(self):
        return self._vehicles

    @property
    def modifiers(self):
        return self._modifiers

    def isArenaInWaiting(self):
        return self.getArenaPeriod() == _PERIOD.WAITING

    def isBattleEndWarningEnabled(self):
        return GUI_SETTINGS.battleEndWarningEnabled

    def isSoloTeam(self, team):
        return False

    def hasRage(self):
        return self._bonus.hasRage()

    def hasRespawns(self):
        return self._bonus.hasRespawns() or self.isEnableExternalRespawn()

    def isEnableExternalRespawn(self):
        ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID, None)
        return bool(ownVehicle.enableExternalRespawn) if ownVehicle else False

    def isArenaLeaveAllowed(self):
        isLeaveAllowed = None
        ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID, None)
        vehRespComponent = ownVehicle and ownVehicle.dynamicComponents.get('VehicleRespawnComponent')
        if vehRespComponent:
            isLeaveAllowed = vehRespComponent.isLeaveAllowed
        return isLeaveAllowed

    def hasHealthBar(self):
        return self._bonus.hasHealthBar()

    def hasGameEndMessage(self):
        return self._bonus.hasGameEndMessage()

    def hasPlayerGroups(self):
        return self._arena.arenaType.numPlayerGroups > 0

    def hasSectors(self):
        return self._bonus.hasSectors()

    def hasStepRepairPoints(self):
        return self._bonus.hasStepRepairPoints()

    def hasPlayerRanks(self):
        return self._bonus.hasPlayerRanks()

    def hasDestructibleEntities(self):
        return self._bonus.hasDestructibleEntities()

    def hasDogTag(self):
        return self._bonus.hasDogTag()

    def hasDynSquads(self):
        return self._bonus.isDynSquadsSupported()

    def hasBattleNotifier(self):
        return self._bonus.hasBattleNotifier()

    def hasPointsOfInterest(self):
        return self._bonus.hasPointsOfInterest()

    def hasCommendationsMessages(self):
        return self._bonus.hasCommendationsMessages()

    def hasLiveTags(self):
        return self._bonus.hasLiveTags()

    def getArenaIcon(self, subdir=''):
        return getArenaImage(self._type.getGeometryName(), subdir)

    def getArenaSubscription(self):
        return self._arena if self._canSubscribe else None

    def getRoundLength(self):
        return self.getArenaModifiers()(BattleParams.BATTLE_LENGTH, self._type.getTypeRoundLength())

    def getTeamSpawnPoints(self, team):
        other = team - 1
        if self._extra.isLowLevelBattle():
            spawnPoints = self._type.getTeamLowLevelSpawnPoints()
            if other not in spawnPoints or not spawnPoints[other]:
                spawnPoints = self._type.getTeamSpawnPoints()
        else:
            spawnPoints = self._type.getTeamSpawnPoints()
        return spawnPoints

    def getTeamSpawnPointsIterator(self, team):
        for teamNum, points in enumerate(self.getTeamSpawnPoints(team), 1):
            for number, point in enumerate(points, 1):
                yield (teamNum, (point[0], 0, point[1]), number)

    def getVehicleCircularAoiRadius(self):
        return self.getArenaModifiers().getConstantsModification().VEHICLE_CIRCULAR_AOI_RADIUS

    def getVisibilityMinRadius(self):
        return self.getArenaModifiers()(BattleParams.VISION_MIN_RADIUS, VISIBILITY.MIN_RADIUS)

    @catch_attribute_exception(default=_ClientArenaSkeleton.isFogOfWarEnabled)
    def isArenaFogOfWarEnabled(self):
        return self._arena.isFogOfWarEnabled

    @catch_attribute_exception(default=_ClientArenaSkeleton.arenaUniqueID)
    def getArenaUniqueID(self):
        return self._arena.arenaUniqueID

    @catch_attribute_exception(default=_ClientArenaSkeleton.guiType)
    def getArenaGuiType(self):
        return self._arena.guiType

    @catch_attribute_exception(default=_ClientArenaSkeleton.bonusType)
    def getArenaBonusType(self):
        return self._arena.bonusType

    @catch_attribute_exception(default=_ClientArenaSkeleton.bonusCapsOverrides)
    def getArenaBonusCapsOverrides(self):
        return self._arena.bonusCapsOverrides

    @catch_attribute_exception(default=_ClientArenaSkeleton.arenaType)
    def getArenaType(self):
        return self._arena.arenaType

    @catch_attribute_exception(default=_ClientArenaSkeleton.period)
    def getArenaPeriod(self):
        return self._arena.period

    @catch_attribute_exception(default=_ClientArenaSkeleton.periodEndTime)
    def getArenaPeriodEndTime(self):
        return self._arena.periodEndTime

    @catch_attribute_exception(default=_ClientArenaSkeleton.periodLength)
    def getArenaPeriodLength(self):
        return self._arena.periodLength

    @catch_attribute_exception(default=_ClientArenaSkeleton.periodAdditionalInfo)
    def getArenaPeriodAdditionalInfo(self):
        return self._arena.periodAdditionalInfo

    @catch_attribute_exception(default=_ClientArenaSkeleton.positions)
    def getArenaPositions(self):
        return self._arena.positions

    @catch_attribute_exception(default=_ClientArenaSkeleton.extraData)
    def getArenaExtraData(self):
        return self._arena.extraData

    @catch_attribute_exception(default=_ClientArenaSkeleton.battleModifiers)
    def getArenaModifiers(self):
        return self._arena.battleModifiers

    @catch_attribute_exception(default=_ClientArenaSkeleton.vehicles)
    def getArenaVehicles(self):
        return self._arena.vehicles

    @catch_attribute_exception(default=_ClientArenaSkeleton.statistics)
    def getArenaStatistics(self):
        return self._arena.statistics

    @catch_attribute_exception(default=_ClientArenaSkeleton.viewPoints)
    def getArenaViewPoints(self):
        return self._arena.viewPoints

    @catch_attribute_exception(default=_ClientArenaSkeleton.componentSystem)
    def getComponentSystem(self):
        return self._arena.componentSystem
