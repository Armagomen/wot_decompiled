# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/__init__.py
from gui.battle_results.components import base
from gui.impl import backport
from gui.impl.gen import R

__all__ = ('TOTAL_VO_META', 'MULTI_TEAM_TABS_BLOCK', 'REGULAR_TABS_BLOCK', 'VEHICLE_PROGRESS_STATS_BLOCK',
           'BATTLE_PASS_PROGRESS_STATS_BLOCK', 'QUESTS_PROGRESS_STATS_BLOCK', 'DOG_TAGS_PROGRESS_STATS_BLOCK',
           'REGULAR_COMMON_STATS_BLOCK', 'REGULAR_PERSONAL_STATS_BLOCK', 'REGULAR_TEAMS_STATS_BLOCK',
           'REGULAR_TEXT_STATS_BLOCK', 'CLAN_TEXT_STATS_BLOCK', 'STRONGHOLD_BATTLE_COMMON_STATS_BLOCK',
           'STRONGHOLD_PERSONAL_STATS_BLOCK', 'STRONGHOLD_TEAMS_STATS_BLOCK', 'CYBER_SPORT_BLOCK',
           'SANDBOX_PERSONAL_STATS_BLOCK', 'SANDBOX_TEAM_ITEM_STATS_ENABLE', 'SANDBOX_PERSONAL_ACCOUNT_DB_ID',
           'RANKED_COMMON_STATS_BLOCK', 'RANKED_TEAMS_STATS_BLOCK', 'RANKED_RESULTS_BLOCK',
           'RANKED_PERSONAL_STATS_BLOCK', 'RANKED_RESULTS_STATUS_BLOCK', 'BOOTCAMP_RESULTS_BLOCK',
           'RANKED_ENABLE_ANIMATION_BLOCK', 'EPIC_COMMON_STATS_BLOCK', 'EPIC_TABS_BLOCK', 'EPIC_PERSONAL_STATS_BLOCK',
           'EPIC_TEAMS_STATS_BLOCK', 'RANKED_SHOW_WIDGET_BLOCK', 'PROGRESSIVE_REWARD_VO', 'RANKED_RESULTS_STATE_BLOCK',
           'BR_TOTAL_VO_META', 'BR_TABS_BLOCK', 'BR_TEAM_STATS_BLOCK', 'BR_PERSONAL_STATS_BLOCK',
           'BR_COMMON_STATS_BLOCK', 'MAPS_TRAINING_RESULTS_BLOCK', 'COMP7_PERSONAL_STATS_BLOCK',
           'COMP7_COMMON_STATS_BLOCK', 'COMP7_TEAMS_STATS_BLOCK', 'COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK',
           'EFFICIENCY_TITLE_WITH_SKILLS_VO')
TOTAL_VO_META = base.DictMeta({'personal': {},
                               'common': {},
                               'team1': [],
                               'team2': [],
                               'textData': {},
                               'battlePass': None,
                               'quests': None,
                               'unlocks': [],
                               'tabInfo': [],
                               'cyberSport': None,
                               'isFreeForAll': False,
                               'closingTeamMemberStatsEnabled': True,
                               'selectedTeamMemberId': -1,
                               'progressiveReward': None,
                               'dog_tags': {},
                               'efficiencyTitle': backport.text(
                                   R.strings.battle_results.common.battleEfficiencyWithoutOreders.title())})
