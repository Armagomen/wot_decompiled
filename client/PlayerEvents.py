# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PlayerEvents.py
import Event

class _PlayerEvents(object):

    def __init__(self):
        self.onPlayerEntityChanging = Event.Event()
        self.onPlayerEntityChangeCanceled = Event.Event()
        self.isPlayerEntityChanging = True
        self.onAvatarObserverVehicleChanged = Event.Event()
        self.onAccountBecomePlayer = Event.Event()
        self.onAccountBecomeNonPlayer = Event.Event()
        self.onAccountShowGUI = Event.Event()
        self.onAccountShowGUISkipped = Event.Event()
        self.onClientUpdated = Event.Event()
        self.onEnqueued = Event.Event()
        self.onDequeued = Event.Event()
        self.onEnqueueFailure = Event.Event()
        self.onKickedFromQueue = Event.Event()
        self.onPrbDispatcherCreated = Event.Event()
        self.onPrebattleJoined = Event.Event()
        self.onPrebattleLeft = Event.Event()
        self.onPrebattleJoinFailure = Event.Event()
        self.onArenaCreated = Event.Event()
        self.onArenaJoinFailure = Event.Event()
        self.onKickedFromUnitsQueue = Event.Event()
        self.onKickedFromPrebattle = Event.Event()
        self.onKickedFromArena = Event.Event()
        self.onQueueInfoReceived = Event.Event()
        self.onPrebattlesListReceived = Event.Event()
        self.onPrebattleAutoInvitesChanged = Event.Event()
        self.onAccountGlobalRatingChanged = Event.Event()
        self.onPrebattleInvitesChanged = Event.Event()
        self.onPrebattleInvitationsChanged = Event.Event()
        self.onPrebattleInvitationAccepted = Event.Event()
        self.onPrebattleInvitesStatus = Event.Event()
        self.onPrebattleInvitationsError = Event.Event()
        self.onClanMembersListChanged = Event.Event()
        self.onEventsDataChanged = Event.Event()
        self.onPrebattleRosterReceived = Event.Event()
        self.onArenaListReceived = Event.Event()
        self.onServerStatsReceived = Event.Event()
        self.onInventoryResync = Event.Event()
        self.onStatsResync = Event.Event()
        self.onShopResyncStarted = Event.Event()
        self.onShopResync = Event.Event()
        self.onDossiersResync = Event.Event()
        self.onOffersResync = Event.Event()
        self.onEventNotificationsChanged = Event.Event()
        self.onVehicleLockChanged = Event.Event()
        self.onVehicleBecomeElite = Event.Event()
        self.onCenterIsLongDisconnected = Event.Event()
        self.onIGRTypeChanged = Event.Event()
        self.onAvatarBecomePlayer = Event.Event()
        self.onAvatarBecomeNonPlayer = Event.Event()
        self.onArenaPeriodChange = Event.Event()
        self.onAvatarReady = Event.Event()
        self.onBattleResultsReceived = Event.Event()
        self.onAvatarVehicleLeaveWorld = Event.Event()
        self.onLoginQueueNumberReceived = Event.Event()
        self.onKickWhileLoginReceived = Event.Event()
        self.onPeripheryRoutingGroupReceived = Event.Event()
        self.onGuiCacheSyncCompleted = Event.Event()
        self.onPMLocksChanged = Event.Event()
        self.onDailyQuestsInfoChange = Event.Event()
        self.onBootcampEnqueued = Event.Event()
        self.onBootcampStartChoice = Event.Event()
        self.onBootcampAccountMigrationComplete = Event.Event()
        self.onNotification = Event.Event()
        self.onTeamChanged = Event.Event()
        self.onDisconnected = Event.Event()
        self.onShowDevelopmentInfo = Event.Event()
        self.onEntityCheckOutEnqueued = Event.Event()
        self.onRoundFinished = Event.Event()
        self.crosshairPanelInitialized = Event.Event()
        self.onServerReplayEntering = Event.Event()
        self.onServerReplayExiting = Event.Event()
        self.onPlatformBlueprintsConvertSaleLimits = Event.Event()
        self.onCollectPrebattleInvites = Event.Event()
        self.onUpdateSpecBattlesWindow = Event.Event()
        self.onLoadingMilestoneReached = Event.Event()
        self.onConfigModelUpdated = Event.Event()
        self.onShowBattleHint = Event.SafeEvent()
        self.onHideBattleHint = Event.SafeEvent()
        self.onEmptyBattleHintsQueue = Event.SafeEvent()


g_playerEvents = _PlayerEvents()
