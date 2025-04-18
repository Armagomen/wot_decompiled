# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_model_helpers.py
import logging
from itertools import izip
import typing
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName, Rank
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from typing import Optional
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from season_common import GameSeason
    from comp7_ranks_common import Comp7Division
    from comp7.gui.impl.gen.view_models.views.lobby.division_info_model import DivisionInfoModel
    from comp7.gui.impl.gen.view_models.views.lobby.schedule_info_model import ScheduleInfoModel
    from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonModel
_logger = logging.getLogger(__name__)
_SEASONS_NAMES_BY_NUMBER = {1: SeasonName.FIRST,
 2: SeasonName.SECOND,
 3: SeasonName.THIRD}
SEASONS_NUMBERS_BY_NAME = {v.value:k for k, v in _SEASONS_NAMES_BY_NUMBER.iteritems()}

def setDivisionInfo(model, division=None):
    division = division or comp7_shared.getPlayerDivision()
    if division is None:
        return
    else:
        divisionValue = comp7_shared.getDivisionEnumValue(division)
        model.setName(divisionValue)
        model.setFrom(division.range.begin)
        model.setTo(division.range.end + 1)
        return


def getValidSeason(season=None):
    return season or _getCurrentSeason() or _getPreannouncedSeason() or _getPrevSeason() or _getNextSeason()


def setSeasonInfo(model, season=None):
    season = getValidSeason(season)
    _SeasonPresenter.setSeasonInfo(model, season)


def setScheduleInfo(model):
    season = getValidSeason()
    if season is not None:
        model.setTooltipId(COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO)
    _SeasonPresenter.setSeasonInfo(model.season, season)
    yearState = comp7_shared.getProgressionYearState()
    model.year.setState(yearState)
    return


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRanksInactivityInfo(model, comp7Controller=None):
    model.setHasRankInactivityWarning(comp7_shared.hasPlayerRankInactivityWarning())
    model.setRankInactivityCount(comp7Controller.activityPoints)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setElitePercentage(model, comp7Controller=None):
    model.setTopPercentage(comp7Controller.leaderboard.getEliteRankPercent())


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRankInfo(model, comp7Controller=None):
    seasonNumber = comp7Controller.getActualSeasonNumber()
    if not seasonNumber:
        return
    rating = comp7Controller.getRatingForSeason(seasonNumber)
    division = comp7_shared.getPlayerDivisionByRating(rating)
    rankEnum = comp7_shared.getRankEnumValue(division)
    model.setCurrentRank(rankEnum)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getYearlyRewardsRank(comp7Controller=None):
    seasonPointsSum = sum(comp7Controller.getReceivedSeasonPoints().itervalues())
    costs = comp7Controller.getYearlyRewards().getCosts()
    costs.reverse()
    for cost, rank in izip(costs, Rank):
        if cost <= seasonPointsSum:
            return rank


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setMaxRankInfo(model, comp7Controller=None):
    seasonNumber = comp7Controller.getActualSeasonNumber()
    if not seasonNumber:
        return
    maxAchivedRankNumber = comp7Controller.getMaxRankNumberForSeason(seasonNumber)
    config = comp7Controller.getRanksConfig()
    ranksOrder = config.ranksOrder
    rankId = ranksOrder[maxAchivedRankNumber - 1]
    model.setMaxAchievedRank(comp7_shared.getRankById(rankId))


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isModeForcedDisabled(status, comp7Controller=None):
    return not comp7Controller.isAvailable() and status == PrimeTimeStatus.AVAILABLE


def getSeasonNameEnum(season=None):
    season = getValidSeason(season)
    return _SEASONS_NAMES_BY_NUMBER.get(season.getNumber()) if season else None


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getCurrentSeason(comp7Controller=None):
    return comp7Controller.getCurrentSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getPreannouncedSeason(comp7Controller=None):
    return comp7Controller.getPreannouncedSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getNextSeason(comp7Controller=None):
    return comp7Controller.getNextSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getPrevSeason(comp7Controller=None):
    return comp7Controller.getPreviousSeason()


class _SeasonPresenter(object):

    @classmethod
    def setSeasonInfo(cls, model, season):
        formattedServerTimestamp = round(getServerUTCTime())
        if season is not None:
            model.setName(getSeasonNameEnum(season))
            model.setStartTimestamp(season.getStartDate())
            model.setEndTimestamp(season.getEndDate())
            model.setServerTimestamp(formattedServerTimestamp)
            model.setHasTentativeDates(season.hasTentativeDates())
        model.setState(cls.__getSeasonState(season))
        return

    @staticmethod
    def __getSeasonState(season):
        if season is not None:
            currentTime = getServerUTCTime()
            if currentTime < season.getStartDate():
                return SeasonState.NOTSTARTED
            if currentTime > season.getEndDate():
                return SeasonState.END
        return comp7_shared.getCurrentSeasonState()
