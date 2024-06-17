# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/settings/views.py
import logging
from constants import ARENA_GUI_TYPE
from gui.Scaleform.framework import COMMON_VIEW_ALIAS
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class VIEW_ALIAS(COMMON_VIEW_ALIAS):
    GOLD_FISH_WINDOW = 'goldFishWindow'
    EULA = 'EULA'
    EULA_FULL = 'EULAFull'
    LOGIN_QUEUE = 'loginQueue'
    LOBBY_HEADER = 'lobbyHeader'
    CUSTOMIZATION_PROPERTIES_SHEET = 'customizationPropertiesSheet'
    CUSTOMIZATION_BOTTOM_PANEL = 'customizationBottomPanel'
    CUSTOMIZATION_INSCRIPTION_CONTROLLER = 'customizationInscriptionController'
    LOBBY_HANGAR = 'hangar'
    LOBBY_STORE = 'store'
    LOBBY_STORAGE = 'storage'
    OVERLAY_WEB_STORE = 'overlayWebStore'
    BROWSER_LOBBY_TOP_SUB = 'overlayBrowserView'
    BROWSER_OVERLAY = 'overlayBrowserFull'
    MAP_BOX_INFO_OVERLAY = 'mapboxInfoOverlay'
    BATTLE_PASS_BROWSER_VIEW = 'battlePassBrowserView'
    BATTLE_PASS_VIDEO_BROWSER_VIEW = 'battlePassVideoBrowserView'
    MANUAL_BROWSER_VIEW = 'ManualBrowserView'
    WEB_VIEW_TRANSPARENT = 'webViewTransparent'
    BLUEPRINTS_EXCHANGE_VIEW = 'blueprintsExchangeView'
    RESOURCE_WELL_BROWSER_VIEW = 'resourceWellBrowserView'
    LOBBY_PROFILE = 'profile'
    LOBBY_MISSIONS = 'missions'
    LOBBY_MISSION_DETAILS = 'missionDetails'
    LOBBY_PERSONAL_MISSION_DETAILS = 'personalMissionDetails'
    LOBBY_PERSONAL_MISSIONS = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATIONS
    PERSONAL_MISSIONS_PAGE = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS
    PERSONAL_MISSIONS_BROWSER_VIEW = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_BROWSER_VIEW_ALIAS
    PROGRESSIVE_ITEMS_BROWSER_VIEW = CUSTOMIZATION_ALIASES.PROGRESSIVE_ITEMS_BROWSER_VIEW
    LOBBY_EVENT_BOARDS_TABLE = 'eventBoardsTable'
    LOBBY_EVENT_BOARDS_AWARDGROUP = 'eventBoardsAwardGroupsLobby'
    LOBBY_EVENT_BOARDS_PAGINATION = 'eventBoardsPaginationLobby'
    LOBBY_EVENT_BOARDS_MAINTENANCE = 'eventBoardsMaintenanceLobby'
    PROFILE_TAB_NAVIGATOR = 'profileTabNavigator'
    PROFILE_SUMMARY_PAGE = 'profileSummaryPage'
    PROFILE_ACHIEVEMENTS_PAGE = 'profileAchievementsPage'
    PROFILE_TOTAL_PAGE = 'profileTotalPage'
    PROFILE_SUMMARY_WINDOW = 'profileSummaryWindow'
    PROFILE_ACHIEVEMENTS_WINDOW = 'profileAchievementsWindow'
    ADVANCED_ACHIEVEMENTS_EARNING_VIEW = 'achievementsEarningView'
    PROFILE_AWARDS = 'profileAwards'
    PROFILE_STATISTICS = 'profileStatistics'
    PROFILE_TECHNIQUE_PAGE = 'profileTechniquePage'
    PROFILE_TECHNIQUE_WINDOW = 'profileTechniqueWindow'
    PROFILE_FORMATIONS_PAGE = 'profileFormationsPage'
    PROFILE_HOF = 'profileHof'
    PROFILE_COLLECTIONS_PAGE = 'profileCollectionsPage'
    PROFILE_PRESTIGE_WIDGET = 'profilePrestigeWidget'
    PROFILE_PRESTIGE_EMBLEM_WIDGET = 'profilePrestigeEmblemWidget'
    GAMMA_WIZARD = 'gammaWizard'
    COLOR_SETTING = 'colorSettings'
    WIKI_VIEW = 'wikiView'
    MANUAL_CHAPTER_VIEW = 'manualChapterView'
    WOT_PLUS_INFO_VIEW = 'wotPlusInfoView'
    TELECOM_RENTAL_VIEW = 'telecomRentalView'
    AMMUNITION_SETUP_VIEW = 'ammunitionSetupView'
    LOBBY_TECHTREE = 'techtree'
    LOBBY_RESEARCH = 'research'
    EXIT_FROM_RESEARCH = 'exitFromResearch'
    LOBBY_BARRACKS = 'barracks'
    LOBBY_CUSTOMIZATION = 'customization'
    LOBBY_MENU = 'lobbyMenu'
    BROWSER = 'browser'
    LOBBY_VEHICLE_MARKER_VIEW = 'lobbyVehicleMarkerView'
    SYSTEM_MESSAGES = 'systemMessages'
    MESSENGER_BAR = 'messengerBar'
    RECRUIT_PARAMS = 'recruitParams'
    NOTIFICATION_LIST_BUTTON = 'notificationListButton'
    CONTACTS_LIST_BUTTON = 'contactsListButton'
    VEHICLE_COMPARE_CART_BUTTON = 'vehicleCompareCartButton'
    TEST_WINDOW = 'testWindow'
    EXCHANGE_WINDOW = 'exchangeWindow'
    EXCHANGE_WINDOW_MODAL = 'exchangeWindowModal'
    PROFILE_WINDOW = 'profileWindow'
    EXCHANGE_XP_WINDOW = 'exchangeXPWindow'
    EXCHANGE_XP_WINDOW_DIALOG_MODAL = 'exchangeXPWindowDialog'
    VEHICLE_BUY_WINDOW = 'vehicleBuyWindow'
    VEHICLE_RESTORE_WINDOW = 'vehicleRestoreWindow'
    BATTLE_QUEUE = 'battleQueue'
    BATTLE_STRONGHOLDS_QUEUE = 'battleStrongholdsQueue'
    BATTLE_LOADING = 'battleLoading'
    LEGAL_INFO_WINDOW = 'legalInfoWindow'
    LEGAL_INFO_TOP_WINDOW = 'legalInfoTopWindow'
    VEHICLE_INFO_WINDOW = 'vehicleInfoWindow'
    MODULE_INFO_WINDOW = 'moduleInfoWindow'
    BOOSTER_INFO_WINDOW = 'boosterInfoWindow'
    GOODIE_INFO_WINDOW = 'goodieInfoWindow'
    VEHICLE_SELL_DIALOG = 'vehicleSellDialog'
    SETTINGS_WINDOW = 'settingsWindow'
    BATTLE_RESULTS = 'battleResults'
    BROWSER_WINDOW = 'browserWindow'
    BROWSER_WINDOW_MODAL = 'browserWindowModal'
    DEMONSTRATOR_WINDOW = 'demonstratorWindow'
    VEHICLE_PREVIEW = 'vehiclePreviewPage'
    STYLE_PREVIEW = 'vehicleStylePreview'
    STYLE_PROGRESSION_PREVIEW = 'vehicleStyleProgressionPreview'
    STYLE_BUYING_PREVIEW = 'vehicleStyleBuyingPreview'
    SHOWCASE_STYLE_BUYING_PREVIEW = 'vehicleShowcaseStyleBuyingPreview'
    IMAGE_VIEW = 'imageView'
    HERO_VEHICLE_PREVIEW = 'heroVehiclePreviewPage'
    TRADE_IN_VEHICLE_PREVIEW = 'tradeInVehiclePreview'
    RENTAL_VEHICLE_PREVIEW = 'rentalVehiclePreview'
    BATTLE_PASS_VEHICLE_PREVIEW = 'battlePassVehiclePreview'
    MARATHON_VEHICLE_PREVIEW = 'marathonVehiclePreview'
    CONFIGURABLE_VEHICLE_PREVIEW = 'configurableVehiclePreview'
    OFFER_GIFT_VEHICLE_PREVIEW = 'offerGiftVehiclePreview'
    RESOURCE_WELL_VEHICLE_PREVIEW = 'resourceWellVehiclePreview'
    RESOURCE_WELL_HERO_VEHICLE_PREVIEW = 'resourceWellHeroVehiclePreview'
    VEHICLE_COMPARE = 'vehicleCompare'
    VEHICLE_COMPARE_MAIN_CONFIGURATOR = 'vehicleCompareConfigurator'
    LOBBY_STRONGHOLD = 'StrongholdView'
    STRONGHOLD_ADS = 'StrongholdAdsView'
    LOBBY_TOURNAMENTS = 'TournamentsView'
    BROWSER_VIEW = 'BrowserView'
    SIMPLE_DIALOG = 'simpleDialog'
    BUTTON_DIALOG = 'buttonDialog'
    CONFIRM_MODULE_DIALOG = 'confirmModuleDialog'
    USE_FREEW_AWARD_SHEET_DIALOG = 'useFreeAwardSheetDialog'
    ICON_DIALOG = 'iconDialog'
    ICON_PRICE_DIALOG = 'iconPriceDialog'
    PM_CONFIRMATION_DIALOG = 'pmConfirmationDialog'
    SYSTEM_MESSAGE_DIALOG = 'systemMessageDialog'
    NOTIFICATIONS_LIST = 'notificationsList'
    CREW_OPERATIONS_POPOVER = 'crewOperationsPopOver'
    BATTLE_TYPE_SELECT_POPOVER = 'battleTypeSelectPopover'
    SQUAD_TYPE_SELECT_POPOVER = 'squadTypeSelectPopover'
    TRADEIN_POPOVER = 'TradeInPopover'
    ACOUSTIC_POPOVER = 'acousticPopover'
    ADVENT_CALENDAR = 'adventCalendar'
    AWARD_WINDOW = 'awardWindow'
    AWARD_WINDOW_MODAL = 'awardWindowModal'
    FITTING_SELECT_POPOVER = 'fittingSelectPopover'
    RESERVE_SELECT_POPOVER = 'reserveSelectPopover'
    OPT_DEVICES_SELECT_POPOVER = 'optDevicesSelectPopover'
    BATTLE_ABILITY_SELECT_POPOVER = 'battleAbilitySelectPopover'
    PACK_ITEM_POPOVER = 'packItemPopover'
    UI_LOGGER_TEST_DIALOG = 'uiLoggerDialog'
    VEH_POST_PROGRESSION = 'vehPostProgression'
    VEH_POST_PROGRESSION_CMP = 'vehPostProgressionCmp'
    CLAN_SUPPLY_INFO_VIEW = 'clanSupplyInfoView'
    MINIMAP_LOBBY = 'minimapLobby'
    MINIMAP_GRID = 'minimapGridLobby'
    MINIMAP_ON_BATTLE_LOADING = 'minimapOnBattleLoading'
    QUESTS_CONTROL = 'questsControl'
    SWITCH_MODE_PANEL = 'switchModePanel'
    TICKER = 'ticker'
    CALENDAR = 'calendar'
    CHANNEL_CAROUSEL = 'channelCarousel'
    G_E_INSPECT_WINDOW = 'GEInspectWindow'
    FREE_X_P_INFO_WINDOW = 'FreeXPInfoWindow'
    RSS_NEWS_FEED = 'rssNewsFeed'
    SERVERS_STATS = 'serverStats'
    PROMO_PREMIUM_IGR_WINDOW = 'PromoPremiumIgrWindow'
    CONFIRM_EXCHANGE_DIALOG = 'ConfirmExchangeDialog'
    CONFIRM_EXCHANGE_DIALOG_MODAL = 'ConfirmExchangeDialogModal'
    QUESTS_SEASON_AWARDS_WINDOW = 'QuestsSeasonAwardsWindow'
    CHECK_BOX_DIALOG = 'CheckBoxDialog'
    REPORT_BUG = 'reportBug'
    SQUAD_PROMO_WINDOW = 'squadPromoWindow'
    BOOSTERS_PANEL = 'boostersPanel'
    MINI_CLIENT_LINKED = 'linkedMiniClientComponent'
    SWITCH_PERIPHERY_WINDOW = 'switchPeripheryWindow'
    SWITCH_PERIPHERY_WINDOW_MODAL = 'switchPeripheryWindowModal'
    CUSTOMIZATION_FILTER_POPOVER = 'CustomizationFilterPopover'
    CUSTOMIZATION_ANCHOR_POPOVER = 'CustomizationAnchorPopover'
    CUSTOMIZATION_ITEMS_POPOVER = 'CustomizationItemsPopover'
    CUSTOMIZATION_PROGRESSIVE_KIT_POPOVER = 'CustomizationProgressiveKitPopover'
    CUSTOMIZATION_EDITED_KIT_POPOVER = 'CustomizationEditedKitPopover'
    CUSTOMIZATION_KIT_POPOVER = 'CustomizationKitPopover'
    CUSTOMIZATION_STYLE_INFO = 'CustomizationStyleInfo'
    TANK_CAROUSEL_FILTER_POPOVER = 'TankCarouselFilterPopover'
    BATTLEPASS_CAROUSEL_FILTER_POPOVER = 'BattlePassCarouselFilterPopover'
    BATTLEROYALE_CAROUSEL_FILTER_POPOVER = 'BattleRoyaleCarouselFilterPopover'
    VEHICLES_FILTER_POPOVER = 'VehiclesFilterPopover'
    STORAGE_VEHICLES_FILTER_POPOVER = 'StorageVehiclesFilterPopover'
    STORAGE_BLUEPRINTS_FILTER_POPOVER = 'StorageBlueprintsFilterPopover'
    STORAGE_VEHICLE_SELECTOR_POPOVER = 'StorageVehicleSelectorPopoverUI'
    CLASSIC_BATTLE_PAGE = 'classicBattlePage'
    DEV_BATTLE_PAGE = 'devBattlePage'
    BADGES_PAGE = 'badgesPage'
    REFERRAL_PROGRAM_WINDOW = 'referralProgramWindow'
    CLAN_NOTIFICATION_WINDOW = 'clanNotificationWindow'
    EPIC_RANDOM_PAGE = 'epicRandomPage'
    EPIC_BATTLE_PAGE = 'epicBattlePage'
    STRONGHOLD_BATTLE_PAGE = 'strongholdBattlePage'
    EVENT_BATTLE_PAGE = 'eventBattlePage'
    RANKED_BATTLE_PAGE = 'rankedBattlePage'
    BATTLE_ROYALE_PAGE = 'battleRoyalePage'
    MISSION_AWARD_WINDOW = 'missionAwardWindow'
    UNBOUND_INJECT_WINDOW = 'unboundInjectWindow'
    BATTLE_PASS_BADGES_DEMO = 'battlePassBadgesDemoView'
    MAPS_TRAINING_PAGE = 'mapsTrainingBattlePage'
    COMP7_BATTLE_PAGE = 'comp7BattlePage'
    WINBACK_BATTLE_PAGE = 'winbackBattlePage'
    INGAME_MENU = 'ingameMenu'
    INGAME_HELP = 'ingameHelp'
    INGAME_DETAILS_HELP = 'ingameDetailsHelp'
    BOTS_MENU = 'botsMenu'
    EVENT_LOADING = 'eventLoading'
    FEEDBACK_DAMAGE_LOG = 'feedbackDamageLog'
    FEEDBACK_BATTLE_EVENTS = 'feedbackBattleEvents'
    FEEDBACK_DAMAGE_INDICATOR = 'feedbackDamageIndicator'
    FEEDBACK_BATTLE_BORDER_MAP = 'feedbackBattleBorderMap'
    FEEDBACK_QUESTS_PROGRESS = 'feedbackQuestsProgress'
    BATTLE_PAGES = (CLASSIC_BATTLE_PAGE,
     DEV_BATTLE_PAGE,
     EVENT_BATTLE_PAGE,
     RANKED_BATTLE_PAGE,
     EPIC_BATTLE_PAGE,
     BATTLE_ROYALE_PAGE,
     WINBACK_BATTLE_PAGE)


VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE = {ARENA_GUI_TYPE.EPIC_RANDOM: VIEW_ALIAS.EPIC_RANDOM_PAGE,
 ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING: VIEW_ALIAS.EPIC_RANDOM_PAGE,
 ARENA_GUI_TYPE.RANKED: VIEW_ALIAS.RANKED_BATTLE_PAGE,
 ARENA_GUI_TYPE.BATTLE_ROYALE: VIEW_ALIAS.BATTLE_ROYALE_PAGE,
 ARENA_GUI_TYPE.EPIC_BATTLE: VIEW_ALIAS.EPIC_BATTLE_PAGE,
 ARENA_GUI_TYPE.EPIC_TRAINING: VIEW_ALIAS.EPIC_BATTLE_PAGE,
 ARENA_GUI_TYPE.EVENT_BATTLES: VIEW_ALIAS.EVENT_BATTLE_PAGE,
 ARENA_GUI_TYPE.MAPS_TRAINING: VIEW_ALIAS.MAPS_TRAINING_PAGE,
 ARENA_GUI_TYPE.SORTIE_2: VIEW_ALIAS.STRONGHOLD_BATTLE_PAGE,
 ARENA_GUI_TYPE.FORT_BATTLE_2: VIEW_ALIAS.STRONGHOLD_BATTLE_PAGE,
 ARENA_GUI_TYPE.COMP7: VIEW_ALIAS.COMP7_BATTLE_PAGE,
 ARENA_GUI_TYPE.TOURNAMENT_COMP7: VIEW_ALIAS.COMP7_BATTLE_PAGE,
 ARENA_GUI_TYPE.TRAINING_COMP7: VIEW_ALIAS.COMP7_BATTLE_PAGE,
 ARENA_GUI_TYPE.WINBACK: VIEW_ALIAS.WINBACK_BATTLE_PAGE}

def addViewBattlePageAliasByArenaGUIType(arenaGuiType, viewAlias, personality):
    if arenaGuiType in VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE:
        raise SoftException('VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE already has arenaGuiType:{guiType}. Personality: {p}'.format(guiType=arenaGuiType, p=personality))
    VIEW_ALIAS.BATTLE_PAGES += (viewAlias,)
    VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE.update({arenaGuiType: viewAlias})
    msg = 'arenaGuiType:{arenaGuiType} was added to VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE. Personality: {p}'.format(arenaGuiType=arenaGuiType, p=personality)
    logging.debug(msg)
