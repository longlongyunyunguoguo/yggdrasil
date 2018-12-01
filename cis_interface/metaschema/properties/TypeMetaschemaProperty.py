from cis_interface.metaschema.datatypes import (
    get_registered_types, get_type_class, MetaschemaTypeError)
from cis_interface.metaschema.properties import register_metaschema_property
from cis_interface.metaschema.properties.MetaschemaProperty import MetaschemaProperty


def _specificity_sort_key(item):
    return -item[1].specificity


@register_metaschema_property
class TypeMetaschemaProperty(MetaschemaProperty):
    r"""Type property with validation of new properties."""

    name = 'type'

    @classmethod
    def encode(cls, instance):
        r"""Method to encode the property given the object.

        Args:
            instance (object): Object to get property for.

        Returns:
            object: Encoded property for instance.

        """
        type_registry = get_registered_types()
        for t, cls in sorted(type_registry.items(), key=_specificity_sort_key):
            if cls.validate(instance):
                return t
        raise MetaschemaTypeError(
            "Could not encode 'type' property for Python type: %s"
            % type(instance))

    @classmethod
    def compare(cls, prop1, prop2):
        r"""Method to determine compatiblity of one property value with another.
        This method is not necessarily symmetric in that the second value may
        not be compatible with the first even if the first is compatible with
        the second.

        Args:
            prop1 (object): Property value to compare against prop2.
            prop2 (object): Property value to compare against.
            
        Yields:
            str: Comparision failure messages.

        """
        type_cls = get_type_class(prop1)
        if not type_cls.issubtype(prop2):
            yield "Type '%s' is not a subtype of type '%s'" % (prop1, prop2)