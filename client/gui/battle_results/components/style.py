# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/style.py
from collections import namedtuple
from constants import IGR_TYPE
from gui import makeHtmlString
from gui.Scaleform import settings
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.battle_results.components import base
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
WIDE_STAT_ROW = 'wideLine'
NORMAL_STAT_ROW = 'normalLine'
SMALL_STAT_LINE = 'smallLineUI'
LINE_BRAKE_STR = '<br/>'
_STATS_INFOTIP_HEADER_FORMAT = '#battle_results:team/stats/infotip_{0}/header'
_VEHICLE_STATE_PREFIX = '{0} ('
_VEHICLE_STATE_SUFFIX = ')'
_DIFF_FORMAT = '+ {}'
_LINE_FEED = '\n'

def getUnknownPlayerName(isEnemy=False):
    return i18n.makeString(BATTLE_RESULTS.PLAYERS_ENEMY_UNKNOWN) if isEnemy else i18n.makeString(BATTLE_RESULTS.PLAYERS_TEAMMATE_UNKNOWN)


I18nDeathReason = namedtuple('I18nDeathReason', 'i18nString prefix suffix')

def makeI18nDeathReason(deathReason):
    state = backport.text(R.strings.battle_results.common.vehicleState.dyn('dead{}'.format(deathReason), R.invalid)())
    return I18nDeathReason(state, _VEHICLE_STATE_PREFIX.format(state), _VEHICLE_STATE_SUFFIX)


def markValueAsError(value):
    return makeHtmlString('html_templates:lobby/battle_results', 'negative_value', {'value': value})


def markValueAsEmpty(value):
    return makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': value})


def makeMarksOfMasteryText(marksOfMastery, totalVehicles):
    return makeHtmlString('html_templates:lobby/profileStatistics', 'marksOfMasteryText', {'marksOfMastery': marksOfMastery,
     'totalVehicles': totalVehicles})


def getIntegralFormatIfNoEmpty(value):
    return backport.getIntegralFormat(value) if value else markValueAsEmpty(value)


def getFractionalFormatIfNoEmpty(value):
    return backport.getFractionalFormat(value) if value else markValueAsEmpty(value)


_SPLASH_CHAR_NO_EMPTY_STAT = '/'
_SPLASH_CHAR_EMPTY_STAT = markValueAsEmpty(_SPLASH_CHAR_NO_EMPTY_STAT)

def getTooltipParamsStyle(paramKey=None):
    if paramKey is None:
        paramKey = BATTLE_RESULTS.COMMON_TOOLTIP_PARAMS_VAL
    return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_params_style', {'text': i18n.makeString(paramKey)})


def _makeModuleTooltipLabel(module, suffix):
    return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_crit_label', {'image': '{0}{1}'.format(module, suffix),
     'value': backport.text(R.strings.item_types.dyn(module).name())})


def makeCriticalModuleTooltipLabel(module):
    return _makeModuleTooltipLabel(module, 'Critical')


def makeDestroyedModuleTooltipLabel(module):
    return _makeModuleTooltipLabel(module, 'Destroyed')


def makeTankmenTooltipLabel(role):
    return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_crit_label', {'image': '{0}Destroyed'.format(role),
     'value': backport.text(R.strings.item_types.tankman.roles.dyn(role)())})


class StatRow(base.StatsItem):
    __slots__ = ('text', 'label', 'lineType', 'column1', 'column2', 'column3', 'column4')

    def __init__(self, text, label, lineType, column1=_LINE_FEED, column2=_LINE_FEED, column3=_LINE_FEED, column4=_LINE_FEED):
        super(StatRow, self).__init__('')
        self.text = text
        self.label = label
        self.lineType = lineType
        self.column1 = column1
        self.column2 = column2
        self.column3 = column3
        self.column4 = column4

    def setRecord(self, record, reusable):
        pass

    def getVO(self):
        return {'label': self.label,
         'labelStripped': self.text,
         'col1': self.column1,
         'col2': self.column2,
         'col3': self.column3,
         'col4': self.column4,
         'lineType': self.lineType}


class EmptyStatRow(StatRow):
    __slots__ = ()

    def __init__(self):
        super(EmptyStatRow, self).__init__(_LINE_FEED, _LINE_FEED, None)
        return


