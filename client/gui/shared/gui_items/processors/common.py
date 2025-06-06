# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/common.py
import logging
import copy
import time
import BigWorld
from BWUtil import AsyncReturn
from constants import EMPTY_GEOMETRY_ID, PREMIUM_TYPE
from exchange.personal_discounts_helper import getDiscountsRequiredForExchange
from gui import SystemMessages
from gui.customization.shared import validateOutfitComponent
from gui.game_control.exchange_rates_with_discounts import getCurrentTime
from gui.impl.lobby.exchange.exchange_rates_helper import createSystemExchangeNotification
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.notifications import NotificationPriorityLevel
from skeletons.gui.shared import IItemsCache
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles, icons
from gui.shared.gui_items.processors import Processor, makeError, makeSuccess, makeI18nError, makeI18nSuccess, plugins, GroupedRequestProcessor
from gui.shared.money import Money, Currency
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket, IWotPlusController, IEpicBattleMetaGameController, IExchangeRatesWithDiscountsProvider
from wg_async import wg_async, wg_await, await_callback
from shared_utils import first
_logger = logging.getLogger(__name__)

class TankmanBerthsBuyer(Processor):

    def __init__(self, berthsPrice, countPacksBerths):
        super(TankmanBerthsBuyer, self).__init__()
        self.addPlugins([plugins.MoneyValidator(berthsPrice)])
        self.berthsPrice = berthsPrice
        self.countPacksBerths = countPacksBerths

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='buy_tankmen_berths/{}'.format(errStr), defaultSysMsgKey='buy_tankmen_berths/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='buy_tankmen_berths/success', money=formatPrice(self.berthsPrice, useStyle=True, justValue=True), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        _logger.debug('Make server request to buy tankman berths')
        BigWorld.player().stats.buyBerths(self.countPacksBerths, lambda code: self._response(code, callback))


class PremiumAccountBuyer(Processor):

    def __init__(self, period, price, arenaUniqueID=0, withoutBenefits=False, requireConfirm=True):
        self.wasPremium = self.itemsCache.items.stats.isPremium
        plugList = [plugins.MoneyValidator(Money(gold=price))]
        if requireConfirm:
            plugList.insert(0, self.__getConfirmator(withoutBenefits, period, price))
        super(PremiumAccountBuyer, self).__init__(plugList)
        self.premiumPrice = price
        self.period = period
        self.arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='premium/{}'.format(errStr), defaultSysMsgKey='premium/server_error', auxData={'errStr': errStr}, period=self.period)

    def _successHandler(self, code, ctx=None):
        localKey = 'premium/continueSuccess' if self.wasPremium else 'premium/buyingSuccess'
        return makeI18nSuccess(sysMsgKey=localKey, period=self.period, money=formatGoldPrice(self.premiumPrice), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        _logger.debug('Make server request to buy premium account, %s, %s', self.period, self.premiumPrice)
        BigWorld.player().stats.upgradeToPremium(self.period, self.arenaUniqueID, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def __getConfirmator(self, withoutBenefits, period, price):
        if withoutBenefits:
            return plugins.HtmlMessageConfirmator('buyPremWithoutBenefitsConfirmation', 'html_templates:lobby/dialogs', 'confirmBuyPremWithoutBenefeits', {'days': text_styles.stats(period),
             Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})
        localKey = 'premiumContinueConfirmation' if self.wasPremium else 'premiumBuyConfirmation'
        return plugins.MessageConfirmator(localKey, ctx={'days': text_styles.stats(period),
         Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})


class GoldToCreditsExchanger(Processor):
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, gold, withConfirm=True):
        rate = self.__exchangeRatesProvider.goldToCredits
        self.gold, self.baseRate = gold, rate.unlimitedDiscountRate
        allDiscounts = copy.deepcopy(rate.allPersonalLimitedDiscounts)
        curTime = getCurrentTime()
        self.discounts = getDiscountsRequiredForExchange(allDiscounts, self.gold, curTime) if allDiscounts else {}
        self.credits = rate.calculateExchange(self.gold)
        super(GoldToCreditsExchanger, self).__init__()
        if withConfirm:
            self.addPlugin(plugins.HtmlMessageConfirmator('exchangeGoldConfirmation', 'html_templates:lobby/dialogs', 'confirmExchange', {'primaryCurrencyAmount': backport.getGoldFormat(self.gold),
             'resultCurrencyAmount': backport.getIntegralFormat(self.credits)}))
        self.addPlugins([plugins.MoneyValidator(Money(gold=self.gold)), plugins.ExchangeValidator(self.gold), plugins.ExchangeValidator(self.credits)])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='exchange/{}'.format(errStr), defaultSysMsgKey='exchange/server_error', gold=int(self.gold))

    def _successHandler(self, code, ctx=None):
        rate = self.__exchangeRatesProvider.goldToCredits
        isUnlimDiscount = True if rate.unlimitedDiscountInfo is not None and rate.unlimitedDiscountInfo.isPersonal else False
        return createSystemExchangeNotification(discounts=self.discounts, goldAmount=self.gold, defaultRate=rate.defaultRate, baseRate=self.baseRate, isPersonalUnlimRate=isUnlimDiscount, exchangeType=rate.getExchangeRateName)

    def _request(self, callback):
        _logger.debug('Make server request to exchange gold to credits')
        BigWorld.player().stats.exchange(self.gold, self.credits, lambda code: self._response(code, callback))


