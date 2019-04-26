from yggdrasil.metaschema.datatypes import register_type
from yggdrasil.metaschema.datatypes import MetaschemaTypeError
from yggdrasil.metaschema.datatypes.MetaschemaType import MetaschemaType
from yggdrasil.metaschema.datatypes.JSONObjectMetaschemaType import (
    JSONObjectMetaschemaType)
from yggdrasil.metaschema.properties.ArgsMetaschemaProperty import (
    ArgsMetaschemaProperty)


@register_type
class InstanceMetaschemaType(MetaschemaType):
    r"""Type for evaluating instances of Python classes."""

    name = 'instance'
    description = 'Type for Python class instances.'
    properties = MetaschemaType.properties + ['class', 'args']
    definition_properties = MetaschemaType.definition_properties + ['class']
    metadata_properties = (MetaschemaType.metadata_properties
                           + ['class', 'args'])
    extract_properties = (MetaschemaType.extract_properties
                          + ['class', 'args'])
    python_types = (object, )

    @classmethod
    def validate(cls, obj, raise_errors=False):
        r"""Validate an object to check if it could be of this type.

        Args:
            obj (object): Object to validate.
            raise_errors (bool, optional): If True, errors will be raised when
                the object fails to be validated. Defaults to False.

        Returns:
            bool: True if the object could be of this type, False otherwise.

        """
        if super(InstanceMetaschemaType, cls).validate(obj,
                                                       raise_errors=raise_errors):
            try:
                ArgsMetaschemaProperty.instance2args(obj)
                return True
            except MetaschemaTypeError:
                if raise_errors:
                    raise ValueError("Class dosn't have an input_args attribute.")
                return False
        return False
        
    @classmethod
    def encode_data(cls, obj, typedef):
        r"""Encode an object's data.

        Args:
            obj (object): Object to encode.
            typedef (dict): Type definition that should be used to encode the
                object.

        Returns:
            string: Encoded object.

        """
        vtypedef = None
        if isinstance(typedef, dict):
            vtypedef = {'properties': typedef.get('args', {})}
        args = ArgsMetaschemaProperty.instance2args(obj)
        return JSONObjectMetaschemaType.encode_data(args, vtypedef)

    @classmethod
    def decode_data(cls, obj, typedef):
        r"""Decode an object.

        Args:
            obj (string): Encoded object to decode.
            typedef (dict): Type definition that should be used to decode the
                object.

        Returns:
            object: Decoded object.

        """
        # TODO: Normalization can be removed if metadata is normalized
        typedef = cls.normalize_definition(typedef)
        args = JSONObjectMetaschemaType.decode_data(
            obj, {'properties': typedef.get('args', {})})
        return typedef['class'](**args)
