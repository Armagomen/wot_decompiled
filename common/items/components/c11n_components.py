# Source Generated with Decompyle++
# File: c11n_components.pyc (Python 2.7)

import itertools
from backports.functools_lru_cache import lru_cache
import Math
import items
import items.vehicles as iv
import nations
from debug_utils import LOG_CURRENT_EXCEPTION
from items import vehicles
from items.components import shared_components
from soft_exception import SoftException
from items.components.c11n_constants import ApplyArea, SeasonType, Options, ItemTags, CustomizationType, MAX_CAMOUFLAGE_PATTERN_SIZE, DecalType, HIDDEN_CAMOUFLAGE_ID, PROJECTION_DECALS_SCALE_ID_VALUES, MAX_USERS_PROJECTION_DECALS, CustomizationTypeNames, DecalTypeNames, CustomizationNamesToTypes, ProjectionDecalFormTags, CUSTOMIZATION_SLOTS_VEHICLE_PARTS, CamouflageTilingType, HIDDEN_FOR_USER_TAG, SLOT_TYPE_NAMES, EMPTY_ITEM_ID, SLOT_DEFAULT_ALLOWED_MODEL, EDITING_STYLE_REASONS
from typing import List, Dict, Type, Tuple, Optional, TypeVar, FrozenSet, Set
from string import lower, upper
from copy import deepcopy
from wrapped_reflection_framework import ReflectionMetaclass
from constants import IS_EDITOR, ARENA_BONUS_TYPE_NAMES
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
if IS_EDITOR:
    from editor_copy import edCopy
Item = TypeVar('TypeVar')