class FreeXPExchanger(Processor):
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, xp, vehiclesCD):
        rate = self.__exchangeRatesProvider.freeXpTranslation
        self.xp, self.baseRate, self.vehiclesCD = xp, rate.unlimitedDiscountRate, vehiclesCD
        self.gold = rate.calculateGoldToExchange(self.xp)
        allDiscounts = copy.deepcopy(rate.allPersonalLimitedDiscounts)
        curTime = getCurrentTime()
        self.discounts = getDiscountsRequiredForExchange(allDiscounts, self.gold, curTime) if allDiscounts else {}
        super(FreeXPExchanger, self).__init__(plugins=(self.__makeConfirmator(),
         plugins.MoneyValidator(Money(gold=self.gold)),
         plugins.ExchangeValidator(self.gold),
         plugins.ExchangeValidator(self.xp),
         plugins.EliteVehiclesValidator(self.vehiclesCD)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='exchangeXP/{}'.format(errStr), defaultSysMsgKey='exchangeXP/server_error', xp=backport.getIntegralFormat(self.xp))

    def _successHandler(self, code, ctx=None):
        rate = self.__exchangeRatesProvider.freeXpTranslation
        isUnlimDiscount = True if rate.unlimitedDiscountInfo is not None and rate.unlimitedDiscountInfo.isPersonal else False
        return createSystemExchangeNotification(discounts=self.discounts, goldAmount=self.gold, defaultRate=rate.defaultRate, baseRate=self.baseRate, isPersonalUnlimRate=isUnlimDiscount, exchangeType=rate.getExchangeRateName)

    def _request(self, callback):
        _logger.debug('Make server request to exchange xp for credits')
        BigWorld.player().stats.convertToFreeXP(self.vehiclesCD, self.xp, self.gold, lambda code: self._response(code, callback))

    def __makeConfirmator(self):
        extra = {'resultCurrencyAmount': backport.getIntegralFormat(self.xp),
         'primaryCurrencyAmount': backport.getGoldFormat(self.gold)}
        return plugins.HtmlMessageConfirmator('exchangeXPConfirmation', 'html_templates:lobby/dialogs', 'confirmExchangeXP', extra, sourceKey='XP_EXCHANGE_FOR_GOLD')


class BattleResultsGetter(Processor):

    def __init__(self, arenaUniqueID):
        super(BattleResultsGetter, self).__init__()
        self.__arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        _logger.warning('Error on server request to get battle results: %s, %s, %s, %s', self.__arenaUniqueID, code, errStr, ctx)
        return makeError()

    def _successHandler(self, code, ctx=None):
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to get battle results')
        BigWorld.player().battleResultsCache.get(self.__arenaUniqueID, lambda code, battleResults: self._response(code, callback, ctx=battleResults))


class OutfitApplier(Processor):

    def __init__(self, vehicle, outfitData):
        super(OutfitApplier, self).__init__((plugins.CustomizationPurchaseValidator(outfitData),))
        self.vehicle = vehicle
        self.outfitData = outfitData

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        _logger.debug('Make server request to put on outfit on vehicle %s, outfitData %s', self.vehicle.invID, self.outfitData)
        requestData = []
        for outfit, season in self.outfitData:
            component = outfit.pack()
            validateOutfitComponent(self.vehicle.descriptor, component)
            requestData.append((component.makeCompDescr(), season))

        BigWorld.player().shop.buyAndEquipOutfit(self.vehicle.invID, requestData, lambda code: self._response(code, callback))


class CustomizationsBuyer(Processor):

    def __init__(self, vehicle, item, count):
        super(CustomizationsBuyer, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        invID = self.vehicle.invID if self.vehicle else 0
        _logger.debug('Make server request to buy customizations on vehicle %s: %s count %s', invID, self.item, self.count)
        BigWorld.player().shop.buyCustomizations(invID, {self.item.intCD: self.count}, lambda code: self._response(code, callback))

    def _getTotalPrice(self):
        buyPrice = self.item.buyPrices.itemPrice.price
        if not buyPrice:
            _logger.error('Incorrect attempt to buy item %s', self.item)
        return buyPrice * self.count

    def _getMsgCtx(self):
        styleItemType = backport.text(R.strings.item_types.customization.style())
        return {'itemType': styleItemType if self.item.itemTypeID == GUI_ITEM_TYPE.STYLE else self.item.userType,
         'itemName': self.item.userName,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice(), useStyle=True)}

    def _successHandler(self, code, ctx=None):
        currency = self.item.buyPrices.itemPrice.price.getCurrency(byWeight=True)
        sysMsgType = CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.PurchaseForGold)
        msgCtx = self._getMsgCtx()
        if self.count == 1:
            msg = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customization.buyOne(), **msgCtx)
        else:
            msgCtx = {'items': backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customization.item(), **msgCtx) + '.',
             'money': msgCtx['money']}
            msg = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customization.buyMany(), **msgCtx)
        SystemMessages.pushMessage(msg, type=sysMsgType)
        return makeSuccess(auxData=ctx)


