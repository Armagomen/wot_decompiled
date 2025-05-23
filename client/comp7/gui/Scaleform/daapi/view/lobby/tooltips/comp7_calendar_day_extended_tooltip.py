# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/tooltips/comp7_calendar_day_extended_tooltip.py
from datetime import datetime
from comp7.gui.Scaleform.daapi.view.lobby.tooltips.comp7_calendar_day_tooltip import Comp7CalendarDayTooltip
from comp7.gui.comp7_constants import SELECTOR_BATTLE_TYPES
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers
from comp7.gui.shared.tooltips import TOOLTIP_TYPE
from gui.Scaleform.daapi.view.lobby.formatters.tooltips import packCalendarBlock
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from helpers import time_utils
_TOOLTIP_MIN_WIDTH = 210

class Comp7CalendarDayExtendedTooltip(Comp7CalendarDayTooltip):
    _TOOLTIP_TYPE = TOOLTIP_TYPE.COMP7_CALENDAR_DAY_EXTENDED_INFO

    def _packBlocks(self, selectedTime):
        items = []
        if self.__isSeasonEnded(selectedTime):
            return items
        blocks = []
        currentSeason = self._controller.getCurrentSeason()
        if currentSeason:
            daysLeft = int((currentSeason.getEndDate() - time_utils.getServerUTCTime()) / time_utils.ONE_DAY)
            blocks.append(self.__packTimeLeftBlock(daysLeft))
        blocks.append(self._packHeaderBlock())
        blocks.extend(self.__packCalendarBlock(selectedTime))
        items.append(formatters.packBuildUpBlockData(blocks, 13))
        return items

    def __packTimeLeftBlock(self, daysLeft):
        return formatters.packTextBlockData(text=text_styles.stats(backport.ntext(self._RES_ROOT.timeLeft.dyn(comp7_model_helpers.getSeasonNameEnum().value)(), daysLeft, days=daysLeft)), blockWidth=_TOOLTIP_MIN_WIDTH)

    def __isSeasonEnded(self, selectedTime):
        if selectedTime is None:
            selectedTime = time_utils.getCurrentLocalServerTimestamp()
        seasonEnd = None
        if self._controller.getCurrentSeason():
            seasonEnd = self._controller.getCurrentSeason().getEndDate()
            seasonEnd = datetime.fromtimestamp(seasonEnd).date()
        return datetime.fromtimestamp(selectedTime).date() > seasonEnd

    def __packCalendarBlock(self, selectedTime):
        return packCalendarBlock(self._controller, selectedTime, SELECTOR_BATTLE_TYPES.COMP7)
