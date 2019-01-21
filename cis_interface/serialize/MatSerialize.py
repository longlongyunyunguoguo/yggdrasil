import numpy as np
from scipy.io import savemat, loadmat
from cis_interface import backwards, platform
from cis_interface.serialize import register_serializer
from cis_interface.serialize.DefaultSerialize import DefaultSerialize


@register_serializer
class MatSerialize(DefaultSerialize):
    r"""Class for serializing a python object into a bytes message using the
    Matlab .mat format."""
    
    _seritype = 'mat'
    _schema_properties = {}
    _default_type = {'type': 'object'}

    def func_serialize(self, args):
        r"""Serialize a message.

        Args:
            args (obj): Python object to be serialized.

        Returns:
            bytes, str: Serialized message.

        Raises:
            TypeError: If args is not a dictionary.

        """
        if not isinstance(args, dict):
            raise TypeError('Object (type %s) is not a dictionary' %
                            type(args))
        fd = backwards.BytesIO()
        savemat(fd, args)
        out = fd.getvalue()
        fd.close()
        return out

    def func_deserialize(self, msg):
        r"""Deserialize a message.

        Args:
            msg (str, bytes): Message to be deserialized.

        Returns:
            obj: Deserialized Python object.

        """
        fd = backwards.BytesIO(msg)
        out = loadmat(fd, matlab_compatible=True)
        mat_keys = ['__header__', '__globals__', '__version__']
        for k in mat_keys:
            del out[k]
        fd.close()
        return out

    @classmethod
    def get_testing_options(cls):
        r"""Method to return a dictionary of testing options for this class.

        Returns:
            dict: Dictionary of variables to use for testing. Key/value pairs:
                kwargs (dict): Keyword arguments for comms tested with the
                    provided content.
                empty (object): Object produced from deserializing an empty
                    message.
                objects (list): List of objects to be serialized/deserialized.
                extra_kwargs (dict): Extra keyword arguments not used to
                    construct type definition.
                typedef (dict): Type definition resulting from the supplied
                    kwargs.
                dtype (np.dtype): Numpy data types that is consistent with the
                    determined type definition.

        """
        msg = {'a': np.array([[int(1)]]), 'b': np.array([[float(1)]])}
        out = super(MatSerialize, cls).get_testing_options()
        out['objects'] = [msg, msg]
        out['empty'] = dict()
        out['contents'] = cls().func_serialize(msg)
        out['contents'] = out['contents'].replace(b'\n', platform._newline)
        return out
