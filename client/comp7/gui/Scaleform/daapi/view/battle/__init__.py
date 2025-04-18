# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/__init__.py
from comp7.gui.Scaleform.daapi.view.battle.page import Comp7BattlePage
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import frag_correlation_bar
    from comp7.gui.Scaleform.daapi.view.battle import players_panel
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from comp7.gui.Scaleform.daapi.view.battle import minimap
    from comp7.gui.Scaleform.daapi.view.battle import damage_panel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import situation_indicators
    from comp7.gui.Scaleform.daapi.view.battle import battle_loading
    from comp7.gui.Scaleform.daapi.view.battle import consumables_panel
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from comp7.gui.Scaleform.daapi.view.battle import full_stats
    from comp7.gui.Scaleform.daapi.view.battle import messages
    from comp7.gui.Scaleform.daapi.view.battle.shared.status_notifications import panel as sn_panel
    from comp7.gui.Scaleform.daapi.view.battle import stats_exchange
    from comp7.gui.Scaleform.daapi.view.battle.prebattle_timer import Comp7PrebattleTimer
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from comp7.gui.Scaleform.daapi.view.battle import battle_carousel
    from comp7.gui.Scaleform.daapi.view.battle import hint_panel
    from gui.Scaleform.daapi.view.battle.shared.points_of_interest import poi_notification_panel
    from comp7.gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    from comp7.gui.Scaleform.daapi.view.battle.filter_popover import Comp7TankCarouselFilterPopover
    from comp7.gui.Scaleform.daapi.view.battle import indicators
    from gui.Scaleform.framework import getSwfExtensionUrl
    SETTINGS_WINDOW_SCOPE = ScopeTemplates.SimpleScope(VIEW_ALIAS.SETTINGS_WINDOW, ScopeTemplates.DEFAULT_SCOPE)
    return (ViewSettings(VIEW_ALIAS.COMP7_BATTLE_PAGE, Comp7BattlePage, getSwfExtensionUrl('comp7', 'comp7BattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.Comp7BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.Comp7StatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.Comp7MinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.Comp7DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, sn_panel.Comp7StatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.Comp7ConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SITUATION_INDICATORS, situation_indicators.SituationIndicators, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, hint_panel.Comp7BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.Comp7PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POINT_OF_INTEREST_NOTIFICATIONS_PANEL, poi_notification_panel.PointsOfInterestPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.Comp7PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, Comp7PrebattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL, battle_carousel.PrebattleTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL_FILTER_POPOVER, Comp7TankCarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.TOP_WINDOW, BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL_FILTER_POPOVER, BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL_FILTER_POPOVER, SETTINGS_WINDOW_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COMP7_RECON_FLIGHT, indicators.ReconFlightIndicator, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.COMP7_BATTLE_PAGE), Comp7BattlePageBusinessHandler())


class Comp7BattlePageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        super(Comp7BattlePageBusinessHandler, self).__init__(((BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),), APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)
