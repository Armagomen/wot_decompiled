# Source Generated with Decompyle++
# File: customizations.pyc (Python 2.7)

from cStringIO import StringIO
from string import lower, upper
import base64
import copy
import varint
import ResMgr
import Math
from collections import namedtuple, OrderedDict, defaultdict
from soft_exception import SoftException
from items.components.c11n_constants import ApplyArea, SeasonType, Options, CustomizationType, CustomizationTypeNames, HIDDEN_CAMOUFLAGE_ID, MAX_USERS_PROJECTION_DECALS, CUSTOMIZATION_SLOTS_VEHICLE_PARTS, DEFAULT_SCALE_FACTOR_ID, EMPTY_ITEM_ID, DEFAULT_SCALE, DEFAULT_ROTATION, DEFAULT_POSITION, DEFAULT_DECAL_TINT_COLOR, ProjectionDecalMatchingTags
from items.components import c11n_components as cn
from constants import IS_CELLAPP, IS_BASEAPP, IS_EDITOR
from items import decodeEnum
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
import enum
from typing import List, Dict, Type, Tuple, Any, TypeVar, Optional, MutableMapping, TYPE_CHECKING
from wrapped_reflection_framework import ReflectionMetaclass
if TYPE_CHECKING:
    from items.vehicles import VehicleDescrType

def getEditorOnlySection(section, createNewSection = False):
    editorOnlySection = section['editorOnly']
    if editorOnlySection is None and createNewSection:
        findOrCreate = findOrCreate
        import items.writers.c11n_writers
        editorOnlySection = findOrCreate(section, 'editorOnly')
    return editorOnlySection


class FieldTypes(object):
    VARINT = 2
    TAGS = 4
    OPTIONS_ENUM = 8
    FLOAT = 16
    APPLY_AREA_ENUM = 32
    TYPED_ARRAY = 64
    CUSTOM_TYPE_OFFSET = 128
    STRING = 512

FieldFlags = enum.unique(<NODE:12>)

class _C11nSerializationTypes(object):
    DEFAULT = 0
    PAINT = 1
    CAMOUFLAGE = 2
    DECAL = 3
    OUTFIT = 4
    INSIGNIA = 5
    PROJECTION_DECAL = 7
    PERSONAL_NUMBER = 8
    SEQUENCE = 9
    ATTACHMENT = 10

if IS_EDITOR:
    FieldType = namedtuple('FieldType', 'type default flags saveTag')
    FieldType.__new__.func_defaults = (None,) * len(FieldType._fields)
else:
    FieldType = namedtuple('FieldType', 'type default flags')

def arrayField(itemType, default = None, flags = FieldFlags.NONE):
    if not default:
        pass
    return FieldType(FieldTypes.TYPED_ARRAY | itemType, [], flags)


def intField(default = 0, nonXml = False):
    if nonXml:
        pass
    return default(FieldFlags.NON_XML, 1, FieldFlags.NONE)


def strField(default = ''):
    return FieldType(FieldTypes.STRING, default, FieldFlags.NONE)


def xmlOnlyIntField(default = 0):
    return FieldType(FieldTypes.VARINT, default, FieldFlags.NON_BIN)


def xmlOnlyFloatField(default = 0):
    return FieldType(FieldTypes.FLOAT, default, FieldFlags.NON_BIN)


def xmlOnlyFloatArrayField(default = None):
    if not default:
        pass
    return FieldType(FieldTypes.TYPED_ARRAY | FieldTypes.FLOAT, [], FieldFlags.NON_BIN)


def applyAreaEnumField(default = 0):
    return FieldType(FieldTypes.APPLY_AREA_ENUM, default, FieldFlags.WEAK_EQUAL_IGNORED)


def xmlOnlyApplyAreaEnumField(default = 0, flags = FieldFlags.NONE):
    return FieldType(FieldTypes.APPLY_AREA_ENUM, default, FieldFlags.WEAK_EQUAL_IGNORED | FieldFlags.NON_BIN | flags)


def xmlOnlyTagsField(default = ()):
    return FieldType(FieldTypes.TAGS, default, FieldFlags.WEAK_EQUAL_IGNORED | FieldFlags.NON_BIN)