def makeStatRow(label='', labelArgs=None, column1=None, column2=None, column3=None, column4=None, htmlKey=''):
    if column2 is not None:
        lineType = WIDE_STAT_ROW
    elif not any((column2, column3, column4)):
        lineType = None
    else:
        lineType = NORMAL_STAT_ROW
    if label:
        if labelArgs:
            i18nText = i18n.makeString(BATTLE_RESULTS.getDetailsCalculation(statName=label), **labelArgs)
        else:
            i18nText = i18n.makeString(BATTLE_RESULTS.getDetailsCalculation(statName=label))
        if htmlKey:
            label = makeHtmlString('html_templates:lobby/battle_results', htmlKey, {'value': i18nText})
        else:
            label = i18nText
    else:
        label = makeHtmlString('html_templates:lobby/battle_results', htmlKey)
        import re
        i18nText = re.sub('<[^<]+?>', '', label)
    return {'label': label,
     'labelStripped': i18nText,
     'col1': column1 if column1 is not None else _LINE_FEED,
     'col2': column2 if column2 is not None else _LINE_FEED,
     'col3': column3 if column3 is not None else _LINE_FEED,
     'col4': column4 if column4 is not None else _LINE_FEED,
     'lineType': lineType}


def makeCreditsLabel(value, canBeFaded=False, isDiff=False, useBigIcon=False, forceFade=False):
    formatted = backport.getGoldFormat(int(round(value)))
    if value < 0:
        formatted = markValueAsError(formatted)
    if isDiff:
        formatted = _DIFF_FORMAT.format(formatted)
    if useBigIcon:
        template = 'credits_label'
    elif canBeFaded and (not value or forceFade):
        template = 'credits_small_inactive_label'
    else:
        template = 'credits_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeGoldLabel(value, canBeFaded=False, isDiff=False, forceFade=False):
    formatted = backport.getGoldFormat(value)
    if isDiff:
        formatted = _DIFF_FORMAT.format(formatted)
    if canBeFaded and (not value or forceFade):
        template = 'gold_small_inactive_label'
    else:
        template = 'gold_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeXpLabel(value, canBeFaded=False, isDiff=False, useBigIcon=False, forceFade=False):
    formatted = backport.getIntegralFormat(int(value))
    if value < 0:
        formatted = markValueAsError(formatted)
    if isDiff:
        formatted = _DIFF_FORMAT.format(formatted)
    if useBigIcon:
        template = 'xp_label'
    elif canBeFaded and (not value or forceFade):
        template = 'xp_small_inactive_label'
    else:
        template = 'xp_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeFreeXpLabel(value, canBeFaded=False, forceFade=False):
    if canBeFaded and (not value or forceFade):
        template = 'free_xp_small_inactive_label'
    else:
        template = 'free_xp_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': backport.getIntegralFormat(int(value))})


def makeCrystalLabel(value):
    formatted = backport.getIntegralFormat(int(value))
    if value < 0:
        formatted = markValueAsError(formatted)
    return makeHtmlString('html_templates:lobby/battle_results', 'crystal_small_label', {'value': formatted})


def makePercentLabel(value):
    formatted = backport.getGoldFormat(int(value))
    template = 'percent'
    if value < 0:
        formatted = markValueAsError(formatted)
        template = 'negative_percent'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeIGRIcon(igrType):
    if igrType == IGR_TYPE.PREMIUM:
        iconName = 'premium'
    else:
        iconName = 'basic'
    return makeHtmlString('html_templates:igr/iconSmall', iconName)


def makeIGRBonusLabel(igrIcon):
    return i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_IGRBONUS, igrIcon=igrIcon)


def makeIGRBonusValue(factor):
    return makeHtmlString('html_templates:lobby/battle_results', 'igr_bonus', {'value': backport.getNiceNumberFormat(factor)})


def makeMultiXPFactorValue(value, useFreeXPStyle=False):
    if value > 0:
        if useFreeXPStyle:
            template = 'multy_xp_small_multiplier_free'
        else:
            template = 'multy_xp_small_multiplier'
    elif useFreeXPStyle:
        template = 'multy_xp_small_label_free'
    else:
        template = 'multy_xp_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': int(value)})


def makeAOGASFactorValue(value):
    formatted = ''.join((i18n.makeString(BATTLE_RESULTS.COMMON_XPMULTIPLIERSIGN), backport.getFractionalFormat(value)))
    formatted = markValueAsError(formatted)
    return formatted


def makeMultiLineHtmlString(seq):
    return LINE_BRAKE_STR.join(seq)


def makeStatValue(field, value):
    tooltip = ''
    tooltipHeader = _STATS_INFOTIP_HEADER_FORMAT.format(field)
    if i18n.doesTextExist(tooltipHeader):
        tooltip = makeTooltip(header=i18n.makeString(tooltipHeader), body=i18n.makeString(BATTLE_RESULTS.getTeamStatsInfotipBody(statName=field)))
    return {'label': i18n.makeString(BATTLE_RESULTS.getTeamStatsLabel(statName=field)),
     'value': value,
     'infoTooltip': tooltip}


def makeTimeStatsVO(field, value):
    return {'label': i18n.makeString(BATTLE_RESULTS.getDetailsTimeLbl(statName=field)),
     'value': value}


