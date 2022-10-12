# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/stats_exchange.py
import typing

import VOIP
from constants import ROLE_TYPE_TO_LABEL
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import DynamicVehicleStatsComponent
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.stats_exchange import PointsOfInterestStatsController
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker, createExchangeBroker, vehicle
from gui.Scaleform.daapi.view.meta.Comp7BattleStatisticDataControllerMeta import Comp7BattleStatisticDataControllerMeta
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.arena_vos import Comp7Keys
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

if typing.TYPE_CHECKING:
    pass

class Comp7VehicleInfoComponent(vehicle.VehicleInfoComponent):
    __slots__ = ()
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def addVehicleInfo(self, vInfoVO, overrides):
        super(Comp7VehicleInfoComponent, self).addVehicleInfo(vInfoVO, overrides)
        rank, division = vInfoVO.gameModeSpecific.getValue(Comp7Keys.RANK, default=(0, 0))
        return self._data.update({'role': ROLE_TYPE_TO_LABEL.get(vInfoVO.vehicleType.role, ''),
         'skillLevel': vInfoVO.gameModeSpecific.getValue(Comp7Keys.ROLE_SKILL_LEVEL, default=0),
         'rank': rank,
         'rankDivision': division,
         'voiceChatConnected': self.__getVoiceChatConnected(vInfoVO)})

    @classmethod
    def __getVoiceChatConnected(cls, vInfoVO):
        voipCtrl = cls.__sessionProvider.dynamic.comp7VOIPController
        if voipCtrl is None or not voipCtrl.isTeamVoipEnabled:
            return True
        else:
            return True if vInfoVO.isEnemy() or not vInfoVO.isPlayer() else vInfoVO.gameModeSpecific.getValue(Comp7Keys.VOIP_CONNECTED, default=False)


class Comp7StatisticsDataController(Comp7BattleStatisticDataControllerMeta):

    def __init__(self):
        super(Comp7StatisticsDataController, self).__init__()
        self.__poiStatsController = None
        self.__arenaInfoComponent = None
        return

    def _createExchangeBroker(self, exchangeCtx):
        exchangeBroker = createExchangeBroker(exchangeCtx)
        exchangeBroker.setVehiclesInfoExchange(vehicle.VehiclesExchangeBlock(Comp7VehicleInfoComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.Comp7SortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=None))
        exchangeBroker.setVehiclesStatsExchange(vehicle.VehiclesExchangeBlock(DynamicVehicleStatsComponent(), positionComposer=broker.BiDirectionComposer(), idsComposers=None, statsComposers=(vehicle.TotalStatsComposer(),)))
        exchangeBroker.setVehicleStatusExchange(vehicle.VehicleStatusComponent(idsComposers=(vehicle.TeamsSortedIDsComposer(sortKey=vos_collections.Comp7SortKey), vehicle.TeamsCorrelationIDsComposer()), statsComposers=(vehicle.TotalStatsComposer(),)))
        return exchangeBroker

    def _getArenaWinTextShort(self):
        return backport.text(R.strings.arenas.type.comp7.short_description())

    def startControl(self, battleCtx, arenaVisitor):
        super(Comp7StatisticsDataController, self).startControl(battleCtx, arenaVisitor)
        self.__poiStatsController = PointsOfInterestStatsController(self)
        self.__poiStatsController.startControl()
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable += self.__onChannelUpdated
            voipMgr.onChannelLost += self.__onChannelUpdated
        return

    def stopControl(self):
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable -= self.__onChannelUpdated
            voipMgr.onChannelLost -= self.__onChannelUpdated
        if self.__poiStatsController is not None:
            self.__poiStatsController.stopControl()
            self.__poiStatsController = None
        super(Comp7StatisticsDataController, self).stopControl()
        return

    def __onChannelUpdated(self, *_, **__):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())