def optionsEnumField(default = 0):
    return FieldType(FieldTypes.OPTIONS_ENUM, default, FieldFlags.NONE)


def customFieldType(customType):
    return FieldType(FieldTypes.CUSTOM_TYPE_OFFSET * customType, None, FieldFlags.NONE)


def intArrayField(default = None, flags = FieldFlags.NONE):
    if not default:
        pass
    return arrayField(FieldTypes.VARINT, [], flags)


def customArrayField(customType, default = None):
    return arrayField(FieldTypes.CUSTOM_TYPE_OFFSET * customType, default)


class SerializationException(SoftException):
    pass


class FoundItemException(SoftException):
    pass


class SerializableComponent(object):
    fields = OrderedDict()
    __slots__ = ()
    customType = _C11nSerializationTypes.DEFAULT
    preview = False
    
    def _SerializableComponent__eq(self, o, ignoreFlags):
        if self.__class__ != o.__class__:
            return False
        for (fname, ftype) in self.fields.iteritems():
            if ftype.flags & ignoreFlags:
                continue
            v1 = getattr(self, fname)
            v2 = getattr(o, fname)
            if ftype.type & FieldTypes.TYPED_ARRAY:
                v1 = set(v1)
                v2 = set(v2)
            if v1 != v2:
                return False
        return True

    
    def __eq__(self, o):
        return self._SerializableComponent__eq(o, FieldFlags.DEPRECATED)

    
    def __ne__(self, o):
        return not self.__eq__(o)

    
    def __hash__(self):
        result = 17
        for (name, ftype) in self.fields.iteritems():
            if ftype.flags & FieldFlags.DEPRECATED:
                continue
            v1 = getattr(self, name)
            if isinstance(v1, list):
                v1 = tuple(v1)
            if isinstance(v1, Math.Vector2) and isinstance(v1, Math.Vector3) or isinstance(v1, Math.Vector4):
                v1 = tuple(v1)
            result = (result * 31 + hash(v1)) % 0x10000000000000000L
        
        return result

    
    def __repr__(self):
        buf = StringIO()
        self._SerializableComponent__writeStr(buf)
        return buf.getvalue()

    
    def weak_eq(self, o):
        return self._SerializableComponent__eq(o, FieldFlags.DEPRECATED | FieldFlags.WEAK_EQUAL_IGNORED)

    
    def copy(self):
        o = self.__class__()
        for fname in self.fields.iterkeys():
            setattr(o, fname, getattr(self, fname))
        
        return o

    
    def isFilled(self):
        return True

    
    def _SerializableComponent__writeStr(self, stream):
        stream.write('{')
        i = 0
        n = len(self.fields)
        for (name, fieldInfo) in self.fields.iteritems():
            if fieldInfo.flags & FieldFlags.DEPRECATED:
                continue
            v = getattr(self, name)
            stream.write('%s: %s' % (name, repr(v)))
            i += 1
            if i != n:
                stream.write(', ')
                continue
        stream.write('}')