class CustomizationsSeller(Processor):

    def __init__(self, vehicle, item, count=1):
        super(CustomizationsSeller, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _getTotalPrice(self):
        sellPrice = self.item.sellPrices.itemPrice.price
        if not sellPrice:
            _logger.error('Attempt to sell item %s that is not sold.', self.item)
        return sellPrice * self.count

    def _getMsgCtx(self):
        styleItemType = backport.text(R.strings.item_types.customization.style())
        return {'itemType': styleItemType if self.item.itemTypeID == GUI_ITEM_TYPE.STYLE else self.item.userType,
         'itemName': self.item.userName,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice()),
         'priority': NotificationPriorityLevel.MEDIUM}

    def _successHandler(self, code, ctx=None):
        messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_SELL
        if ctx is not None and 'count' in ctx:
            self.count = ctx['count']
        if self.count > 0:
            SystemMessages.pushI18nMessage(messageType, type=SM_TYPE.Selling, **self._getMsgCtx())
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        vehicleCD = self.vehicle.intCD if self.vehicle is not None else 0
        _logger.debug('Make server request to sell customizations on vehicle %s, item %s, count %s', vehicleCD, self.item, self.count)
        BigWorld.player().shop.sellCustomizations(vehicleCD, self.item.intCD, self.count, lambda code, ctx={}: self._response(code, callback, ctx=ctx))
        return


class BadgesSelector(Processor):

    def __init__(self, badges=None):
        if badges is None:
            plugs = ()
            badges = ()
        else:
            plugs = (plugins.BadgesValidator(badges),)
        super(BadgesSelector, self).__init__(plugs)
        self.__badges = badges
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to select badges %s', self.__badges)
        BigWorld.player().badges.selectBadges(self.__badges, lambda resID, code, errStr: self._response(code, callback, errStr))


