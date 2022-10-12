# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/subscriptions/subscriptions_controller.py
import logging
import typing

from BWUtil import AsyncReturn
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.products_fetcher.controller import ProductsFetchController, _PlatformProductListParams
from gui.platform.products_fetcher.subscriptions.subscriptions_descriptor import PrimeGamingDescriptor, \
    SubscriptionDescriptor
from helpers import dependency, getClientLanguage
from skeletons.gui.platform.product_fetch_controller import ISubscriptionsFetchController
from skeletons.gui.platform.wgnp_controllers import IWGNPGeneralRequestController
from wg_async import wg_async, wg_await

_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    pass

class PlatformSubscriptionsParams(_PlatformProductListParams):
    storefront = 'player_subscriptions'
    language = getClientLanguage()
    __wgnpCountryController = dependency.descriptor(IWGNPGeneralRequestController)

    @wg_async
    def setCountry(self):
        status = yield wg_await(self.__wgnpCountryController.getAccountCountry())
        if status.typeIs(StatusTypes.ADDED):
            self.country = status.country
        raise AsyncReturn(None)
        return


class SubscriptionFetcherController(ProductsFetchController, ISubscriptionsFetchController):
    platformParams = PlatformSubscriptionsParams
    defaultProductDescriptor = SubscriptionDescriptor
    productIDToDescriptor = {'prime_subscription': PrimeGamingDescriptor}
