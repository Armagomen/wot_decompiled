# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_battle_modification_panel.py
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from frontline.gui.Scaleform.daapi.view.meta.FrontlineModificationPanelMeta import FrontlineModificationPanelMeta
from frontline.gui.frontline_helpers import FLBattleTypeDescription
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class FrontlineBattleModificationPanel(FrontlineModificationPanelMeta, IArenaVehiclesController):
    __slots__ = ('_isVisible', '_lastPeriod')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FrontlineBattleModificationPanel, self).__init__()
        self._isVisible = False
        self._lastPeriod = ARENA_PERIOD.IDLE

    def _populate(self):
        super(FrontlineBattleModificationPanel, self)._populate()
        g_playerEvents.onArenaPeriodChange += self._onRoundStarted
        self.addListener(events.GameEvent.BATTLE_LOADING, self._onBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.BATTLE_LOADING, self._onBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onArenaPeriodChange -= self._onRoundStarted
        super(FrontlineBattleModificationPanel, self)._dispose()

    def __animationStart(self):
        self.as_setDataS(self.__getData())
        self._isVisible = True
        self.as_setVisibleS(True)

    def __animationHide(self):
        self._isVisible = False
        self.as_setVisibleS(False)

    def _onBattleLoading(self, event):
        if not event.ctx['isShown'] and not self._lastPeriod:
            self._onRoundStarted(self.__sessionProvider.shared.arenaPeriod.getPeriod())

    def _onRoundStarted(self, period, *_):
        if self._lastPeriod == period:
            return
        if self._isVisible and period == ARENA_PERIOD.BATTLE:
            self.__animationHide()
        elif not self._isVisible and period in [ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE]:
            self.__animationStart()
        self._lastPeriod = period

    def __getData(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        modifier = arenaDP.getReservesModifier() if arenaDP else None
        return {'modificationIconPath': FLBattleTypeDescription.getBattleTypeIconPath(modifier, 'c_64x64'),
         'modificationTitle': FLBattleTypeDescription.getTitle(modifier),
         'modificationDescription': FLBattleTypeDescription.getShortDescription(modifier)}
