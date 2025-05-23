# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/abstract.py
import logging
from collections import namedtuple
import BigWorld
from AccountCommands import isCodeValid, RES_FAILURE, RES_SUCCESS
from helpers import isPlayerAccount
from ids_generators import Int32IDGenerator
from gui.shared.utils import code2str
from adisp import adisp_async, adisp_process
from gui.Scaleform.Waiting import Waiting
from gui.shared.utils.decorators import ReprInjector
_logger = logging.getLogger(__name__)

class AbstractRequester(object):

    def __init__(self):
        self._data = self._getDefaultDataValue()
        self.__synced = False

    @adisp_async
    @adisp_process
    def request(self, callback):
        _logger.debug('Prepare requester %s', self.__class__.__name__)
        self.__synced = False
        if not isPlayerAccount():
            yield lambda callback: callback(None)
            _logger.error('Player is not account, requester %s can not be invoked.', self.__class__.__name__)
        else:
            _logger.debug('Invoke requester %s', self.__class__.__name__)
            self._data = yield self._requestCache()
        callback(self)

    def isSynced(self):
        return self.__synced

    def clear(self):
        self._data = self._getDefaultDataValue()
        self.__synced = False

    def _response(self, resID, value, callback=None):
        _logger.debug('Response %r is received for requester %s', resID, self.__class__.__name__)
        self.__synced = resID >= 0
        if resID < 0:
            _logger.error('There is error while getting data from cache: %r, %r, %r', self.__class__.__name__, code2str(resID), resID)
            if callback is not None:
                callback(self._getDefaultDataValue())
        elif callback is not None:
            callback(self._preprocessValidData(value))
        return

    @adisp_async
    def _requestCache(self, callback):
        self._response(0, self._getDefaultDataValue(), callback)

    def _getDefaultDataValue(self):
        return None

    def _preprocessValidData(self, data):
        return data


class AbstractSyncDataRequester(AbstractRequester):

    def getCacheValue(self, key, defaultValue=None):
        return self._data[key] if key in self._data else defaultValue

    def getCacheValueByPath(self, path, defaultValue=None):
        value = self._data
        for key in path:
            if not isinstance(value, dict) or key not in value:
                return defaultValue
            value = value[key]

        return value

    def _getDefaultDataValue(self):
        return {}

    def _preprocessValidData(self, data):
        return dict(data)


@ReprInjector.simple(('getWaitingID', 'waitingID'), ('getRequestType', 'requestType'))
class RequestCtx(object):
    __slots__ = ('_waitingID', '_callback')

    def __init__(self, waitingID=''):
        self._waitingID = waitingID
        self._callback = None
        return

    def getRequestType(self):
        pass

    def getSingulizerKey(self):
        return None

    def getWaitingID(self):
        return self._waitingID

    def setWaitingID(self, waitingID):
        if not self.isProcessing():
            self._waitingID = waitingID
        else:
            _logger.error('In processing: %r', self)

    def isProcessing(self):
        return self._callback is not None

    def startProcessing(self, callback=None):
        if self._waitingID:
            Waiting.show(self._waitingID)
        if callback is not None and callable(callback):
            self._callback = callback
        return

    def stopProcessing(self, result=False, errorCode=None):
        if self._callback is not None:
            callback = self._callback
            self._callback = None
            callback(result if errorCode is None else (result, errorCode))
        if self._waitingID:
            Waiting.hide(self._waitingID)
        return

    def onResponseReceived(self, code):
        if code < 0:
            _logger.error('Server return error for request: %r, %r', code, self)
        self.stopProcessing(result=code >= 0)

    def clear(self):
        self._callback = None
        return

    def getCooldown(self):
        pass


class DataRequestCtx(RequestCtx):

    def stopProcessing(self, result=False, data=None):
        if self._callback is not None:
            self._callback(result, data)
            self._callback = None
        if self._waitingID:
            Waiting.hide(self._waitingID)
        return