class ComponentBinSerializer(object):
    
    def __init__(self):
        super(ComponentBinSerializer, self).__init__()

    
    def serialize(self, target):
        a = varint.encode(target.customType)
        b = self._ComponentBinSerializer__serializeCustomType(target)
        return a + b

    
    def _ComponentBinSerializer__serializeCustomType(self, obj):
        hasValue = 0
        offset = 1
        result = [
            '\x0']
        for (fieldName, fieldInfo) in obj.fields.iteritems():
            if fieldInfo.flags & FieldFlags.DEPRECATED:
                offset <<= 1
                continue
            if fieldInfo.flags & FieldFlags.NON_BIN:
                continue
            if IS_EDITOR and fieldInfo.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
                continue
            value = getattr(obj, fieldName)
            if value != fieldInfo.default:
                hasValue |= offset
                result.append(self._ComponentBinSerializer__serialize(value, fieldInfo.type))
            offset <<= 1
        
        result[0] = varint.encode(hasValue)
        return ''.join(result)

    
    def _ComponentBinSerializer__serializeArray(self, value, itemType):
        continue
        result = [ self._ComponentBinSerializer__serialize(item, itemType) for item in value ]
        return varint.encode(len(value)) + ''.join(result)

    
    def _ComponentBinSerializer__serializeString(self, value):
        return varint.encode(len(value)) + value

    
    def _ComponentBinSerializer__serialize(self, value, itemType):
        if itemType == FieldTypes.VARINT:
            return varint.encode(value)
        if None == FieldTypes.STRING:
            return self._ComponentBinSerializer__serializeString(value)
        if None == FieldTypes.APPLY_AREA_ENUM:
            return varint.encode(value)
        if None == FieldTypes.OPTIONS_ENUM:
            return varint.encode(value)
        if None & FieldTypes.TYPED_ARRAY:
            return self._ComponentBinSerializer__serializeArray(value, itemType ^ FieldTypes.TYPED_ARRAY)
        if None >= FieldTypes.CUSTOM_TYPE_OFFSET:
            return self._ComponentBinSerializer__serializeCustomType(value)
        raise None('Unsupported field type %d' % (itemType,))



class ComponentBinDeserializer(object):
    
    def __init__(self, customTypes):
        self._ComponentBinDeserializer__stream = None
        self.customTypes = customTypes
        super(ComponentBinDeserializer, self).__init__()

    
    def decode(self, data):
        self._ComponentBinDeserializer__stream = StringIO(data)
        
        try:
            code = varint.decode_stream(self._ComponentBinDeserializer__stream)
            obj = self._ComponentBinDeserializer__decodeCustomType(code)
        except EOFError:
            raise SerializationException('Cannot parse given stream')

        return obj

    
    def hasItem(self, data, path, value):
        self._ComponentBinDeserializer__stream = StringIO(data)
        
        try:
            code = varint.decode_stream(self._ComponentBinDeserializer__stream)
            self._ComponentBinDeserializer__decodeCustomType(code, path, value)
        except EOFError:
            raise SerializationException('Cannot parse given stream')
        except FoundItemException:
            return True

        return False

    
    def _ComponentBinDeserializer__decodeCustomType(self, itemType, path = None, wanted = None):
        cls = self.customTypes.get(itemType, None)
        if wanted is None:
            obj = cls()
        else:
            obj = None
        fields = cls.fields
        io = self._ComponentBinDeserializer__stream
        valueMap = varint.decode_stream(io)
        offset = 1
        for (k, t) in fields.iteritems():
            if t.flags & FieldFlags.NON_BIN:
                continue
            if IS_EDITOR and t.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
                continue
            if not path or path[0] != k:
                pass
            next = path[1]
            if valueMap & offset:
                ftype = t.type
                if ftype == FieldTypes.VARINT:
                    value = varint.decode_stream(io)
                elif ftype == FieldTypes.STRING:
                    value = self._ComponentBinDeserializer__decodeString()
                elif ftype == FieldTypes.APPLY_AREA_ENUM:
                    value = varint.decode_stream(io)
                elif ftype == FieldTypes.OPTIONS_ENUM:
                    value = varint.decode_stream(io)
                elif ftype & FieldTypes.TYPED_ARRAY:
                    value = self._ComponentBinDeserializer__decodeArray(ftype ^ FieldTypes.TYPED_ARRAY, k, path, next, wanted)
                elif ftype >= FieldTypes.CUSTOM_TYPE_OFFSET:
                    value = self._ComponentBinDeserializer__decodeCustomType(ftype / FieldTypes.CUSTOM_TYPE_OFFSET, next, wanted)
                else:
                    raise SerializationException('Unsupported field type index')
                if not (1.flags & FieldFlags.DEPRECATED) and hasattr(obj, k) or obj is None:
                    if wanted is None:
                        setattr(obj, k, value)
                    elif path and path[1] is None and path[0] == k and value == wanted:
                        raise FoundItemException()
                    
                
            offset <<= 1
        
        return obj

    
    def _ComponentBinDeserializer__decodeArray(self, itemType, k, path, next, wanted):
        io = self._ComponentBinDeserializer__stream
        n = varint.decode_stream(io)
        if itemType == FieldTypes.VARINT:
            continue
            array = [ varint.decode_stream(io) for _ in xrange(n) ]
            if path and path[1] is None and path[0] == k and wanted in array:
                raise FoundItemException()
            return array
        if None >= FieldTypes.CUSTOM_TYPE_OFFSET:
            customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
            continue
            return [ self._ComponentBinDeserializer__decodeCustomType(customType, next, wanted) for _ in xrange(n) ]
        raise None('Unsupported item type')

    
    def _ComponentBinDeserializer__decodeString(self):
        stream = self._ComponentBinDeserializer__stream
        return stream.read(varint.decode_stream(stream))



