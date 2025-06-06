# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_full_stats.py
import BigWorld
from frontline.gui.Scaleform.daapi.view.meta.FrontlineFullStatsMeta import FrontlineFullStatsMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import i18n

class FrontlineFullStatsComponent(FrontlineFullStatsMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(FrontlineFullStatsComponent, self)._populate()
        self.as_initializeTextS(str(i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_MY_LANE).upper()), str(i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_ALL_LANES).upper()))
        BigWorld.player().arena.componentSystem.playerDataComponent.onCrewRolesFactorUpdated += self.__setGeneralBonus

    def _dispose(self):
        super(FrontlineFullStatsComponent, self)._dispose()
        arena = BigWorld.player().arena if hasattr(BigWorld.player(), 'arena') else None
        if arena and hasattr(arena, 'componentSystem'):
            componentSystem = BigWorld.player().arena.componentSystem
            if componentSystem:
                componentSystem.playerDataComponent.onCrewRolesFactorUpdated -= self.__setGeneralBonus
        return

    def __setGeneralBonus(self, newFactor, allyVehID=None, allyNewRank=None):
        self.as_setGeneralBonusS(newFactor)
