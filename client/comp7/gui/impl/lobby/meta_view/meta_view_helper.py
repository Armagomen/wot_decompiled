# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/meta_view_helper.py
import logging
import typing
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank
from comp7.gui.impl.gen.view_models.views.lobby.progression_division import ProgressionDivision, State
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared
from helpers import dependency
from intervals import Interval
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_base_model import ProgressionBaseModel
    from comp7.gui.impl.gen.view_models.views.lobby.progression_item_base_model import ProgressionItemBaseModel
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)

def setRankItemData(itemModel, rankIdx, ranksConfig):
    setRankData(itemModel, rankIdx, ranksConfig)
    setDivisionData(itemModel, getRankDivisions(rankIdx, ranksConfig))
    return itemModel


def setProgressionItemData(itemModel, parentModel, rankIdx, ranksConfig):
    setRankData(itemModel, rankIdx, ranksConfig)
    setCurrentProgressionIdx(parentModel, rankIdx, ranksConfig)
    setDivisionData(itemModel, getRankDivisions(rankIdx, ranksConfig))


def setRankData(itemModel, rank, ranksConfig):
    sortedDivisions = getRankDivisions(rank, ranksConfig)
    rankLimits = Interval(sortedDivisions[0].range.begin, sortedDivisions[-1].range.end)
    itemModel.setRank(comp7_shared.getRankById(rank))
    itemModel.setFrom(rankLimits.begin)
    itemModel.setTo(rankLimits.end + 1)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setCurrentProgressionIdx(model, rank, ranksConfig, comp7Controller=None):
    sortedDivisions = getRankDivisions(rank, ranksConfig)
    rankLimits = Interval(sortedDivisions[0].range.begin, sortedDivisions[-1].range.end)
    isRankElite = rank == _getEliteRank()
    if not isRankElite or comp7Controller.isElite:
        if comp7Controller.rating in rankLimits:
            rankIdx = ranksConfig.ranksOrder.index(rank)
            model.setCurrentItemIndex(rankIdx)


def getRankDivisions(rank, ranksConfig):
    if len(ranksConfig.ranksOrder) != len(Rank):
        _logger.error('Config/ enum ranks length mismatch')
    sortedDivisions = ranksConfig.divisionsByRank[rank]
    if len(sortedDivisions) > len(Division):
        _logger.error('Config/ enum divisions length mismatch')
    return sortedDivisions


def setDivisionData(itemModel, divisions):
    divisionsArray = itemModel.getDivisions()
    divisionsArray.clear()
    for division in divisions:
        divisionModel = ProgressionDivision()
        divisionModel.setName(comp7_shared.getDivisionEnumValue(division))
        divisionModel.setState(getDivisionState(division))
        divisionsArray.addViewModel(divisionModel)

    divisionsArray.invalidate()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getDivisionState(division, comp7Controller=None):
    eliteRank = _getEliteRank()
    if division.rank == eliteRank and not comp7Controller.isElite:
        return State.INACTIVE
    currentRating = comp7Controller.rating
    if division.range.begin <= currentRating:
        if currentRating <= division.range.end:
            return State.CURRENT
        return State.ACHIEVED
    return State.INACTIVE


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getEliteRank(comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    eliteRank = ranksConfig.ranksOrder[-1]
    return eliteRank
