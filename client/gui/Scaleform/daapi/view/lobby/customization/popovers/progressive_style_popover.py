# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/popovers/progressive_style_popover.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import DisjunctionCarouselFilter, FilterAliases
from gui.Scaleform.daapi.view.lobby.customization.popovers import C11nPopoverItemData, orderKey
from gui.Scaleform.daapi.view.lobby.customization.shared import getCurrentVehicleAvailableRegionsMap, fitOutfit, ITEM_TYPE_TO_SLOT_TYPE, removePartsFromOutfit
from gui.Scaleform.daapi.view.meta.CustomizationProgressiveKitPopoverMeta import CustomizationProgressiveKitPopoverMeta
from gui.customization.shared import SEASONS_ORDER, SEASON_TYPE_TO_NAME, EDITABLE_STYLE_IRREMOVABLE_TYPES, C11nId, C11N_ITEM_TYPE_MAP
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.c11n_components import getItemSlotType
from items.components.c11n_constants import SeasonType, CustomizationType
from skeletons.gui.customization import ICustomizationService
POPOVER_SEASONS_ORDER = (SeasonType.ALL,) + SEASONS_ORDER

class FilterTypes(object):
    HISTORIC = 1
    NON_HISTORIC = 2
    FANTASTICAL = 3
    LOCKED = 4


