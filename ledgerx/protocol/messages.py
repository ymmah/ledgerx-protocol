# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.messages
:synopsis: Messages structure and encoding facilities module.
:author: Amr Ali <amr@ledgerx.com>
"""

import sys
import abc
import logging

from uuid import uuid4
from types import MethodType
from semantic_version import Version

from ledgerx.protocol.system import realtime, monotonic
from ledgerx.protocol.detail import msgpack, jsonapi

_asstr = lambda x: x.decode('utf8') if isinstance(x, bytes) else x

def record_message_type(klass):
    """\
    A decorator to build a append a message to the MessageTypes dictionary.
    """
    module = sys.modules[klass.__module__]
    if not hasattr(module, 'MessageTypes'):
        module.MessageTypes = {}
    module.MessageTypes.update({klass.Type: klass})
    return klass

class MessageField(property): pass

class MessageMeta(abc.ABCMeta):
    """\
    Keep track of MessageFields in __fields__.
    """
    attr_name = '__fields__'

    def __new__(cls, name, bases, attrs):
        mfields = filter(lambda x:
                not x[0].startswith('_') and
                type(x[1]) is MessageField, attrs.items())
        mfields = list(map(lambda x: x[0], mfields))
        if cls.attr_name not in attrs:
            attrs[cls.attr_name] = []
        for base in bases:
            if cls.attr_name in base.__dict__:
                attrs[cls.attr_name].extend(base.__fields__)
        attrs[cls.attr_name].extend(mfields)
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        setattr(cls, 'fullfills', MethodType(cls.__fullfills, cls))

    def __call__(cls, *args, **kwargs):
        o = super().__call__(*args, **kwargs)
        o.__dict__.update(
                dict.fromkeys(
                    map('_{0}'.format, o.__fields__)
                    )
                )
        return o

    @staticmethod
    def __fullfills(cls, other):
        """\
        A method to check if `cls` fullfills `other`'s message interface.
        """
        return set(cls.__fields__).issuperset(other.__fields__)

class MessageIDMixin(object, metaclass=MessageMeta):
    """\
    A message that includes a UUID field according to RFC-4122.
    """

    @MessageField
    def mid(self):
        if not self._mid:
            self._mid = uuid4().hex
        return self._mid

    @mid.setter
    def mid(self, val):
        self._mid = val

class MessageVersionMixin(object, metaclass=MessageMeta):
    """\
    A message that includes a version field.
    """
    Version = Version('0.0.0')

    @MessageField
    def mversion(self):
        if not self._mversion:
            self._mversion = self.Version
        return str(self._mversion)

    @mversion.setter
    def mversion(self, val):
        self._mversion = Version(val)

class MessageTypeMixin(object, metaclass=MessageMeta):
    """\
    A message that includes a type field.
    """
    Type = None

    @MessageField
    def type(self):
        if not self._type:
            self._type = self.Type
        return self._type

    @type.setter
    def type(self, val):
        self._type = val

class MessageTimeMixin(object, metaclass=MessageMeta):
    """\
    A message that includes timer fields.
    """

    @MessageField
    def timestamp(self):
        if not self._timestamp:
            self._timestamp = realtime()
        return int(self._timestamp * 1e9)

    @timestamp.setter
    def timestamp(self, val):
        pass

    @MessageField
    def ticks(self):
        if not self._ticks:
            self._ticks = monotonic()
        return int(self._ticks * 1e9)

    @ticks.setter
    def ticks(self, val):
        pass

    def refresh_timers(self):
        """\
        Update both the timestamp and ticks fields.
        """
        self._timestamp = realtime()
        self._ticks = monotonic()

class BaseMessage(object, metaclass=MessageMeta):
    """\
    Base message contract to enforce a certain interface on all messages.
    """
    Serializer = None # must support pickle's interface

    def __setattr__(self, key, val):
        """\
        Make sure that all bytes set through this interface are decoded to
        unicode.
        """
        super().__setattr__(key, _asstr(val))

    def reply(self):
        """\
        Create a status message with the same message ID.
        """
        raise NotImplementedError("reply method is not implemented")

    def finalize(self):
        """\
        A final operation to be made before serializing this message.
        Note that this method return value is ignored as it is supposed
        to be used to carry out final preparations on the message before
        serialization.
        """
        pass

    def augment(self, other):
        """\
        A method to add a deserialized message (i.e., other) members to `self`.
        """
        fields = set(self.__fields__).intersection(other.__dict__).union(
                other.__fields__)
        try:
            for k in fields:
                setattr(self, k, getattr(other, k))
        except AttributeError as ex:
            raise AttributeError(
                    "error occurred while setting '{}' attribute".format(k)) from ex

    def dumps(self):
        """\
        A method to serialize members of this instance to a particular format.
        """
        self.finalize()
        obj = {k: v for k, v in map(lambda x: (x, getattr(self, x)), self.__fields__) if v != None}
        return self.Serializer.dumps(obj)

    def loads(self, data):
        """\
        A method to deserialize a message into this object.

        :param data: A specially formatted string.
        """
        obj = self.Serializer.loads(data)
        [setattr(self, k, v)
                for k, v in map(lambda x: (_asstr(x[0]), x[1]), obj.items())
                if not k.startswith('_')]

class BaseMessageParser(object):
    """\
    An abstract message parser to determine message type and version.
    """
    ParentMessage = None
    MessageStatus = None
    MessageVersions = {} # e.g., {version: <module>}

    @classmethod
    def parse(cls, data):
        """\
        Parse data and determine message type and version.

        :returns:
            A new object of the supplied message type.
        """
        logger = logging.getLogger('ledgerx.protocol')
        try:
            obj = cls.ParentMessage()
            obj.loads(data)
        except:
            logger.exception("unable to parse a message")
            return cls.MessageStatus().client_error("unable to parse message")

        try:
            if obj.mversion not in cls.MessageVersions:
                return obj.reply().client_error("unsupported message version")
        except ValueError:
            return obj.reply().client_error("invalid message version")
        except:
            logger.exception("error occurred while parsing message version")
            return obj.reply().server_error(
                    "error occurred while parsing message version")

        mtypes = cls.MessageVersions[obj.mversion].MessageTypes
        if obj.type not in mtypes:
            return obj.reply().client_error("unsupported message type")
        mobj = mtypes[obj.type]()
        mobj.augment(obj)
        return mobj

class BaseMessageStatus(MessageTypeMixin):
    """\
    An abstract status message to report the status of a previous message.
    """
    Type = 'status'

    @MessageField
    def status(self):
        return self._status

    @status.setter
    def status(self, val):
        self._status = val

    @MessageField
    def message(self):
        return self._message

    @message.setter
    def message(self, val):
        self._message = val

    @MessageField
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    @abc.abstractmethod
    def set(self, code, message, data):
        """\
        Set status message attributes.
        """
        pass

    @abc.abstractmethod
    def client_error(self, message):
        """\
        An abstract method to return a client error status message.
        """
        pass

    @abc.abstractmethod
    def server_error(self, message):
        """\
        An abstract method to return a server error status message.
        """
        pass

class JsonMessage(BaseMessage):
    """\
    A message object that can be serialized to a JSON string.
    """
    Serializer = jsonapi

class MsgPackMessage(BaseMessage):
    """\
    A message object that can be serialized to `msgpack` format.
    """
    Serializer = msgpack

