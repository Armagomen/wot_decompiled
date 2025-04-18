# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/section2dict.py
import typing
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    TReaders = typing.Dict[str, typing.Callable[[DataSection], dict]]

def _parseDataSection(dataSection, readers=None, normalizeValues=False):
    if not len(dataSection):
        if normalizeValues:
            return _normalizeValue(dataSection.asString)
        else:
            return dataSection.asString
    result = {}
    for section in dataSection.values():
        if section.isAttribute:
            continue
        key = section.name
        if readers and key in readers:
            value = readers[key](section)
        else:
            value = _parseDataSection(section, readers, normalizeValues)
        if key in result:
            if isinstance(result[key], list):
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        result[key] = value

    return result


def _normalizeValue(value):
    if value.isdigit():
        value = int(value)
    else:
        try:
            value = float(value)
        except ValueError:
            pass

    return value


def parse(data, readers=None, normalizeValues=False):
    return {} if not len(data) else _parseDataSection(data, readers, normalizeValues)