class ProgressiveStylePopover(CustomizationProgressiveKitPopoverMeta):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(ProgressiveStylePopover, self).__init__(ctx)
        self.__ctx = None
        self.__style = None
        self.__filters = None
        self.__itemsList = []
        self.__initFilters()
        return

    def onWindowClose(self):
        self.destroy()

    def remove(self, intCD, slotIds, season):
        if C11N_ITEM_TYPE_MAP[slotIds[0].slotType] in CustomizationType.COMMON_TYPES:
            self.__ctx.mode.removeFromSlots(slotIds, season)
            return
        if season == SeasonType.ALL:
            for commonSeason in SeasonType.COMMON_SEASONS:
                self.__ctx.mode.removeFromSlots(slotIds, commonSeason)

        else:
            self.__ctx.mode.removeFromSlots(slotIds, season)

    def removeAll(self):
        if self.__has3DAttachments():
            self.__ctx.mode.removeItemsFromSeason(SeasonType.ALL)
        if self.__style is not None:
            reqCriteria = self.__getFilterReq()
            if not reqCriteria.conditions:
                self.__ctx.returnToStyleMode()
                self.__ctx.mode.removeStyle(self.__style.intCD)
            else:
                for season in SeasonType.COMMON_SEASONS:
                    self.__ctx.mode.removeItemsFromSeason(season=season, filterMethod=self.__getFilterReq())

        return

    def setToDefault(self):
        self.__ctx.mode.clearStyle()

    def onFilterChanged(self, showHistoric, showNonHistoric, showFantastic, showProgressiveLocked):
        self.__filters.update(showHistoric, FilterAliases.HISTORIC)
        self.__filters.update(showNonHistoric, FilterAliases.NON_HISTORIC)
        self.__filters.update(showFantastic, FilterAliases.FANTASTICAL)
        self.__filters.update(showProgressiveLocked, FilterAliases.LOCKED)
        self.__update()

    def _populate(self):
        super(ProgressiveStylePopover, self)._populate()
        self.__ctx = self.__service.getCtx()
        self.__ctx.events.onCacheResync += self.__update
        self.__ctx.events.onSeasonChanged += self.__update
        self.__ctx.events.onItemInstalled += self.__update
        self.__ctx.events.onItemsRemoved += self.__update
        self.__ctx.events.onChangesCanceled += self.__update
        self.__update()

    def _dispose(self):
        if self.__ctx.events is not None:
            self.__ctx.events.onChangesCanceled -= self.__update
            self.__ctx.events.onItemsRemoved -= self.__update
            self.__ctx.events.onItemInstalled -= self.__update
            self.__ctx.events.onSeasonChanged -= self.__update
            self.__ctx.events.onCacheResync -= self.__update
        self.__style = None
        self.__ctx = None
        super(ProgressiveStylePopover, self)._dispose()
        return

    def __update(self, *_):
        outfit = self.__ctx.mode.currentOutfit
        self.__style = self.__service.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id) if outfit.id else None
        if self.__style is not None and (not self.__style.isEditable or not self.__style.isQuestsProgression):
            self.destroy()
        self.__itemsList = self.__buildList()
        self.as_setItemsS({'items': self.__itemsList})
        self.__setHeader()
        self.__setClearMessage()
        self.as_setDefaultButtonEnabledS(self.__hasIsRemovable())
        return

    def __setHeader(self):
        if [ pItem for pItem in self.__ctx.getPurchaseItems() if pItem.item.itemTypeID == GUI_ITEM_TYPE.ATTACHMENT ]:
            header = backport.text(R.strings.vehicle_customization.customization.kitPopover.title.summary())
        elif self.__style is None:
            header = backport.text(R.strings.vehicle_customization.customization.kitPopover.title.items())
        else:
            header = backport.text(R.strings.vehicle_customization.customization.progressiveKitPopover.title(), value=self.__style.userName)
        self.as_setHeaderS(text_styles.highTitle(header))
        return

    def __setClearMessage(self):
        if self.__style is None or len(self.__itemsList) <= len(SeasonType.COMMON_SEASONS):
            clearMsgResId = R.strings.vehicle_customization.customization.itemsPopover.message.clearFiltered
            clearMessage = text_styles.main(backport.text(clearMsgResId()))
        else:
            clearMessage = ''
        self.as_showClearMessageS(clearMessage)
        return

    def __buildList(self):
        data = []
        if self.__style is None:
            return data
        else:
            vehicleDescriptor = g_currentVehicle.item.descriptor
            purchaseItems = self.__ctx.getPurchaseItems()
            req = self.__getFilterReq()
            filteredItems = [ pItem for pItem in purchaseItems if req(pItem.item) ]
            seasonPurchaseItems = {season:[] for season in SeasonType.REGULAR}
            for pItem in filteredItems:
                if pItem.group not in SeasonType.REGULAR:
                    continue
                seasonPurchaseItems[pItem.group].append(pItem)

            availableRegionsMap = getCurrentVehicleAvailableRegionsMap()
            for season in POPOVER_SEASONS_ORDER:
                seasonGroupVO = self.__getSeasonGroupVO(season)
                itemsData = self.__getSeasonItemsData(season, seasonPurchaseItems[season], availableRegionsMap, vehicleDescriptor)
                if itemsData:
                    data.append(seasonGroupVO)
                    data.extend(itemsData)

            return data

    def __getSeasonItemsData(self, season, purchaseItems, availableRegionsMap, vehicleDescriptor):
        itemData = {}
        for pItem in purchaseItems:
            item = pItem.item
            if item.isHiddenInUI():
                continue
            sType = getItemSlotType(item.descriptor)
            key = (pItem.item.intCD, pItem.isFromInventory)
            if key not in itemData:
                isBase = not pItem.isEdited
                if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
                    isRemovable = False
                elif sType in self.__style.changeableSlotTypes or item.itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
                    if isBase:
                        isRemovable = False
                    elif item.itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
                        if bool(self.__style.getDependenciesIntCDs()) and item.itemTypeID != GUI_ITEM_TYPE.CAMOUFLAGE:
                            isRemovable = False
                        else:
                            isRemovable = True
                    else:
                        isRemovable = True
                else:
                    isRemovable = False
                itemData[key] = C11nPopoverItemData(item=item, season=season, isBase=isBase, isRemovable=isRemovable, isRemoved=False, isFromInventory=pItem.isFromInventory)
            slotId = C11nId(pItem.areaID, pItem.slotType, pItem.regionIdx)
            itemData[key].slotsIds.append(slotId._asdict())

        baseOutfit = self.__getBaseOutfit(season, vehicleDescriptor.makeCompactDescr())
        fitOutfit(baseOutfit, availableRegionsMap)
        nationalEmblemItem = self.__service.getItemByID(GUI_ITEM_TYPE.EMBLEM, vehicleDescriptor.type.defaultPlayerEmblemID)
        showStyle = False
        nationalEmblemDetected = False
        otherDetected = False
        req = self.__getFilterReq()
        for intCD, _, regionIdx, container, _ in baseOutfit.itemsFull():
            item = self.__service.getItemByCD(intCD)
            if not req(item):
                continue
            if item.isHiddenInUI():
                continue
            else:
                showStyle = False
            if not nationalEmblemDetected and intCD == nationalEmblemItem.intCD:
                nationalEmblemDetected = True
            elif not otherDetected and intCD != nationalEmblemItem.intCD:
                otherDetected = True
            key = (intCD, True)
            if key not in itemData:
                itemData[key] = C11nPopoverItemData(item=item, season=season, isBase=True, isRemoved=True, isFromInventory=True)
            if itemData[key].isRemoved:
                areaId = container.getAreaID()
                slotType = ITEM_TYPE_TO_SLOT_TYPE[item.itemTypeID]
                slotId = C11nId(areaId, slotType, regionIdx)
                itemData[key].slotsIds.append(slotId._asdict())

        if nationalEmblemDetected and not otherDetected:
            showStyle = True
            key = (nationalEmblemItem.intCD, True)
            itemData.pop(key)
        if showStyle:
            key = (self.__style.intCD, True)
            itemData[key] = C11nPopoverItemData(item=self.__style, season=season, isBase=True, isRemoved=False, isFromInventory=True)
        data = [ self.__makeItemDataVO(itemData) for itemData in sorted(itemData.values(), key=orderKey) ]
        return data

    def __makeItemDataVO(self, itemData):
        item = itemData.item
        progressionLevel = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
        icon = item.icon if progressionLevel == -1 else item.iconByProgressionLevel(progressionLevel)
        name = text_styles.main(item.userName)
        if itemData.isRemoved or not itemData.isRemovable:
            countLabel = ''
            price = None
        elif itemData.isFromInventory:
            countLabel = text_styles.main('{} '.format(len(itemData.slotsIds)))
            price = None
        else:
            countLabel = text_styles.main('{} x '.format(len(itemData.slotsIds)))
            price = getItemPricesVO(item.buyPrices.itemPrice)[0]
        disabledLabel = backport.text(R.strings.vehicle_customization.popover.style.removed())
        disabledLabel = text_styles.bonusPreviewText(disabledLabel)
        isApplied = itemData.isBase
        progressionLevel = 0
        isLinked = item.isQuestsProgression and item.itemTypeID != GUI_ITEM_TYPE.STYLE
        if isLinked:
            _, progressionLevel = item.getQuestsProgressionInfo()
        isLocked = not item.isUnlockedByToken()
        rarity = item.rarity
        isRare = bool(rarity)
        rarityIconSource = ''
        rarityBackgroundIconSource = ''
        if isRare:
            rarityIconSource = backport.image(R.images.gui.maps.icons.customization.rarity.sign.s20x20.dyn(rarity)())
            rarityBackgroundIconSource = backport.image(R.images.gui.maps.icons.customization.rarity.glow.s104x104.dyn(rarity)())
        itemDataVO = {'id': item.intCD,
         'icon': icon,
         'userName': name,
         'numItems': countLabel,
         'customizationDisplayType': item.customizationDisplayType(),
         'price': price,
         'isApplied': isApplied,
         'isWide': item.isWide(),
         'itemsList': itemData.slotsIds,
         'isDim': item.isDim(),
         'isDisabled': itemData.isRemoved,
         'disabledLabel': disabledLabel,
         'isRemovable': itemData.isRemovable,
         'seasonType': itemData.season,
         'progressionLevel': progressionLevel,
         'isProgressiveLocked': isLocked,
         'rarityIcon': rarityIconSource,
         'rarityBackground': rarityBackgroundIconSource}
        return itemDataVO

    @staticmethod
    def __getSeasonGroupVO(season):
        seasonName = SEASON_TYPE_TO_NAME[season]
        seasonTitle = makeHtmlString('html_templates:lobby/customization/StylePopoverSeasonName', seasonName, ctx={'align': 'CENTER'})
        seasonGroupVO = {'isTitle': True,
         'titleLabel': seasonTitle}
        return seasonGroupVO

    def __initFilters(self):
        self.__filters = DisjunctionCarouselFilter(criteria={FilterAliases.HISTORIC: REQ_CRITERIA.CUSTOMIZATION.HISTORICAL,
         FilterAliases.NON_HISTORIC: REQ_CRITERIA.CUSTOMIZATION.NON_HISTORICAL,
         FilterAliases.FANTASTICAL: REQ_CRITERIA.CUSTOMIZATION.FANTASTICAL,
         FilterAliases.LOCKED: REQ_CRITERIA.CUSTOM(lambda item: not item.isUnlockedByToken())})

    def __getFilterReq(self):
        return self.__filters.criteria if self.__filters.isApplied() else REQ_CRITERIA.EMPTY

    def __hasIsRemovable(self):
        for item in self.__itemsList:
            if item.get('isRemovable'):
                return True

        return False

    def __getBaseOutfit(self, season, vehicleCD=''):
        return self.__ctx.getCommonOutfit() if season == SeasonType.ALL else removePartsFromOutfit(season, self.__style.getOutfit(season, vehicleCD))

    def __has3DAttachments(self):
        for intCD in self.__ctx.getCommonModifiedOutfit().items():
            item = self.__service.getItemByCD(intCD)
            if not item.isHiddenInUI() and item.itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
                return True

        return False