class ConvertBlueprintFragmentProcessor(Processor):

    def __init__(self, vehicleCD, count, fragmentPosition, usedNationalFragments):
        super(ConvertBlueprintFragmentProcessor, self).__init__()
        self.__vehicleCD = vehicleCD
        self.__position = fragmentPosition
        self.__count = count
        self.__usedNationalFragments = usedNationalFragments

    def _request(self, callback):
        BigWorld.player().blueprints.convertBlueprintFragment(self.__vehicleCD, self.__position, self.__count, self.__usedNationalFragments, lambda code: self._response(code, callback))


class _MapsBlackListSelector(Processor):

    def __init__(self, selectedMaps=None):
        super(_MapsBlackListSelector, self).__init__()
        if selectedMaps is None:
            selectedMaps = ()
        self.__selectedMaps = selectedMaps
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        itemsCache = dependency.instance(IItemsCache)
        wotPLusController = dependency.instance(IWotPlusController)
        isPremiumActive = itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        isWotPlusActive = wotPLusController.isEnabled()
        if not isPremiumActive and not isWotPlusActive:
            return makeI18nSuccess(sysMsgKey='{}/success/noSubscriptions'.format(self._getMessagePrefix()))
        if isPremiumActive and not isWotPlusActive:
            return makeI18nSuccess(sysMsgKey='{}/success/premium'.format(self._getMessagePrefix()))
        return makeI18nSuccess(sysMsgKey='{}/success/wotPlus'.format(self._getMessagePrefix())) if not isPremiumActive and isWotPlusActive else makeI18nSuccess(sysMsgKey='{}/success'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to select black maps %r', self.__selectedMaps)
        BigWorld.player().stats.setMapsBlackList(self.__selectedMaps, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getLayout(self):
        return [ mapID for mapID, _ in self.itemsCache.items.stats.getMapsBlackList() ]


class MapsBlackListSetter(_MapsBlackListSelector):

    def __init__(self, selectedMapID):
        layout = self._getLayout()
        wasInserted = False
        for idx, mapID in enumerate(layout):
            if mapID == EMPTY_GEOMETRY_ID:
                layout[idx] = selectedMapID
                wasInserted = True
                break

        if not wasInserted:
            layout.append(selectedMapID)
        super(MapsBlackListSetter, self).__init__(layout)


class MapsBlackListRemover(_MapsBlackListSelector):

    def __init__(self, removeMapID):
        layout = self._getLayout()
        if removeMapID in layout:
            layout[layout.index(removeMapID)] = EMPTY_GEOMETRY_ID
        else:
            _logger.error('Cannot remove mapID %d from layout %r', removeMapID, layout)
        super(MapsBlackListRemover, self).__init__(layout)


class MapsBlackListChanger(_MapsBlackListSelector):

    def __init__(self, srcMapID, destMapID):
        layout = self._getLayout()
        if srcMapID in layout:
            layout[layout.index(srcMapID)] = destMapID
        else:
            _logger.error('Cannot change srcMapID %d from layout %r', srcMapID, layout)
        super(MapsBlackListChanger, self).__init__(layout)


class PremiumBonusApplier(Processor):

    def __init__(self, arenaUniqueID=None, vehTypeCompDescr=None):
        super(PremiumBonusApplier, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__vehTypeCompDescr = vehTypeCompDescr

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to apply premium XP bonus %d', self.__arenaUniqueID)
        BigWorld.player().shop.applyPremiumXPBonus(self.__arenaUniqueID, self.__vehTypeCompDescr, lambda resID, code, errStr: self._response(code, callback, errStr))


class UseCrewBookProcessor(GroupedRequestProcessor):

    def __init__(self, crewBookCD, crewBookCount, vehInvID, tmanInvID, groupID=0, groupSize=1):
        self.__crewBookCD = crewBookCD
        self.__crewBookCount = crewBookCount
        self.__vehInvID = vehInvID
        self.__tmanInvID = tmanInvID
        super(UseCrewBookProcessor, self).__init__(BigWorld.player().inventory.useCrewBook, crewBookCD, crewBookCount, vehInvID, tmanInvID, groupID=groupID, groupSize=groupSize)

    def _makeSuccessData(self, *args, **kwargs):
        itemsCache = dependency.instance(IItemsCache)
        auxData = []
        for item in iter(kwargs.get('ctx', [])):
            if item.itemCount == 1:
                auxData.append(makeI18nSuccess(sysMsgKey='crewBooksNotification/bookUsed', name=itemsCache.items.getItemByCD(item.itemID).userName))
                continue
            auxData.append(makeI18nSuccess(sysMsgKey='crewBooksNotification/booksUsed', name=itemsCache.items.getItemByCD(item.itemID).userName, count=item.itemCount))

        return auxData

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='crewBooksNotification/success', auxData=self._makeSuccessData(ctx=ctx))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='crewBooks/{}'.format(errStr), auxData=self._makeErrorData(errStr), defaultSysMsgKey='crewBooks/failed')


class ClaimRewardForPostProgression(Processor):

    def __init__(self, xppToConvert):
        super(ClaimRewardForPostProgression, self).__init__()
        self.addPlugins([plugins.ExperiencePostProgressionValidator(xppToConvert)])

    def _request(self, callback):
        _logger.debug('Make server request to claim reward for post progression.')
        BigWorld.player().inventory.claimRewardForPostProgression(0, lambda code, ctx: self._response(code, callback, ctx=ctx))

    def _successHandler(self, code, ctx=None):
        crewBookID = ctx.get('crewBookID')
        itemsCache = dependency.instance(IItemsCache)
        crewBook = first(itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.ID(crewBookID)).values())
        formatedDate = str(time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time())))
        text = backport.text(R.strings.system_messages.post_progression.success(), book_name=crewBook.getName().strip(), amount=str(int(ctx.get('count'))), at=formatedDate)
        return makeI18nSuccess(sysMsgKey=text, type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, auxData={'header': backport.text(R.strings.system_messages.post_progression.success.title())})

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey=backport.text(R.strings.system_messages.post_progression.server_error()), type=SM_TYPE.Error)