class ComponentXmlDeserializer(object):
    __slots__ = ('customTypes',)
    
    def __init__(self, customTypes):
        self.customTypes = customTypes
        super(ComponentXmlDeserializer, self).__init__()

    
    def decode(self, itemType, xmlCtx, section):
        obj = self._ComponentXmlDeserializer__decodeCustomType(itemType, xmlCtx, section)
        return obj

    
    def _ComponentXmlDeserializer__decodeCustomType(self, customType, ctx, section):
        cls = self.customTypes[customType]
        instance = cls()
        for (fname, finfo) in cls.fields.iteritems():
            if finfo.flags & FieldFlags.NON_XML:
                continue
            if not section.has_key(fname):
                if IS_EDITOR and finfo.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
                    editorOnlySection = getEditorOnlySection(section)
                    if editorOnlySection is not None and editorOnlySection.has_key(fname):
                        section = editorOnlySection
                    
                
            
        ftype = finfo.type
        if ftype == FieldTypes.VARINT:
            value = section.readInt(fname)
        elif ftype == FieldTypes.FLOAT:
            value = section.readFloat(fname)
        elif ftype == FieldTypes.APPLY_AREA_ENUM:
            value = self._ComponentXmlDeserializer__decodeEnum(section.readString(fname), ApplyArea)
        elif ftype == FieldTypes.TAGS:
            value = tuple(section.readString(fname).split())
        elif ftype == FieldTypes.STRING:
            value = section.readString(fname)
        elif ftype == FieldTypes.OPTIONS_ENUM:
            value = self._ComponentXmlDeserializer__decodeEnum(section.readString(fname), Options)
        elif ftype & FieldTypes.TYPED_ARRAY:
            itemType = ftype ^ FieldTypes.TYPED_ARRAY
            value = self._ComponentXmlDeserializer__decodeArray(itemType, (ctx, fname), section[fname])
        elif ftype >= FieldTypes.CUSTOM_TYPE_OFFSET:
            ftype = ftype / FieldTypes.CUSTOM_TYPE_OFFSET
            value = self._ComponentXmlDeserializer__decodeCustomType(ftype, (ctx, fname), section[fname])
        else:
            raise SerializationException('Unsupported item type')
        if not (None.flags & FieldFlags.DEPRECATED) or hasattr(instance, fname):
            setattr(instance, fname, value)
        if IS_EDITOR and finfo.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
            section = section.parentSection()
            continue
        return instance

    
    def _ComponentXmlDeserializer__decodeArray(self, itemType, ctx, section):
        result = []
        for (iname, isection) in enumerate(section.items()):
            if itemType == FieldTypes.VARINT:
                result.append(isection.asInt)
                continue
            if itemType == FieldTypes.FLOAT:
                result.append(isection.asFloat)
                continue
            if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
                customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
                ictx = (ctx, '{0} {1}'.format(iname, isection))
                result.append(self._ComponentXmlDeserializer__decodeCustomType(customType, ictx, isection))
                continue
            raise SerializationException('Unsupported item type')
        
        return result

    
    def _ComponentXmlDeserializer__decodeEnum(self, value, enum):
        return decodeEnum(value, enum)[0]



class EmptyComponent(SerializableComponent):
    pass


class PaintComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.PAINT
    fields = OrderedDict((('id', intField()), ('appliedTo', applyAreaEnumField(ApplyArea.PAINT_REGIO