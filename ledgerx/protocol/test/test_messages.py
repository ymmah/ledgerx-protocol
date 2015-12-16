# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.test.test_messages
:synopsis: Unit tests for the messages module.
:author: Amr Ali <amr@ledgerx.com>
"""

import unittest

from ledgerx.protocol.detail import jsonapi, msgpack
from ledgerx.protocol.messages import (
        MessageField,
        MessageComplexField,
        MessageMeta,
        BaseMessage,
        BaseMessageParser,
        BaseMessageStatus,
        JsonMessage,
        MsgPackMessage,
        MessageIDMixin,
        MessageVersionMixin,
        MessageTypeMixin,
        MessageTimeMixin)

class TestMessage(unittest.TestCase):

    def test_base_message_meta(self):
        class _TestMsg(object, metaclass=MessageMeta):
            @MessageField
            def test_field(self): return getattr(self, '_x', None)
            @test_field.setter
            def test_field(self, val): self._x = val

        msg = _TestMsg()
        self.assertEqual(msg.test_field, None)
        msg.test_field = 'test'
        self.assertEqual(msg.test_field, 'test')
        self.assertIsInstance(msg.__fields__, list)
        self.assertIn('test_field', msg.__fields__)

    def test_base_message(self):
        class _TestMsg(BaseMessage):
            Serializer = jsonapi
            @MessageField
            def none_field(self): return None
            @none_field.setter
            def none_field(self, val): pass
            @MessageField
            def test(self): return self._test
            @test.setter
            def test(self, val): self._test = val
            def finalize(self): self.test = 'test'
        class _TestLatentMsg(_TestMsg):
            @MessageField
            def latent_field(self): return self._latent_field
            @latent_field.setter
            def latent_field(self, val): self._latent_field = val

        msg = _TestMsg()
        with self.assertRaises(NotImplementedError):
            msg.reply()

        data = msg.dumps()
        self.assertEqual(data, jsonapi.dumps({'test': 'test'}))
        self.assertIsNone(msg.none_field)
        self.assertEqual(msg.test, 'test')
        msg.augment(msg)
        self.assertEqual(msg.test, 'test')
        self.assertTrue(msg.fullfills(msg))
        self.assertTrue(msg.fullfills(_TestMsg))
        self.assertTrue(msg.fullfills(BaseMessage))

        jobj = jsonapi.loads(data)
        jobj['latent_field'] = 'test latent'
        msg_latent = _TestLatentMsg()
        msg.loads(jsonapi.dumps(jobj))
        self.assertEqual(msg.test, 'test')
        msg_latent.augment(msg)
        self.assertEqual(msg_latent.latent_field, 'test latent')
        self.assertTrue(msg_latent.fullfills(_TestMsg))
        self.assertTrue(msg_latent.fullfills(_TestLatentMsg))
        self.assertFalse(msg.fullfills(_TestLatentMsg))

        self.assertEqual(msg.Serializer, jsonapi)
        data = msg.dumps_custom(msgpack)
        self.assertEqual(msg.Serializer, jsonapi)
        self.assertEqual(data, msgpack.dumps({'test': 'test'}))
        msg.loads_custom(msgpack, data)
        self.assertEqual(msg.test, 'test')
        self.assertEqual(msg.Serializer, jsonapi)

    def test_message_complex_field(self):
        class Struct(object):
            def __init__(self, **entries):
                self.__dict__.update(entries)
        class _TestParentMsg(BaseMessage, MessageTypeMixin):
            Serializer = jsonapi
            mversion = '0.0.0'

            def reply(self, *args, **kwargs):
                return _TestStatus()
        class _TestStatus(_TestParentMsg):
            def set(self, code, message, data):
                self.status = code
                self.message = message
                self.data = data
            def client_error(self, message):
                self.message = message
                return self
            def server_error(self, message):
                self.message = message
                return self
        class _TestMsg(_TestParentMsg):
            Type = 'complex_message'
            @MessageComplexField
            def complex(self): return self._complex
            @complex.setter
            def complex(self, val): self._complex = val
            @MessageComplexField
            def complex_list(self): return self._complex_list
            @complex_list.setter
            def complex_list(self, val): self._complex_list = val
        class _TestNestedMsg(_TestParentMsg):
            Type = 'nested_message'
            @MessageField
            def name(self): return self._name
            @name.setter
            def name(self, val): self._name = val

        MessageTypes = {
                'complex_message': _TestMsg,
                'nested_message': _TestNestedMsg
                }
        class _TestMsgParser(BaseMessageParser):
            ParentMessage = _TestParentMsg
            MessageStatus = _TestStatus
            MessageVersions = {'0.0.0': Struct(MessageTypes=MessageTypes)}

        nested_msg1 = _TestNestedMsg()
        nested_msg1.name = 'test1'
        nested_msg2 = _TestNestedMsg()
        nested_msg2.name = 'test2'
        nested_msg3 = _TestNestedMsg()
        nested_msg3.name = 'test3'
        msg = _TestMsg()
        msg.complex = nested_msg1
        msg.complex_list = [nested_msg1, nested_msg2, nested_msg3]
        data = msg.dumps()
        obj = _TestMsgParser.parse(data)
        self.assertIsInstance(obj, _TestMsg)
        self.assertIsInstance(obj.complex, _TestNestedMsg)
        self.assertEqual(obj.complex.name, 'test1')
        self.assertIsInstance(obj.complex_list, list)
        for c in obj.complex_list:
            with self.subTest(c=c):
                self.assertIsInstance(c, _TestNestedMsg)
        self.assertEqual(obj.complex_list[0].name, 'test1')
        self.assertEqual(obj.complex_list[1].name, 'test2')
        self.assertEqual(obj.complex_list[2].name, 'test3')

    def test_base_message_parser(self):
        with self.assertRaises(TypeError):
            BaseMessageParser.parse('')

    def test_base_message_status(self):
        with self.assertRaises(TypeError):
            BaseMessageStatus()
        self.assertTrue(BaseMessageStatus.fullfills(BaseMessageStatus))

    def test_json_message(self):
        class _TestMsg(JsonMessage):
            @MessageField
            def name(self): return self._name
            @name.setter
            def name(self, val): self._name = val

        obj0 = _TestMsg()
        obj0.name = b'test'
        blob = obj0.dumps()
        obj1 = _TestMsg()
        obj1.loads(blob)
        self.assertIsInstance(obj1.name, str)
        self.assertEqual(obj0.name, obj1.name)

    def test_msgpack_message(self):
        class _TestMsg(MsgPackMessage):
            @MessageField
            def name(self): return self._name
            @name.setter
            def name(self, val): self._name = val

        obj0 = _TestMsg()
        obj0.name = b'test'
        blob = obj0.dumps()
        obj1 = _TestMsg()
        obj1.loads(blob)
        self.assertIsInstance(obj1.name, str)
        self.assertEqual(obj0.name, obj1.name)

    def test_message_id_mixin(self):
        class __TestMsg(MessageIDMixin): pass
        msg = __TestMsg()
        msg.generate_mid()
        mid = msg.mid
        self.assertEqual(mid, msg.mid)
        with self.assertRaises(ValueError):
            msg.mid = 'test'

        msg.mid = 'a' * __TestMsg.FIELD_LENGTH
        self.assertNotEqual(mid, msg.mid)
        self.assertEqual(msg.mid, 'a' * __TestMsg.FIELD_LENGTH)
        self.assertTrue(msg.fullfills(MessageIDMixin))

    def test_message_id_mixin_has_no_initial_mid(self):
        class __TestMsg(MessageIDMixin): pass
        msg = __TestMsg()
        self.assertEqual(msg.mid, None)

    def test_message_id_mixin_generate_mid_method(self):
        class __TestMsg(MessageIDMixin): pass
        msg = __TestMsg()
        initial_mid = msg.mid
        retval_mid = msg.generate_mid()
        final_mid = msg.mid
        self.assertNotEqual(initial_mid, final_mid)
        self.assertNotEqual(initial_mid, retval_mid)
        self.assertEqual(retval_mid, final_mid)
        self.assertEqual(msg.mid, final_mid)

    def test_message_version_mixin(self):
        class __TestMsg(MessageVersionMixin): pass
        msg = __TestMsg()
        with self.assertRaises(ValueError):
            msg.mversion = '0.0'
        self.assertEqual(msg.mversion, '0.0.0')
        msg.mversion = '0.0.1'
        self.assertEqual(msg.mversion, '0.0.1')
        self.assertTrue(msg.fullfills(MessageVersionMixin))

    def test_message_type_mixin(self):
        class __TestMsg(MessageTypeMixin): pass
        msg = __TestMsg()
        self.assertEqual(msg.type, None)
        msg.type = 'test'
        self.assertEqual(msg.type, 'test')
        self.assertTrue(msg.fullfills(MessageTypeMixin))

    def test_message_time_mixin(self):
        class __TestMsg(MessageTimeMixin): pass
        msg = __TestMsg()
        ts = msg.timestamp
        ti = msg.ticks
        self.assertEqual(msg.timestamp, ts)
        self.assertEqual(msg.ticks, ti)
        msg.refresh_timers()
        self.assertNotEqual(msg.ticks, ti)
        self.assertNotEqual(msg.timestamp, ts)
        self.assertTrue(msg.fullfills(MessageTimeMixin))


