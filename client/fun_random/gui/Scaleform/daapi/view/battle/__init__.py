# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.classic import tab_screen
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.component import FunRandomBattleHintPanel
    from fun_random.gui.Scaleform.daapi.view.battle.battle_loading import FepBattleLoading
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    from gui.Scaleform.daapi.view.battle.classic import players_panel
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import minimap
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
    from gui.Scaleform.daapi.view.battle.shared import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from gui.Scaleform.daapi.view.battle.shared import consumables_panel
    from gui.Scaleform.daapi.view.battle.shared import situation_indicators
    from gui.Scaleform.daapi.view.battle.shared import ribbons_panel
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from gui.Scaleform.daapi.view.battle.shared import messages
    from gui.Scaleform.daapi.view.battle.shared.battle_hint import DefaultBattleHint
    from gui.Scaleform.daapi.view.battle.classic.map_info_tip import MapInfoTip
    return (ViewSettings(VIEW_ALIAS.CLASSIC_BATTLE_PAGE, ClassicPage, 'battlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, FepBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, tab_screen.TabScreenComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.ClassicMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.ConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SITUATION_INDICATORS, situation_indicators.SituationIndicators, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.BattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, FunRandomBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.PreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, DefaultBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.NEWBIE_HINT, DefaultBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MAP_INFO_TIP, MapInfoTip, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.CLASSIC_BATTLE_PAGE),)
