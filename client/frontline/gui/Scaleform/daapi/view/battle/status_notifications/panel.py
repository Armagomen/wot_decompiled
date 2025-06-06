# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/status_notifications/panel.py
import logging
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from frontline.gui.Scaleform.daapi.view.battle.status_notifications import sn_items as frontline_sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
_logger = logging.getLogger(__name__)

class _FrontlineBattleHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_FrontlineBattleHighPriorityGroup, self).__init__((sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN,
         frontline_sn_items.FrontlineDeathZoneDamagingSN,
         frontline_sn_items.FrontlineDeathZoneDangerSN,
         frontline_sn_items.FrontlineDeathZoneWarningSN,
         frontline_sn_items.SectorAirstrikeSN,
         sn_items.UnderFireSN,
         sn_items.FireSN), updateCallback)


class FrontlineStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_FrontlineBattleHighPriorityGroup,
         frontline_sn_items.ResupplyTimerSN,
         sn_items.StunSN,
         frontline_sn_items.FrontlineEnemySmokeSN,
         frontline_sn_items.FrontlineEnemySmokePostEffectSN,
         frontline_sn_items.FrontlineSmokeSN,
         frontline_sn_items.StealthSN,
         frontline_sn_items.StealthInactiveSN,
         frontline_sn_items.FrontlineInspireSN,
         frontline_sn_items.FrontlineInspireCooldownSN,
         frontline_sn_items.FrontlineInspireSourceSN,
         frontline_sn_items.FrontlineInspireInactivationSourceSN,
         frontline_sn_items.FrontlineHealingSN,
         frontline_sn_items.FrontlineHealingCooldownSN,
         frontline_sn_items.FrontlineRepairingSN,
         frontline_sn_items.FrontlineRepairingCooldownSN,
         frontline_sn_items.RecoverySN,
         frontline_sn_items.CaptureBlockSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(FrontlineStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        if BigWorld.player().hasBonusCap(ARENA_BONUS_TYPE_CAPS.LIFT_OVER):
            overturnedIcon = _LINKS.OVERTURNED_GREEN_ICON
            overturnedColor = _COLORS.GREEN
            iconOffsetY = 1
        else:
            overturnedIcon = _LINKS.OVERTURNED_ICON
            overturnedColor = _COLORS.ORANGE
            iconOffsetY = 0
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.DEATH_ZONE, _LINKS.AIRSTRIKE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.DAMAGING_ZONE, _LINKS.AIRSTRIKE_ICON, link, countdownVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.UNDER_FIRE, _LINKS.UNDER_FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.RECOVERY, _LINKS.RECOVERY_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.ORANGE_ZONE, _LINKS.AIRSTRIKE_ICON, link, _COLORS.ORANGE, countdownVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.REPAIRING, _LINKS.RECOVERY_ICON, link)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True, text=INGAME_GUI.STUN_INDICATOR)
        self._addNotificationTimerSetting(data, _TYPES.CAPTURE_BLOCK, _LINKS.BLOCKED_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _TYPES.SMOKE, _LINKS.SMOKE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.DAMAGING_SMOKE, _LINKS.ENEMY_SMOKE_ICON, link, _COLORS.ORANGE)
        self._addNotificationTimerSetting(data, _TYPES.INSPIRE, _LINKS.INSPIRE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.INSPIRE_CD, _LINKS.INSPIRE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.INSPIRE_SOURCE, _LINKS.INSPIRE_SOURCE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.INSPIRE_INACTIVATION_SOURCE, _LINKS.INSPIRE_SOURCE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.HEALING, _LINKS.HEAL_ICON_FRONTLINE, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.HEALING_CD, _LINKS.HEAL_ICON_FRONTLINE, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.REPAIRING, _LINKS.RECOVERY_ZONE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.REPAIRING_CD, _LINKS.RECOVERY_ZONE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.STEALTH_RADAR, _LINKS.STEALTH_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.STEALTH_RADAR_INACTIVE, _LINKS.STEALTH_INACTIVE_ICON, link, _COLORS.GREEN_DISABLED)
        link = _LINKS.RESUPPLY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.RESUPPLY, _LINKS.RESUPPLY_TIMER_UI, link)
        return data
