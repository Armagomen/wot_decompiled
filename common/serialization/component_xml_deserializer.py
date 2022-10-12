# File: c (Python 2.7)

from constants import IS_EDITOR
from items import decodeEnum
from items.components.c11n_constants import ApplyArea, Options
from items.utils import getEditorOnlySection
from serialization.definitions import FieldFlags, FieldTypes
from serialization.exceptions import SerializationException

__all__ = ('ComponentXmlDeserializer',)

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