class BaseCustomizationItem(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('id', 'tags', 'filter', 'parentGroup', 'season', 'historical', 'i18n', 'priceGroup', 'requiredToken', 'priceGroupTags', 'maxNumber', 'texture', 'progression')
    allSlots = __slots__
    itemType = 0
    
    def __init__(self, parentGroup = None):
        self.id = 0
        self.tags = frozenset()
        self.filter = None
        self.season = SeasonType.ALL
        self.historical = False
        self.i18n = None
        self.priceGroup = ''
        self.priceGroupTags = frozenset()
        self.requiredToken = ''
        self.maxNumber = 0
        self.texture = ''
        self.progression = None
        if not IS_EDITOR:
            pass
        copyBaseValue = edCopy
        if parentGroup and parentGroup.itemPrototype:
            for field in self.allSlots:
                if hasattr(parentGroup.itemPrototype, field):
                    value = getattr(parentGroup.itemPrototype, field)
                    setattr(self, field, copyBaseValue(value))
                    continue
        self.parentGroup = parentGroup

    
    def _copy(self, newItem):
        newItem.id = self.id
        newItem.tags = deepcopy(self.tags)
        newItem.filter = deepcopy(self.filter)
        newItem.season = self.season
        newItem.historical = self.historical
        newItem.i18n = deepcopy(self.i18n)
        newItem.priceGroup = deepcopy(self.priceGroup)
        newItem.priceGroupTags = deepcopy(self.priceGroupTags)
        newItem.requiredToken = deepcopy(self.requiredToken)
        newItem.maxNumber = self.maxNumber
        newItem.texture = deepcopy(self.texture)
        newItem.progression = deepcopy(self.progression)
        newItem.parentGroup = self.parentGroup

    
    def matchVehicleType(self, vehTypeDescr):
        if not not (self.filter):
            pass
        return self.filter.matchVehicleType(vehTypeDescr)

    
    def isVehicleBound(self):
        return ItemTags.VEHICLE_BOUND in self.tags

    
    def isUnlocked(self, tokens):
        if not (self.requiredToken) and tokens:
            pass
        return self.requiredToken in tokens

    
    def isRare(self):
        return ItemTags.RARE in self.tags

    
    def isHiddenInUI(self):
        return ItemTags.HIDDEN_IN_UI in self.tags

    
    def isProgressive(self):
        return self.progression is not None

    
    def isUnique(self):
        return self.maxNumber > 0

    isUnique = property(isUnique)
    
    def isStyleOnly(self):
        return ItemTags.STYLE_ONLY in self.tags

    isStyleOnly = property(isStyleOnly)
    
    def makeIntDescr(cls, itemId):
        return items.makeIntCompactDescrByID('customizationItem', cls.itemType, itemId)

    makeIntDescr = classmethod(makeIntDescr)
    
    def compactDescr(self):
        return self.__class__.makeIntDescr(self.id)

    compactDescr = property(compactDescr)
    
    def userString(self):
        if self.i18n:
            return self.i18n.userString

    userString = property(userString)
    
    def userKey(self):
        if self.i18n:
            return self.i18n.userKey

    userKey = property(userKey)
    
    def description(self):
        description = self.i18n.description
        if self.i18n:
            return description

    description = property(description)
    
    def shortDescriptionSpecial(self):
        shortDescriptionSpecial = self.i18n.shortDescriptionSpecial
        if self.i18n:
            return shortDescriptionSpecial

    shortDescriptionSpecial = property(shortDescriptionSpecial)
    
    def longDescriptionSpecial(self):
        longDescriptionSpecial = self.i18n.longDescriptionSpecial
        if self.i18n:
            return longDescriptionSpecial

    longDescriptionSpecial = property(longDescriptionSpecial)


class PaintItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.PAINT
    __slots__ = ('color', 'usageCosts', 'gloss', 'metallic')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.color = 0
        self.usageCosts = (lambda .0: pass# WARNING: Decompyle incomplete
)(ApplyArea.RANGE)
        self.gloss = 0
        self.metallic = 0
        super(PaintItem, self).__init__(parentGroup)

    
    def getAmount(self, parts):
        result = 0
        for i in ApplyArea.RANGE:
            if parts & i or i not in self.usageCosts:
                return None
            None += self.usageCosts[i]
            continue
        
        return result



class DecalItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.DECAL
    __slots__ = ('type', 'canBeMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.type = 0
        self.canBeMirrored = False
        super(DecalItem, self).__init__(parentGroup)



class ProjectionDecalItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.PROJECTION_DECAL
    __slots__ = ('canBeMirroredHorizontally', 'glossTexture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.canBeMirroredHorizontally = False
        self.glossTexture = ''
        super(ProjectionDecalItem, self).__init__(parentGroup)

    
    def canBeMirroredVertically(self):
        return ItemTags.DISABLE_VERTICAL_MIRROR not in self.tags

    canBeMirroredVertically = property(canBeMirroredVertically)
    
    def canBeMirroredOnlyVertically(self):
        return ItemTags.ONLY_VERTICAL_MIRROR in self.tags

    canBeMirroredOnlyVertically = property(canBeMirroredOnlyVertically)


class CamouflageItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.CAMOUFLAGE
    __slots__ = ('palettes', 'compatibleParts', 'componentsCovering', 'invisibilityFactor', 'tiling', 'tilingSettings', 'scales', 'rotation', 'glossMetallicSettings')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.compatibleParts = ApplyArea.CAMOUFLAGE_REGIONS_VALUE
        self.componentsCovering = 0
        self.palettes = []
        self.invisibilityFactor = 1
        self.rotation = {
            'hull': 0,
            'turret': 0,
            'gun': 0 }
        self.tiling = { }
        self.tilingSettings = (CamouflageTilingType.LEGACY, None, None)
        self.scales = (1.2, 1, 0.7)
        self.glossMetallicSettings = {
            'glossMetallicMap': '',
            'gloss': Math.Vector4(0),
            'metallic': Math.Vector4(0) }
        super(CamouflageItem, self).__init__(parentGroup)

    
    def __deepcopy__(self, memodict = { }):
        newItem = type(self)()
        newItem.compatibleParts = self.compatibleParts
        newItem.componentsCovering = self.componentsCovering
        newItem.palettes = deepcopy(self.palettes)
        newItem.invisibilityFactor = self.invisibilityFactor
        newItem.rotation = deepcopy(self.rotation)
        newItem.tiling = deepcopy(self.tiling)
        newItem.tilingSettings = deepcopy(self.tilingSettings)
        newItem.scales = self.scales
        super(CamouflageItem, self)._copy(newItem)
        return newItem



class PersonalNumberItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.PERSONAL_NUMBER
    _PersonalNumberItem__prohibitedNumbers = ()
    __slots__ = ('compatibleParts', 'digitsCount', 'previewTexture', 'fontInfo', 'isMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.compatibleParts = ApplyArea.INSCRIPTION_REGIONS
        self.digitsCount = 3
        self.previewTexture = ''
        self.fontInfo = None
        self.isMirrored = False
        super(PersonalNumberItem, self).__init__(parentGroup)

    
    def setProhibitedNumbers(cls, prohibitedNumbers):
        cls._PersonalNumberItem__prohibitedNumbers = frozenset(prohibitedNumbers)

    setProhibitedNumbers = classmethod(setProhibitedNumbers)
    
    def getProhibitedNumbers(cls):
        return cls._PersonalNumberItem__prohibitedNumbers

    getProhibitedNumbers = classmethod(getProhibitedNumbers)


class SequenceItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.SEQUENCE
    __slots__ = ('sequenceName',)
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.sequenceName = None
        super(SequenceItem, self).__init__(parentGroup)



class AttachmentItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.ATTACHMENT
    __slots__ = ('modelName', 'sequenceId', 'attachmentLogic', 'initialVisibility')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.modelName = None
        self.sequenceId = None
        self.attachmentLogic = None
        self.initialVisibility = True
        super(AttachmentItem, self).__init__(parentGroup)



class ModificationItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.MODIFICATION
    __slots__ = ('effects',)
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.effects = { }
        super(ModificationItem, self).__init__(parentGroup)

    
    def getEffectValue(self, type, default = 0):
        return self.effects.get(type, default)



class StyleItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.STYLE
    __slots__ = ('outfits', 'isRent', 'rentCount', 'modelsSet', 'isEditable', 'alternateItems', 'itemsFilters', '_changeableSlotTypes', 'styleProgressions', 'dependencies', 'dependenciesAncestors')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.outfits = { }
        self.isRent = False
        self.rentCount = 1
        self.modelsSet = ''
        self.isEditable = False
        self.alternateItems = { }
        self.itemsFilters = { }
        self.dependencies = { }
        self.dependenciesAncestors = { }
        self._changeableSlotTypes = None
        self.styleProgressions = { }
        super(StyleItem, self).__init__(parentGroup)

    
    def isVictim(self, color):
        return '{}Victim'.format(color) in self.tags

    
    def isItemInstallable(self, item):
        if not self.isEditable:
            return False
        if None.historical and not (item.historical):
            return False
        if None.id in self.alternateItems.get(item.itemType, ()):
            return True
        itemFilter = None.itemsFilters.get(item.itemType)
        if itemFilter is None:
            return False
        return None.match(item)

    
    def changeableSlotTypes(self):
        if self._changeableSlotTypes is None:
            
            c11nChecker = lambda i: self.isItemInstallable(i)
            
            emblemChecker = lambda i: if self.isItemInstallable(i):
passi.type == DecalType.EMBLEM
            
            inscriptionChecker = lambda i: if self.isItemInstallable(i):
passi.type == DecalType.INSCRIPTION
            _C11N_TYPES_CHECK_DATA = ((CustomizationType.MODIFICATION, c11nChecker, None), (CustomizationType.CAMOUFLAGE, c11nChecker, None), (CustomizationType.PAINT, c11nChecker, None), (CustomizationType.PROJECTION_DECAL, c11nChecker, None), (CustomizationType.PERSONAL_NUMBER, c11nChecker, None), (CustomizationType.DECAL, emblemChecker, DecalType.EMBLEM), (CustomizationType.DECAL, inscriptionChecker, DecalType.INSCRIPTION))
            customizationCache = vehicles.g_cache.customization20()
            slotTypes = set()
            for (c11nType, checker, decalType) in _C11N_TYPES_CHECK_DATA:
                for item in customizationCache.itemTypes[c11nType].itervalues():
                    if item.id == EMPTY_ITEM_ID:
                        continue
                    if checker(item):
                        slotTypes.add(getSlotType(c11nType, decalType))
                        break
                        continue
            
            self._changeableSlotTypes = slotTypes
        return self._changeableSlotTypes

    changeableSlotTypes = property(changeableSlotTypes)
    
    def clearableSlotTypes(self):
        return set(SLOT_TYPE_NAMES.EDITABLE_STYLE_DELETABLE).intersection(self.changeableSlotTypes)

    clearableSlotTypes = property(clearableSlotTypes)
    
    def isProgression(self):
        return ItemTags.STYLE_PROGRESSION in self.tags

    isProgression = property(isProgression)
    
    def hasDependent(self):
        return bool(self.dependencies)

    hasDependent = property(hasDependent)


class InsigniaItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.INSIGNIA
    __slots__ = ('atlas', 'alphabet', 'canBeMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__
    
    def __init__(self, parentGroup = None):
        self.atlas = ''
        self.alphabet = ''
        self.canBeMirrored = False
        super(InsigniaItem, self).__init__(parentGroup)



class ItemGroup(object):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.ITEM_GROUP
    __slots__ = ('itemPrototype', 'name')
    
    def __init__(self, itemClass):
        self.itemPrototype = itemClass()
        self.name = ''
        super(ItemGroup, self).__init__()

    
    def id(self):
        return self.itemPrototype.id

    id = property(id)
    
    def makeIntDescr(cls, itemId):
        return items.makeIntCompactDescrByID('customizationItem', cls.itemType, itemId)

    makeIntDescr = classmethod(makeIntDescr)
    
    def compactDescr(self):
        return self.makeIntDescr(self.itemPrototype.id)

    compactDescr = property(compactDescr)


class PriceGroup(object):
    itemType = CustomizationType.ITEM_GROUP
    __slots__ = ('price', 'notInShop', 'id', 'name', 'tags')
    
    def __init__(self):
        self.price = (0, 0, 0)
        self.name = None
        self.id = 0
        self.notInShop = False
        self.tags = []

    
    def compactDescr(self):
        return items.makeIntCompactDescrByID('customizationItem', self.itemType, self.id)

    compactDescr = property(compactDescr)


class Font(object):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.FONT
    __slots__ = ('id', 'texture', 'alphabet', 'mask')
    
    def __init__(self):
        self.id = 0
        self.texture = ''
        self.alphabet = ''
        self.mask = ''

    
    def compactDescr(self):
        return items.makeIntCompactDescrByID('customizationItem', self.itemType, self.id)

    compactDescr = property(compactDescr)

if IS_EDITOR:
    CUSTOMIZATION_TYPES = {
        CustomizationType.MODIFICATION: ModificationItem,
        CustomizationType.STYLE: StyleItem,
        CustomizationType.DECAL: DecalItem,
        CustomizationType.CAMOUFLAGE: CamouflageItem,
        CustomizationType.PERSONAL_NUMBER: PersonalNumberItem,
        CustomizationType.PAINT: PaintItem,
        CustomizationType.PROJECTION_DECAL: ProjectionDecalItem,
        CustomizationType.INSIGNIA: InsigniaItem,
        CustomizationType.SEQUENCE: SequenceItem,
        CustomizationType.FONT: Font,
        CustomizationType.ATTACHMENT: AttachmentItem }
    CUSTOMIZATION_CLASSES = (lambda .0: pass# WARNING: Decompyle incomplete
)(CUSTOMIZATION_TYPES.items())

class _Filter(object):
    __slots__ = ('include', 'exclude')
    
    def __init__(self):
        super(_Filter, self).__init__()
        self.include = []
        self.exclude = []

    
    def __deepcopy__(self, memodict = { }):
        newItem = type(self)()
        newItem.include = deepcopy(self.include)
        newItem.exclude = deepcopy(self.exclude)
        return newItem

    
    def __str__(self):
        includes = map((lambda x: str(x)), self.include)
        excludes = map((lambda x: str(x)), self.exclude)
        result = []
        if includes:
            result.append('includes: ' + str(includes))
        if excludes:
            result.append('excludes: ' + str(excludes))
        return '; '.join(result)

    
    def match(self, item):
        raise NotImplementedError



class VehicleFilter(_Filter):
    __metaclass__ = ReflectionMetaclass
    
    class FilterNode(object):
        __metaclass__ = ReflectionMetaclass
        __slots__ = ('nations', 'levels', 'tags', 'vehicles')
        
        def __init__(self):
            self.nations = None
            self.levels = None
            self.tags = None
            self.vehicles = None

        
        def __deepcopy__(self, memodict = { }):
            newItem = type(self)()
            newItem.nations = deepcopy(self.nations)
            newItem.levels = deepcopy(self.levels)
            newItem.vehicles = deepcopy(self.vehicles)
            newItem.tags = deepcopy(self.tags)
            return newItem

        
        def __str__(self):
            result = []
            if self.nations:
                result.append(str(self.nations))
            if self.levels:
                result.append(str(self.levels))
            if self.vehicles:
                result.append(str(self.vehicles))
            if self.tags:
                result.append(str(self.tags))
            return '; '.join(result)

        
        def match(self, vehicleDescr):
            return self.matchVehicleType(vehicleDescr.type)

        
        def matchVehicleType(self, vehicleType):
            nationID = vehicleType.customizationNationID
            if self.nations and nationID not in self.nations:
                return False
            if None.levels and vehicleType.level not in self.levels:
                return False
            if None.vehicles and vehicleType.compactDescr not in self.vehicles:
                return False
            if None.tags and not (self.tags < vehicleType.tags):
                return False


    
    def match(self, vehicleDescr):
        if not not (self.include):
            pass
        include = (any,)((lambda .0: continue)(self.include))
        if include:
            if self.exclude:
                pass
        return not (any,)((lambda .0: continue)(self.exclude))

    
    def matchVehicleType(self, vehicleType):
        if not not (self.include):
            pass
        include = (any,)((lambda .0: continue)(self.include))
        if include:
            if self.exclude:
                pass
        return not (any,)((lambda .0: continue)(self.exclude))



class ItemsFilter(_Filter):
    __metaclass__ = ReflectionMetaclass
    
    class FilterNode(object):
        __slots__ = ('ids', 'itemGroupNames', 'tags', 'types', 'historical')
        
        def __init__(self):
            self.ids = None
            self.itemGroupNames = None
            self.tags = None
            self.types = None
            self.historical = None

        
        def __str__(self):
            result = []
            if self.ids is not None:
                result.append(str(self.ids))
            if self.itemGroupNames is not None:
                result.append(str(self.itemGroupNames))
            if self.tags is not None:
                result.append(str(self.tags))
            if self.types is not None:
                result.append(str(self.types))
            if self.historical is not None:
                result.append(str(self.historical))
            return '; '.join(result)

        
        def matchItem(self, item):
            if self.ids is not None and item.id not in self.ids:
                return False
            if None.itemGroupNames is not None and item.parentGroup.name not in self.itemGroupNames:
                return False
            if None.tags is not None and not (self.tags < item.tags):
                return False
            if None.types is not None and item.itemType == CustomizationType.DECAL and item.type not in self.types:
                return False
            if None.historical is not None and item.historical != self.historical:
                return False


    
    def match(self, item):
        if not not (self.include):
            pass
        include = (any,)((lambda .0: continue)(self.include))
        if include:
            if self.exclude:
                pass
        return not (any,)((lambda .0: continue)(self.exclude))



class ProgressForCustomization(object):
    __slots__ = ('autobound', 'levels', 'autoGrantCount', 'bonusTypes', 'priceGroup', 'defaultLvl')
    
    def __init__(self):
        super(ProgressForCustomization, self).__init__()
        self.autobound = False
        self.levels = { }
        self.autoGrantCount = 0
        self.bonusTypes = set()
        self.priceGroup = ''
        self.defaultLvl = 0

    
    def __deepcopy__(self, memodict = { }):
        newItem = type(self)()
        newItem.autobound = self.autobound
        newItem.levels = deepcopy(self.levels)
        newItem.autoGrantCount = self.autoGrantCount
        newItem.priceGroup = self.priceGroup
        newItem.defaultLvl = self.defaultLvl
        return newItem

    
    def __str__(self):
        result = {
            'autobound': self.autobound,
            'levels': self.levels,
            'autoGrantCount': self.autoGrantCount,
            'bonusTypes': self.bonusTypes,
            'priceGroup': self.priceGroup,
            'defaultLvl': self.defaultLvl }
        return str(result)



class CustomizationCache(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('paints', 'camouflages', 'decals', 'projection_decals', 'modifications', 'levels', 'itemToPriceGroup', 'priceGroups', 'priceGroupNames', 'insignias', 'styles', 'defaultColors', 'defaultInsignias', 'itemTypes', 'priceGroupTags', '__victimStyles', 'personal_numbers', 'fonts', 'sequences', 'attachments', 'customizationWithProgression', 'itemGroupByProgressionBonusType', '__vehicleCanMayIncludeCustomization', 'topVehiclesByNation')
    
    def __init__(self):
        self.priceGroupTags = { }
        self.paints = { }
        self.camouflages = { }
        self.decals = { }
        self.projection_decals = { }
        self.personal_numbers = { }
        self.modifications = { }
        self.itemToPriceGroup = { }
        self.priceGroups = { }
        self.priceGroupNames = { }
        self.styles = { }
        self.insignias = { }
        self.defaultInsignias = { }
        self.defaultColors = { }
        self.fonts = { }
        self.sequences = { }
        self.attachments = { }
        self._CustomizationCache__victimStyles = { }
        self.customizationWithProgression = { }
        self.itemGroupByProgressionBonusType = (lambda .0: pass# WARNING: Decompyle incomplete
)(ARENA_BONUS_TYPE_NAMES.values())
        self._CustomizationCache__vehicleCanMayIncludeCustomization = { }
        self.topVehiclesByNation = { }
        self.itemTypes = {
            CustomizationType.MODIFICATION: self.modifications,
            CustomizationType.STYLE: self.styles,
            CustomizationType.DECAL: self.decals,
            CustomizationType.CAMOUFLAGE: self.camouflages,
            CustomizationType.PERSONAL_NUMBER: self.personal_numbers,
            CustomizationType.PAINT: self.paints,
            CustomizationType.PROJECTION_DECAL: self.projection_decals,
            CustomizationType.INSIGNIA: self.insignias,
            CustomizationType.SEQUENCE: self.sequences,
            CustomizationType.ATTACHMENT: self.attachments }
        super(CustomizationCache, self).__init__()

    
    def getVehiclesCanMayInclude(self, item):
        vehsCanUseItem = self._CustomizationCache__vehicleCanMayIncludeCustomization.get(item.compactDescr)
        if vehsCanUseItem is None:
            vehsCanUseItem = []
            for nationID in nations.INDICES.itervalues():
                for descr in iv.g_list.getList(nationID).itervalues():
                    vehCD = descr.compactDescr
                    if item.matchVehicleType(iv.getVehicleType(vehCD)):
                        vehsCanUseItem.append(vehCD)
                        continue
            
            self._CustomizationCache__vehicleCanMayIncludeCustomization[item.compactDescr] = vehsCanUseItem
        return vehsCanUseItem

    
    def isVehicleBound(self, itemId):
        if isinstance(itemId, int):
            (itemType, inTypeId) = splitIntDescr(itemId)
        else:
            (itemType, inTypeId) = itemId
        if itemType not in self.itemTypes:
            raise SoftException('Incorrect item type', itemId)
        if inTypeId not in self.itemTypes[itemType]:
            raise SoftException('Item not found in cache', itemId)
        return ItemTags.VEHICLE_BOUND in self.itemTypes[itemType][inTypeId].tags

    
    def splitByVehicleBound(self, itemsDict, vehType):
        itemsToOperate = (lambda .0: pass# WARNING: Decompyle incomplete
)(itemsDict.iteritems())
        return itemsToOperate

    
    def getVictimStyles(self, hunting, vehType):
        if not self._CustomizationCache__victimStyles:
            self._CustomizationCache__victimStyles[''] = { }
            stylesByColor = self._CustomizationCache__victimStyles.setdefault
            for style in self.styles.itervalues():
                for tag in style.tags:
                    if tag.endswith('Victim'):
                        stylesByColor(tag[:-6], []).append(style)
                        continue
            
        for s in self._CustomizationCache__victimStyles.get(hunting, []):
            if s.matchVehicleType(vehType):
                continue
                return [][s]

    
    def validateOutfit(self, vehDescr, outfit, progressionStorage, tokens = None, season = SeasonType.ALL):
        usedStyle = None
        
        try:
            vehType = vehDescr.type
            styleID = outfit.styleId
            if styleID != 0:
                usedStyle = self.styles.get(styleID, None)
                if usedStyle is None:
                    raise SoftException('Wrong styleId {} '.format(styleID))
                if not usedStyle.matchVehicleType(vehType):
                    raise SoftException('style {} is incompatible with vehicle {}'.format(styleID, vehDescr.name))
                if usedStyle.isProgressive():
                    if usedStyle.progression.defaultLvl > outfit.styleProgressionLevel:
                        pass
                    outfit.styleProgressionLevel > len(usedStyle.progression.levels)
                    if 1:
                        raise SoftException('Progression style {} level out of limits'.format(styleID))
            projectionDecalsCount = len(outfit.projection_decals)
            if projectionDecalsCount > MAX_USERS_PROJECTION_DECALS:
                raise SoftException('projection decals quantity {} greater than acceptable'.format(projectionDecalsCount))
            for itemType in CustomizationType.FULL_RANGE:
                typeName = lower(CustomizationTypeNames[itemType])
                componentsAttrName = '{}s'.format(typeName)
                components = getattr(outfit, componentsAttrName, None)
                if not components:
                    continue
                elif usedStyle is not None and not (usedStyle.isEditable):
                    raise SoftException("Style {} can't contain extra items in outfit".format(styleID))
                if itemType in CustomizationType.STYLE_ONLY_RANGE and components:
                    raise SoftException("Outfit can't contain style-only items: {}".format(components))
                storage = getattr(self, componentsAttrName)
                if usedStyle is not None:
                    baseOutfit = usedStyle.outfits.get(season)
                    if not baseOutfit:
                        raise SoftException("Style {} hasn't base outfit for season {}".format(styleID, season))
                    baseComponents = getattr(baseOutfit, componentsAttrName, None)
                for component in components:
                    if not isinstance(component, int):
                        pass
                    componentId = component
                    item = storage.get(componentId, None)
                    if componentId != EMPTY_ITEM_ID:
                        if item is None:
                            raise SoftException('{} {} not found'.format(typeName, componentId))
                        _validateItem(typeName, item, season, tokens, vehType, styleID)
                        if item.isProgressive():
                            _validateProgression(component, item, progressionStorage, vehType)
                        if itemType in CustomizationType.APPLIED_TO_TYPES:
                            _validateApplyTo(component, item)
                            if itemType == CustomizationType.CAMOUFLAGE:
                                _validateCamouflage(component, item)
                            elif itemType == CustomizationType.PERSONAL_NUMBER:
                                _validatePersonalNumber(component, item)
                            
                        elif itemType == CustomizationType.PROJECTION_DECAL:
                            _validateProjectionDecal(component, item, vehDescr, usedStyle)
                        
                    if usedStyle is not None and usedStyle.isEditable:
                        _validateEditableStyle(componentId, typeName, itemType, component, item, usedStyle, outfit, vehDescr, baseComponents, season)
                        continue
            
            if usedStyle is not None and usedStyle.isEditable:
                _validateDependencies(outfit, usedStyle, vehDescr, season)
        except SoftException:
            1
            ex = component.id
            return (False, ex.message)

        return (True, '')

    
    def adjustProgression(self, vehTypeCompDescr, outfit, progressionStorage, itemForce = None):
        force = False
        itemTypes = CustomizationType.RANGE
    # WARNING: Decompyle incomplete



class EditingStyleReason(object):
    
    def __init__(self, reson):
        self.reason = reson

    
    def __nonzero__(self):
        return self.reason in EDITING_STYLE_REASONS.ENABLED



def _adjustProgression(component, vehTypeCD, item, progressionStorage, attr, force = False):
    if item is None:
        raise SoftException('Missing customization item for component: {}'.format(component))
    if not item.isProgressive():
        return None
    if not None(component, attr):
        raise SoftException('Missing progression level for component: {}'.format(component))
    if not force and getattr(component, attr):
        return None
    if not None.progression.autobound:
        vehTypeCD = 0
    level = progressionStorage.get(item.itemType, { }).get(item.id, { }).get(vehTypeCD, { }).get('level')
    if level is None:
        raise SoftException('missing progression for item: {} at vehicle: {}'.format(item.id, vehTypeCD))
    setattr(component, attr, level)


def _validateItem(typeName, item, season, tokens, vehType, styleID):
    if not item.matchVehicleType(vehType):
        raise SoftException('{} {} incompatible vehicle {}'.format(typeN