# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/notification/listeners.py
from functools import partial
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_BOND_EQUIPMENT_REMINDER_SHOWN_TIMESTAMP, COMP7_LAST_SEASON_WITH_SEEN_REWARD
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import hasAvailableWeeklyQuestsOfferGiftTokens
from comp7.gui.impl.lobby.rewards_screen import TokensRewardsView
from comp7.gui.impl.lobby.rewards_selection_screen import Comp7RewardsSelectionView
from comp7.notification.decorators import Comp7BondEquipmentDecorator
from frameworks.wulf import ViewStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from notification.decorators import MessageDecorator
from notification.listeners import BaseReminderListener
from notification.settings import NOTIFICATION_TYPE, NotificationData
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.impl import IGuiLoader

class Comp7OfferTokenListener(BaseReminderListener, Notifiable):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __TYPE = NOTIFICATION_TYPE.COMP7_OFFER_TOKENS
    __ENTITY_ID = 0
    __TEMPLATE = 'BondEquipmentChoosingMessage'
    __noNotifyViewTypes = (Comp7RewardsSelectionView, TokensRewardsView)

    def __init__(self):
        super(Comp7OfferTokenListener, self).__init__(self.__TYPE, self.__ENTITY_ID)
        self.__isNoNotifyViewOpen = False

    def start(self, model):
        result = super(Comp7OfferTokenListener, self).start(model)
        if result:
            self.__comp7Controller.onComp7ConfigChanged += self.__onComp7ConfigChanged
            if self.__guiLoader.windowsManager is not None:
                self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
            g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
            self.__tryNotify()
        return result

    def stop(self):
        super(Comp7OfferTokenListener, self).stop()
        self.__comp7Controller.onComp7ConfigChanged -= self.__onComp7ConfigChanged
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.clearNotification()
        return

    def _createNotificationData(self, priority, **__):
        title = backport.text(R.strings.messenger.serviceChannelMessages.bondEquipmentChoosing())
        data = {'title': title}
        return NotificationData(self._getNotificationId(), data, priority, None)

    def _createDecorator(self, data):
        return Comp7BondEquipmentDecorator(data.entityID, self._getNotificationType(), data.savedData, self._model(), self.__TEMPLATE, data.priorityLevel)

    def __onTokensUpdate(self, *_):
        self.__tryNotify()

    def __onComp7ConfigChanged(self, *_):
        self.__tryNotify()

    def __onViewStatusChanged(self, viewID, status):
        if status == ViewStatus.CREATED:
            view = self.__guiLoader.windowsManager.getView(viewID)
            if any((isinstance(view, viewType) for viewType in self.__noNotifyViewTypes)):
                self.__isNoNotifyViewOpen = True
                view.setNoNotifyViewClosedCallback(self.__noNotifyViewClosedCallback)

    def __tryNotify(self):
        self.clearNotification()
        if not hasAvailableWeeklyQuestsOfferGiftTokens():
            self._removeNotification()
            return
        currentSeason = self.__comp7Controller.getActualSeasonNumber()
        lastShownSeason = AccountSettings.getNotifications(COMP7_LAST_SEASON_WITH_SEEN_REWARD)
        if currentSeason != lastShownSeason or self.__isNoNotifyViewOpen:
            return
        notificationTimes = self.__comp7Controller.remainingOfferTokensNotifications
        if not notificationTimes:
            return
        currentTimestamp = time_utils.getServerUTCTime()
        if currentTimestamp < notificationTimes[0]:
            self.__addNotifier(notificationTimes[0])
            return
        lastShownTime = AccountSettings.getNotifications(COMP7_BOND_EQUIPMENT_REMINDER_SHOWN_TIMESTAMP) or 0
        potentialNotifications = (notificationTime for notificationTime in notificationTimes if currentTimestamp >= notificationTime)
        shouldNotify = next((notificationTime for notificationTime in potentialNotifications if lastShownTime < notificationTime), False)
        if not shouldNotify:
            for notificationTime in notificationTimes:
                if notificationTime > currentTimestamp:
                    self.__addNotifier(notificationTime)
                    return

        if self._notify(priority=NotificationPriorityLevel.MEDIUM):
            AccountSettings.setNotifications(COMP7_BOND_EQUIPMENT_REMINDER_SHOWN_TIMESTAMP, currentTimestamp)

    def __addNotifier(self, notificationTime):
        notificator = SimpleNotifier(partial(self.__getTimeToStart, notificationTime), self.__tryNotify)
        self.addNotificator(notificator)
        self.startNotification()

    def __getTimeToStart(self, startDate):
        return startDate - time_utils.getServerUTCTime()

    def __noNotifyViewClosedCallback(self):
        self.__isNoNotifyViewOpen = False
        self.__tryNotify()
