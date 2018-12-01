import nose.tools as nt
from cis_interface.metaschema.datatypes.tests import test_MetaschemaType as parent


def valid_function():  # pragma: debug
    pass


class TestFunctionMetaschemaType(parent.TestMetaschemaType):
    r"""Test class for FunctionMetaschemaType class with float."""

    _mod = 'FunctionMetaschemaType'
    _cls = 'FunctionMetaschemaType'

    def __init__(self, *args, **kwargs):
        super(TestFunctionMetaschemaType, self).__init__(*args, **kwargs)
        self._value = valid_function
        self._valid_encoded = [self.typedef]
        self._valid_decoded = [self._value]
        self._invalid_encoded = [{}]
        self._invalid_decoded = [object]
        self._compatible_objects = [(self._value, self._value, None)]

    def test_decode_data_errors(self):
        r"""Test errors in decode_data."""
        nt.assert_raises(ValueError, self.import_cls.decode_data, 'hello', None)
        nt.assert_raises(AttributeError, self.import_cls.decode_data,
                         'cis_interface:invalid', None)