class FillingAllUntrainedPerksProcessor(Processor):

    def __init__(self, fillInBarracks):
        super(FillingAllUntrainedPerksProcessor, self).__init__()
        self._fillInBarracks = fillInBarracks

    def _request(self, callback):
        _logger.debug('Make server request to fill untrained perks for all crew members.')
        BigWorld.player().inventory.fillAllTankmenSkills(self._fillInBarracks, lambda resID, code, errStr: self._response(code, callback, errStr))

    def _successHandler(self, code, ctx=None):
        return makeI18nError(sysMsgKey=backport.text(R.strings.system_messages.filling_untrained_perks.success()), type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey=backport.text(R.strings.system_messages.filling_untrained_perks.server_error()), type=SM_TYPE.Error)


class VehicleChangeNation(Processor):
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, cvh, nvh):
        super(VehicleChangeNation, self).__init__()
        self._cvh = cvh
        self._nvh = nvh

    def _request(self, callback):
        BigWorld.player().inventory.switchNation(self._cvh.name, self._nvh.name, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey=backport.text(R.strings.system_messages.nation_change.dyn(errStr)()), defaultSysMsgKey=backport.text(R.strings.system_messages.nation_change.error()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=backport.text(R.strings.system_messages.nation_change.success()), veh_name=self._cvh.userName)


class BuyBattleAbilitiesProcessor(Processor):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, skillIds):
        super(BuyBattleAbilitiesProcessor, self).__init__()
        self.__skillIds = skillIds

    @wg_async
    def _request(self, callback):
        errorCode = yield wg_await(self._requestChain())
        callback(makeError(errorCode) if errorCode else makeSuccess())

    @wg_async
    def _requestChain(self):
        for skillId in self.__skillIds:
            _, errorCode = yield await_callback(self.__epicMetaGameCtrl.increaseSkillLevel)(skillId)
            if errorCode:
                raise AsyncReturn(errorCode)

        raise AsyncReturn(None)
        return
