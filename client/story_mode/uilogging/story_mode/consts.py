# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/uilogging/story_mode/consts.py
from enum import Enum

class Features(str, Enum):
    ONBOARDING = 'onboarding'
    STORY_MODE = 'story_mode'


class LogWindows(str, Enum):
    HELP = 'help_window'
    QUEUE = 'queue_window'
    INTRO_VIDEO = 'intro_video'
    OUTRO_VIDEO = 'outro_video'
    PRE_BATTLE = 'pre_battle_window'
    POST_BATTLE = 'post_battle_window'
    EPILOGUE = 'epilogue_window'
    CONGRATULATIONS = 'congratulations_window'
    MODE_SELECTOR_CARD = 'mode_selector_card'
    MISSION_SELECTION = 'mission_selection_window'
    ESCAPE_MENU = 'escape_menu'
    SETTINGS_MENU = 'settings_menu'
    INFO_PAGE = 'info_page'
    ENTRY_POINT = 'entry_point'
    ENTRY_POINT_EVENT = 'entry_point_vday'
    NEWBIE_ADVERTISING = 'newbie_advertising_view'
    EVENT_WELCOME = 'event_welcome_view'
    COMPLETED_TASKS_WARNING = 'completed_tasks_warning_window'


class LogButtons(str, Enum):
    SKIP = 'skip_button'
    CONTINUE = 'continue_button'
    OK = 'ok_button'
    APPLY = 'apply_button'
    CLOSE = 'close_button'
    QUIT = 'quit_button'
    BATTLE = 'battle_button'
    RESTART_BATTLE = 'restart_battle_button'
    INFO = 'info_button'
    SELECT = 'select_button'
    GARAGE = 'garage_button'
    SETTINGS = 'settings_button'
    HELP = 'help_button'
    TAB = 'tab'
    SUBMIT = 'submit_button'
    ABOUT = 'about_button'
    TAB_SECTION = 'tab_section'


class LogActions(str, Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    AUTO_SELECT = 'auto_select'
    SHOW = 'show'
    PLAY = 'play'
    WATCHED = 'watched'
    GAME_LOADING_CLOSE = 'game_loading_close'
    TOOLTIP_SHOWN = 'tooltip_shown'


class LogBattleResultStats(str, Enum):
    WIN = 'win'
    LOST = 'lost'
