# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/base/views_loaders.py
import logging
from typing import TYPE_CHECKING
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.customization.constants import CustomizationModes
from gui.impl import backport
from gui.impl.gen import R
from gui.lootbox_system.base.common import ViewID, Views, getTextResource
from gui.lootbox_system.base.utils import getIntroVideoUrl, getIsShowIntro, getShopOverlayUrl, getVehicleForStyle
from gui.shared.event_dispatcher import hideVehiclePreview, selectVehicleInHangar, showBrowserOverlayView, showStylePreview, showVehiclePreviewWithoutBottomPanel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)

def showIntro(eventName):
    if getIsShowIntro(eventName):
        showBrowserOverlayView(getIntroVideoUrl(eventName), VIEW_ALIAS.LOOT_BOXES_INTRO_BROWSER_VIEW)


def showMain(eventName, subViewID=None, *args, **kwargs):
    from gui.impl.lobby.lootbox_system.base.main_view import MainWindow
    window = findActiveWindow(R.views.lobby.lootbox_system.MainView())
    if window is not None:
        window.switchToSubView(subViewID, eventName=eventName, *args, **kwargs)
        return
    else:
        window = MainWindow(subViewID, eventName=eventName, *args, **kwargs)
        window.load()
        return


def showInfo(eventName, previousWindow=None, category='', backCallback=None):
    from gui.impl.lobby.lootbox_system.base.info_page import InfoPageWindow
    window = findActiveWindow(R.views.lobby.lootbox_system.InfoPage())
    if window is None:
        window = InfoPageWindow(previousWindow=previousWindow, category=category, eventName=eventName, backCallback=backCallback)
        window.load()
    return


def showAutoOpen(eventName, rewards, boxes):
    from gui.impl.lobby.lootbox_system.base.auto_open_view import AutoOpenWindow
    window = AutoOpenWindow(eventName, rewards, boxes)
    window.load()


@dependency.replace_none_kwargs(customization=ICustomizationService, itemsCache=IItemsCache)
def showItemPreview(itemType, itemID, styleID, eventName, backCallback=None, customization=None, itemsCache=None):
    backLabel = backport.text(getTextResource('preview/backLabel'.split('/'), eventName)())
    if itemType == 'vehicles':
        vehicle = itemsCache.items.getItemByCD(itemID)
        if vehicle.isInInventory:
            window = findActiveWindow(R.views.lobby.lootbox_system.MainView())
            if window is not None:
                window.destroyWindow()
            selectVehicleInHangar(itemID, loadHangar=True)
        else:
            ClientSelectableCameraObject.switchCamera()
            style = customization.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID else None
            showVehiclePreviewWithoutBottomPanel(itemID, backCallback=backCallback, backBtnLabel=backLabel, style=style)
    elif itemType == 'customizations':
        style = customization.getItemByID(GUI_ITEM_TYPE.STYLE, itemID)
        if style.is3D:
            showCustomizationHangar(style, previewBackCb=backCallback, backBtnLabel=backLabel)
        else:
            showVehicleStylePreview(style, previewBackCb=backCallback, backBtnLabel=backLabel)
    else:
        _logger.error('Type "%s" is not supported for preview', itemType)
    return


def hideItemPreview():
    hideVehiclePreview(back=False, close=True)


@dependency.replace_none_kwargs(customization=ICustomizationService, itemsCache=IItemsCache)
def showCustomizationHangar(style, previewBackCb=None, backBtnLabel=None, itemsCache=None, customization=None):

    def _callback():
        if style is not None:
            installedOn = style.getInstalledVehicles()
            if vehicle.intCD not in installedOn:
                ctx = customization.getCtx()
                ctx.changeMode(CustomizationModes.STYLE_3D if style.is3D else CustomizationModes.STYLE_2D)
                ctx.mode.installItem(style.intCD, StyledMode.STYLE_SLOT)
                ctx.selectItem(style.intCD)
        return

    vehicles = itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(style.mayInstall))
    vehicle = first(vehicles.itervalues()) if vehicles else None
    if style.isInInventory and vehicle is not None and vehicle.isInInventory and vehicle.isCustomizationEnabled():
        customization.showCustomization(vehicle.invID, callback=_callback, prevVehicleInvID=g_currentVehicle.invID)
    else:
        showVehicleStylePreview(style, previewBackCb=previewBackCb, backBtnLabel=backBtnLabel)
    return


def showVehicleStylePreview(style, previewBackCb=None, backBtnLabel=''):
    ClientSelectableCameraObject.switchCamera()
    if style.isProgression:
        raise SoftException('Progression styles is not supported')
    vehicle = getVehicleForStyle(style)
    showStylePreview(vehicle.intCD, style, backCallback=previewBackCb, backBtnDescrLabel=backBtnLabel)


def openShop(eventName, parent=None, executePreconditions=False):
    showBrowserOverlayView(getShopOverlayUrl(eventName), VIEW_ALIAS.OVERLAY_WEB_STORE)
    if not executePreconditions:
        from gui.impl.lobby.lootbox_system.base.info_page import InfoPage
        InfoPage.cleanBaseWindow()


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def findActiveWindow(viewID, uiLoader=None):
    return uiLoader.windowsManager.getViewByLayoutID(viewID)


def registerViewsLoaders():
    Views.setLoaders({ViewID.INTRO: showIntro,
     ViewID.MAIN: showMain,
     ViewID.INFO: showInfo,
     ViewID.AUTOOPEN: showAutoOpen,
     ViewID.SHOP: openShop})


def unregisterViewsLoaders():
    Views.clear()
