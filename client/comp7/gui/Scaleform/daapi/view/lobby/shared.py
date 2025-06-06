# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/shared.py
import typing
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import AlertData, PeriodType
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getTillTimeByResource
from gui.shared.utils.functions import makeTooltip
from season_common import GameSeason

class Comp7AlertData(AlertData):
    _RES_ROOT = R.strings.comp7_ext.alertMessage
    _RES_REASON_ROOT = R.strings.comp7_ext.noVehicles.text
    _PERIOD_TYPES_WITH_SEASON = (PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END,
     PeriodType.AFTER_SEASON,
     PeriodType.BETWEEN_SEASONS)
    _PERIOD_TYPES_WITH_BUTTON = (PeriodType.NOT_AVAILABLE,
     PeriodType.STANDALONE_NOT_AVAILABLE,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.NOT_SET,
     PeriodType.STANDALONE_NOT_SET)
    _PERIOD_TYPES_PRIME_ALERT = (PeriodType.AVAILABLE,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.NOT_SET,
     PeriodType.ALL_NOT_SET,
     PeriodType.STANDALONE_NOT_SET,
     PeriodType.NOT_AVAILABLE,
     PeriodType.ALL_NOT_AVAILABLE,
     PeriodType.STANDALONE_NOT_AVAILABLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END,
     PeriodType.AFTER_SEASON)
    _PERIOD_TYPES_WITHOUT_TOOLTIP = (PeriodType.ALL_NOT_SET, PeriodType.ALL_NOT_AVAILABLE_END, PeriodType.AFTER_SEASON)

    @classmethod
    def _getAlertLabel(cls, periodInfo, serverShortName):
        params = cls._getAlertLabelParams(periodInfo)
        params['serverName'] = serverShortName
        if periodInfo.periodType in cls._PERIOD_TYPES_WITH_SEASON:
            periodType = periodInfo.periodType.value
            seasonName = comp7_model_helpers.getSeasonNameEnum().value
            return backport.text(cls._RES_ROOT.dyn(periodType, cls._RES_ROOT.undefined).dyn(seasonName)(), **params)
        return super(Comp7AlertData, cls)._getAlertLabel(periodInfo, serverShortName)

    @classmethod
    def _getTooltip(cls, periodInfo):
        return None if periodInfo.periodType in cls._PERIOD_TYPES_WITHOUT_TOOLTIP else COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO

    @classmethod
    def constructForBan(cls, duration):
        tillTime = getTillTimeByResource(duration, cls._RES_ROOT.timeLeft, removeLeadingZeros=True)
        resShortCut = R.strings.menu.headerButtons.fightBtn.tooltip.comp7BanIsSet
        header = backport.text(resShortCut.header())
        body = backport.text(resShortCut.body())
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonVisible=False, statusText=backport.text(cls._RES_ROOT.temporaryBan(), expiryTime=tillTime), isSimpleTooltip=True, tooltip=makeTooltip(header, body))

    @classmethod
    def constructForOffline(cls):
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonVisible=False, statusText=text_styles.vehicleStatusCriticalText(backport.text(cls._RES_ROOT.modeOffline())), shadowFilterVisible=True)

    @classmethod
    def constructForPreannounce(cls, season):
        seasonName = comp7_model_helpers.getSeasonNameEnum(season).value
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonVisible=False, statusText=text_styles.vehicleStatusCriticalText(backport.text(cls._RES_ROOT.preannounce.dyn(seasonName)(), date=backport.getShortDateTimeFormat(season.getStartDate()))))