def makeBadgeIcon(badge):
    return settings.getBadgeIconPath(settings.BADGES_ICONS.X24, badge)


def makeRankedResultsTitle(title):
    return text_styles.promoTitle(title)


def makeRankedPointValue(pointsValue):
    return makeHtmlString('html_templates:lobby/battle_results', 'xp_small_label', {'value': text_styles.playerOnline(pointsValue)})


def makeRankedPointHugeValue(pointsValue):
    return makeHtmlString('html_templates:lobby/battle_results', 'xp_small_label', {'value': text_styles.hightlight(pointsValue)})


def markVehicleAsTeamKiller(vehicle):
    vehicle.vehicleStatePrefix = vehicle.vehicleStatePrefix[:-1] + makeTeamKillerText(vehicle.vehicleStatePrefix[-1])
    vehicle.vehicleStateSuffix = makeTeamKillerText(vehicle.vehicleStateSuffix)


def makeTeamKillerText(text):
    return makeHtmlString('html_templates:lobby/battle_results', 'team_killer', {'text': text})


def makeRankedNickNameValue(name):
    return text_styles.playerOnline(name)


def makeRankedNickNameHugeValue(name):
    return text_styles.hightlight(name)


class GroupMiddleLabelBlock(base.DirectStatsItem):

    def __init__(self, label):
        super(GroupMiddleLabelBlock, self).__init__('', {'groupLabel': text_styles.main(label)})


class _SlashedValueItem(base.StatsItem):

    def _convert(self, value, reusable):
        if value:
            converted = str(value)
            isEmpty = False
        else:
            converted = markValueAsEmpty(value)
            isEmpty = True
        return (isEmpty, converted)


class _RedSlashedValueItem(base.StatsItem):

    def _convert(self, value, reusable):
        isEmpty = False if value > 0 else True
        converted = str(value)
        return (isEmpty, converted)


class _RedSlashedValuesMeta(base.ListMeta):

    def registerComponent(self, component):
        super(_RedSlashedValuesMeta, self).registerComponent(component)
        if not isinstance(component, _RedSlashedValueItem):
            raise base.StatsComponentError('Block can be added _RedSlashedValueItem only')

    def generateVO(self, components):
        if not self._registered:
            return _SPLASH_CHAR_EMPTY_STAT
        result = []
        noStats = True
        for component in components:
            isEmpty, value = component.getVO()
            noStats = noStats and isEmpty
            result.append(value)

        markValue = markValueAsEmpty if noStats else markValueAsError
        return markValue(_SPLASH_CHAR_NO_EMPTY_STAT.join(result))


class _SlashedValuesMeta(base.ListMeta):

    def registerComponent(self, component):
        super(_SlashedValuesMeta, self).registerComponent(component)
        if not isinstance(component, _SlashedValueItem):
            raise base.StatsComponentError('Block can be added SlashedValuesItem only')

    def generateVO(self, components):
        if not self._registered:
            return _SPLASH_CHAR_EMPTY_STAT
        result = []
        noStats = True
        for component in components:
            isEmpty, value = component.getVO()
            noStats = noStats and isEmpty
            result.append(value)

        if noStats:
            slash = _SPLASH_CHAR_EMPTY_STAT
        else:
            slash = _SPLASH_CHAR_NO_EMPTY_STAT
        return slash.join(result)


class TwoItemsWithSlashBlock(base.StatsBlock):

    def __init__(self, itemClass, meta=None, field=''):
        super(TwoItemsWithSlashBlock, self).__init__(meta=meta, field=field)
        self._itemClass = itemClass
        self.addComponent(0, itemClass(''))
        self.addComponent(1, itemClass(''))

    def setRecord(self, result, reusable):
        for index, value in enumerate(result):
            self.getComponent(index).setRecord(value, reusable)

    def clone(self, *exclude):
        return TwoItemsWithSlashBlock(self._itemClass, meta=self._meta, field=self._field)


class SlashedValuesBlock(TwoItemsWithSlashBlock):

    def __init__(self, field=''):
        super(SlashedValuesBlock, self).__init__(_SlashedValueItem, meta=_SlashedValuesMeta(), field=field)


class RedSlashedValuesBlock(TwoItemsWithSlashBlock):

    def __init__(self, field=''):
        super(RedSlashedValuesBlock, self).__init__(_RedSlashedValueItem, meta=_RedSlashedValuesMeta(), field=field)


class MetersToKillometersItem(base.StatsItem):

    def _convert(self, value, reusable):
        converted = backport.getFractionalFormat(value / 1000.0)
        if not value:
            converted = markValueAsEmpty(converted)
        return converted


class XpStatsItem(base.StatsItem):

    def _convert(self, value, reusable):
        converted = makeXpLabel(value)
        if not value:
            converted = markValueAsEmpty(converted)
        return converted