class RequestsByIDProcessor(object):

    def __init__(self, idsGenerator=None):
        super(RequestsByIDProcessor, self).__init__()
        self._requests = {}
        self._idsGenerator = idsGenerator

    def init(self):
        pass

    def fini(self):
        self.stopProcessing()

    def stopProcessing(self, resCode=RES_SUCCESS):
        while self._requests:
            ctx, data = self._requests.popitem()
            data[0].stopProcessing(self._makeResponse(resCode, 'stop processing', ctx=ctx))

    def getSender(self):
        raise NotImplementedError

    def doRequest(self, ctx, methodName, *args, **kwargs):
        result, requestID = self._sendRequest(ctx, methodName, [], *args, **kwargs)
        if result:
            self._startProcessing(requestID, ctx)
        return result

    def doRequestChain(self, ctx, chain):
        result, requestID = self._sendNextRequest(ctx, chain)
        if result:
            self._startProcessing(requestID, ctx)
        return result

    def doRequestEx(self, ctx, callback, methodName, *args, **kwargs):
        result, requestID = self._sendRequest(ctx, methodName, [], *args, **kwargs)
        if result:
            self._startProcessing(requestID, ctx, callback)
        else:
            self._stopProcessing(ctx, 'request failure', callback)
        return result

    def doRequestChainEx(self, ctx, callback, chain):
        result, requestID = self._sendNextRequest(ctx, chain)
        if result:
            self._startProcessing(requestID, ctx, callback)
        else:
            self._stopProcessing(ctx, 'request failure', callback)
        return result

    def doRawRequest(self, methodName, *args, **kwargs):
        sender = self.getSender()
        method = getattr(sender, methodName)
        result = False
        if callable(method):
            method(*args, **kwargs)
            result = True
        else:
            _logger.error('Name of method is invalid: %r', methodName)
        return result

    def stopWithFailure(self, ctx, reason, callback=None):
        self._stopProcessing(ctx, reason, callback)

    def _startProcessing(self, requestID, ctx, callback=None):
        ctx.startProcessing(callback)

    def _stopProcessing(self, ctx, reason, callback=None):
        if callback is not None:
            callback(self._makeResponse(RES_FAILURE, reason, ctx=ctx))
        return

    def _onResponseReceived(self, requestID, result):
        if requestID > 0:
            ctx, chain = self._requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and chain:
                    BigWorld.callback(ctx.getCooldown(), lambda : self._sendNextRequest(ctx, chain))
                    return
                ctx.stopProcessing(result)
        else:
            self.stopProcessing()
        return

    def _doCall(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        return self._idsGenerator.next() if self._idsGenerator is not None else result

    def _getSenderMethod(self, sender, methodName):
        return getattr(sender, methodName, None)

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
        result, requestID = False, 0
        requester = self.getSender()
        if not requester:
            _logger.warning('There is not sender is present: %r', self)
            return (result, requestID)
        method = self._getSenderMethod(requester, methodName)
        if callable(method):
            requestID = self._doCall(method, *args, **kwargs)
            if requestID > 0:
                self._requests[requestID] = (ctx, chain)
                result = True
            else:
                _logger.error('Request ID can not be null')
        else:
            _logger.error('Name of method is invalid: %r', methodName)
        return (result, requestID)

    def _sendNextRequest(self, ctx, chain):
        methodName, args, kwargs = chain[0]
        return self._sendRequest(ctx, methodName, chain[1:], *args, **kwargs)

    def _makeResponse(self, code=0, txtMsg='', data=None, ctx=None):
        return isCodeValid(code)


class DataRequestsByIDProcessor(RequestsByIDProcessor):

    def __init__(self):
        super(DataRequestsByIDProcessor, self).__init__(Int32IDGenerator())

    def _onResponseReceived(self, requestID, result, data):
        if requestID > 0:
            ctx, chain = self._requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and chain:
                    self._sendNextRequest(ctx, chain)
                    return
                ctx.stopProcessing(result, data)
        else:
            self.stopProcessing()
        return

    def _doCall(self, method, *args, **kwargs):
        requestID = self._idsGenerator.next()
        method(requestID, *args, **kwargs)
        return requestID


_Response = namedtuple('_Response', ['code',
 'txtStr',
 'data',
 'extraCode',
 'headers'])
_Response.__new__.__defaults__ = (0, '', None, 0, None)

class Response(_Response):

    def isSuccess(self):
        return self.code == 0

    def getCode(self):
        return self.code

    def getExtraCode(self):
        return self.extraCode

    def getTxtString(self):
        return self.txtStr

    def getData(self):
        return self.data

    def getHeaders(self):
        return self.headers


class ClientRequestsByIDProcessor(RequestsByIDProcessor):

    def __init__(self, sender=None, responseClass=None, idsGenerator=None):
        super(ClientRequestsByIDProcessor, self).__init__(idsGenerator=idsGenerator or Int32IDGenerator())
        self.__responseClass = responseClass or Response
        self._sender = sender

    def getSender(self):
        return self._sender

    def fini(self):
        self._sender = None
        super(ClientRequestsByIDProcessor, self).fini()
        return

    def _doCall(self, method, *args, **kwargs):
        requestID = self._idsGenerator.next()

        def _callback(code, txtMsg, data):
            ctx = self._requests.get(requestID)
            self._onResponseReceived(requestID, self._makeResponse(code, txtMsg, data, ctx))

        method(callback=_callback, *args, **kwargs)
        return requestID

    def _makeResponse(self, code=0, txtMsg='', data=None, ctx=None, extraCode=0, headers=None):
        response = self.__responseClass(code, txtMsg, data, extraCode, headers)
        if not response.isSuccess():
            _logger.warning('Client request error: %r, %r', ctx, response)
        return response
