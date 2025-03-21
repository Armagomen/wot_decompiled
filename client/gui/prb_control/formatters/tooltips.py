# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/formatters/tooltips.py
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.role_presenter_helper import getRoleUserName
from helpers import i18n
from prebattle_shared import LIMIT_DEFAULTS

def getAbsenceCrewList():
    crewList = ''
    vehicle = g_currentVehicle.item
    crewRoles = vehicle.descriptor.type.crewRoles
    for slotIdx, tman in vehicle.crew:
        if tman is None:
            userString = getRoleUserName(crewRoles[slotIdx][0]).lower()
            crewList += (', ' if crewList else '') + userString

    return crewList


def getCrewNotFullTooltip():
    crewList = getAbsenceCrewList()
    return makeTooltip('#tooltips:redButton/disabled/crew/notFull/header', i18n.makeString('#tooltips:redButton/disabled/crew/notFull/body') % crewList)


def getVehicleStateInvalidTooltip(restriction):
    return '#tooltips:redButton/disabled/{0:>s}'.format(restriction)


def getVehicleClassInvalidTooltip(teamsLimit, restriction):
    classTag = PREBATTLE_RESTRICTION.getVehClassRestrictions().get(restriction)
    minLevel, maxLevel = prb_getters.getClassLevelLimits(teamsLimit, classTag)
    return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/{0:>s}/header'.format(restriction)), i18n.makeString('#tooltips:redButton/disabled/{0:>s}/body'.format(restriction), minLevel, maxLevel))


def getLevelInvalidTooltip(teamLimits, restriction):
    minLevel, maxLevel = prb_getters.getLevelLimits(teamLimits)
    return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/{0:>s}/header'.format(restriction)), i18n.makeString('#tooltips:redButton/disabled/{0:>s}/body'.format(restriction), minLevel, maxLevel))


def getTotalLevelInvalidTooltip(teamsLimit, restriction):
    minLevel, maxLevel = prb_getters.getTotalLevelLimits(teamsLimit)
    return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/{0:>s}/header'.format(restriction)), i18n.makeString('#tooltips:redButton/disabled/{0:>s}/body'.format(restriction), minLevel, maxLevel))


def getActionDisabledTooltip(restriction, entity=None):
    if not restriction:
        return
    else:
        tooltip = None
        if restriction == PREBATTLE_RESTRICTION.CREW_NOT_FULL:
            tooltip = getCrewNotFullTooltip()
        elif restriction in PREBATTLE_RESTRICTION.VEHICLE_INVALID_STATES:
            tooltip = getVehicleStateInvalidTooltip(restriction)
        else:
            if entity:
                teamLimits = entity.getSettings().getTeamLimits(entity.getPlayerTeam())
            else:
                LOG_ERROR('Entity is not defined')
                teamLimits = LIMIT_DEFAULTS
            if PREBATTLE_RESTRICTION.inVehClassLimit(restriction):
                tooltip = getVehicleClassInvalidTooltip(teamLimits, restriction)
            elif restriction == PREBATTLE_RESTRICTION.LIMIT_TOTAL_LEVEL:
                tooltip = getTotalLevelInvalidTooltip(teamLimits, restriction)
            elif restriction == PREBATTLE_RESTRICTION.LIMIT_LEVEL:
                tooltip = getLevelInvalidTooltip(teamLimits, restriction)
            else:
                LOG_ERROR('Formatter not found', restriction)
        return tooltip
