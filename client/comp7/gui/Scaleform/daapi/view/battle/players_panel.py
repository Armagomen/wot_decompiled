# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/players_panel.py
from comp7.gui.Scaleform.daapi.view.battle.comp7_voip_helper import Comp7VoipHelper, VoiceChatControlTextStyles
from comp7.gui.Scaleform.daapi.view.meta.Comp7PlayersPanelMeta import Comp7PlayersPanelMeta
from constants import ARENA_PERIOD

class PlayersPanel(Comp7PlayersPanelMeta):

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self.__voipHelper = Comp7VoipHelper(component=self, textStyle=VoiceChatControlTextStyles.PLAYERS_PANEL)

    def onVoiceChatControlClick(self):
        self.__voipHelper.onVoiceChatControlClick()

    def setPeriod(self, period):
        self.__voipHelper.enable(enable=self.__isVoipControlEnabled(period))

    def _populate(self):
        super(PlayersPanel, self)._populate()
        self.__voipHelper.populate()
        self.__voipHelper.enable(enable=self.__isVoipControlEnabled())

    def _dispose(self):
        self.__voipHelper.dispose()
        super(PlayersPanel, self)._dispose()

    @classmethod
    def __isVoipControlEnabled(cls, period=None):
        if period is None:
            period = cls.sessionProvider.shared.arenaPeriod.getPeriod()
        return period == ARENA_PERIOD.PREBATTLE
