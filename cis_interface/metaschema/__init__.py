import os
import copy
import pprint
import jsonschema
import cis_interface
from cis_interface import backwards
from cis_interface.metaschema.encoder import encode_json, decode_json
from cis_interface.metaschema.properties import (
    get_registered_properties, import_all_properties)
from cis_interface.metaschema.datatypes import (
    get_registered_types, import_all_types)


# TODO: this should be included in release as YAML/JSON and then loaded
_metaschema_fbase = '.cis_metaschema.json'
_metaschema_fname = os.path.abspath(os.path.join(
    os.path.dirname(cis_interface.__file__), _metaschema_fbase))
_metaschema = None
_validator = None
_base_schema = {"$schema": ""}


if os.path.isfile(_metaschema_fname):
    with open(_metaschema_fname, 'r') as fd:
        _metaschema = decode_json(fd)
    schema_id = _metaschema.get('id', _metaschema.get('$id', None))
    assert(schema_id is not None)
    _metaschema.setdefault('$schema', schema_id)
    _base_schema['$schema'] = _metaschema.get('$schema', schema_id)

        
_base_validator = jsonschema.validators.validator_for(_base_schema)

        
def create_metaschema(overwrite=False):
    r"""Create the meta schema for validating cis schema.

    Args:
        overwrite (bool, optional): If True, the existing meta schema will be
            overwritten. If False and the metaschema exists, an error will be
            raised. Defaults to False.

    Returns:
        dict: Meta schema specifying rules for cis type schema. This includes
            all original JSON schema rules with the addition of types and
            property definitions.

    Raises:
        RuntimeError: If the file already exists and overwrite is False.

    """
    if (not overwrite) and os.path.isfile(_metaschema_fname):
        raise RuntimeError("Metaschema file already exists.")
    out = copy.deepcopy(_base_validator.META_SCHEMA)
    out['title'] = "Cis meta-schema for data type schemas"
    # TODO: Replace schema with a link to the metaschema in the documentation
    # del out['$schema']
    # Add properties
    for k, v in get_registered_properties().items():
        if v.schema is not None:
            assert(k not in out['properties'])
            out['properties'][k] = v.schema
    # Add types
    for k, v in sorted(get_registered_types().items()):
        if k not in out['definitions']['simpleTypes']['enum']:
            out['definitions']['simpleTypes']['enum'].append(k)
        for p in v.properties:
            assert(p in out['properties'])
    # Convert to unicode if python 2
    if backwards.PY2:  # pragma: Python 2
        out = backwards.as_unicode(out, recurse=True, convert_types=(str,),
                                   allow_pass=True)
    # Print
    print('Created metaschema')
    pprint.pprint(out)
    # Save it to a file
    with open(_metaschema_fname, 'w') as fd:
        encode_json(out, fd)
    return out


def get_metaschema():
    r"""Return the meta schema for validating cis schema.

    Returns:
        dict: Meta schema specifying rules for cis type schema. This includes
            all original JSON schema rules with the addition of types and
            property definitions.

    .. note:: This function should not be called at the module level as it can
              cause the metaschema (if it dosn't exist) to be generated before
              all of the necessary modules have been loaded.

    """
    global _metaschema
    if (_metaschema is None):
        _metaschema = create_metaschema()
    return copy.deepcopy(_metaschema)


def get_validator(overwrite=False, normalizers=None, **kwargs):
    r"""Return the validator that includes cis expansion types.

    Args:
        overwrite (bool, optional): If True, the existing validator will be
            overwritten. Defaults to False.
        normalizers (dict, optional): Additional normalizers to add.
        **kwargs: Additional keyword arguments are passed to normalizer.create.

    Returns:
        jsonschema.IValidator: JSON schema validator.

    """
    from cis_interface.metaschema import normalizer
    global _validator
    if (_validator is None) or overwrite:
        metaschema = get_metaschema()
        # Get set of validators
        all_validators = copy.deepcopy(_base_validator.VALIDATORS)
        for k, v in get_registered_properties().items():
            if (not v._replaces_existing):
                assert(k not in all_validators)
            all_validators[k] = v.wrapped_validate
        # Get set of datatypes
        # TODO: This will need to be changed with deprecation in jsonschema
        all_datatypes = copy.deepcopy(_base_validator.DEFAULT_TYPES)
        for k, v in get_registered_types().items():
            if (not v._replaces_existing):
                # Error raised on registration
                assert(k not in all_datatypes)
            all_datatypes[k] = v.python_types
        # Get set of normalizers
        if normalizers is None:
            normalizers = {}
        # Use default base and update validators
        _validator = normalizer.create(meta_schema=metaschema,
                                       validators=all_validators,
                                       normalizers=normalizers,
                                       default_types=all_datatypes, **kwargs)
        _validator._base_validator = _base_validator
    return _validator


def validate_schema(obj):
    r"""Validate a schema against the metaschema.

    Args:
        obj (dict): Schema to be validated.

    Raises:
        ValidationError: If the schema is not valid.

    """
    cls = get_validator()
    cls.check_schema(obj)


def validate_instance(obj, schema, **kwargs):
    r"""Validate an instance against a schema.

    Args:
        obj (object): Object to be validated using the provided schema.
        schema (dict): Schema to use to validate the provided object.
        **kwargs: Additional keyword arguments are passed to validate.

    Raises:
        ValidationError: If the object is not valid.

    """
    cls = get_validator()
    cls.check_schema(schema)
    return cls(schema).validate(obj, **kwargs)


def normalize_instance(obj, schema, **kwargs):
    r"""Normalize an object using the provided schema.

    Args:
        obj (object): Object to be normalized using the provided schema.
        schema (dict): Schema to use to normalize the provided object.
        **kwargs: Additional keyword arguments are passed to normalize.
    
    Returns:
        object: Normalized instance.

    """
    cls = get_validator()
    cls.check_schema(schema)
    return cls(schema).normalize(obj, **kwargs)


def import_all_classes():
    r"""Import all metaschema classes (types and properties)."""
    import_all_properties()
    import_all_types()


import_all_classes()
