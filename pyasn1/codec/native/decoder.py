#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pyasn1/license.html
#
from pyasn1 import debug
from pyasn1 import error
from pyasn1.type import base
from pyasn1.type import char
from pyasn1.type import tag
from pyasn1.type import univ
from pyasn1.type import useful

__all__ = ['decode']

LOG = debug.registerLoggee(__name__, flags=debug.DEBUG_DECODER)


class AbstractScalarPayloadDecoder(object):
    def __call__(self, pyObject, asn1Spec, decodeFun=None, **options):
        return asn1Spec.clone(pyObject)


class BitStringPayloadDecoder(AbstractScalarPayloadDecoder):
    def __call__(self, pyObject, asn1Spec, decodeFun=None, **options):
        return asn1Spec.clone(univ.BitString.fromBinaryString(pyObject))


class SequenceOrSetPayloadDecoder(object):
    def __call__(self, pyObject, asn1Spec, decodeFun=None, **options):
        asn1Value = asn1Spec.clone()

        componentsTypes = asn1Spec.componentType

        for field in asn1Value:
            if field in pyObject:
                asn1Value[field] = decodeFun(pyObject[field], componentsTypes[field].asn1Object, **options)

        return asn1Value


class SequenceOfOrSetOfPayloadDecoder(object):
    def __call__(self, pyObject, asn1Spec, decodeFun=None, **options):
        asn1Value = asn1Spec.clone()

        for pyValue in pyObject:
            asn1Value.append(decodeFun(pyValue, asn1Spec.componentType), **options)

        return asn1Value


class ChoicePayloadDecoder(object):
    def __call__(self, pyObject, asn1Spec, decodeFun=None, **options):
        asn1Value = asn1Spec.clone()

        componentsTypes = asn1Spec.componentType

        for field in pyObject:
            if field in componentsTypes:
                asn1Value[field] = decodeFun(pyObject[field], componentsTypes[field].asn1Object, **options)
                break

        return asn1Value


TAG_MAP = {
    univ.Integer.tagSet: AbstractScalarPayloadDecoder(),
    univ.Boolean.tagSet: AbstractScalarPayloadDecoder(),
    univ.BitString.tagSet: BitStringPayloadDecoder(),
    univ.OctetString.tagSet: AbstractScalarPayloadDecoder(),
    univ.Null.tagSet: AbstractScalarPayloadDecoder(),
    univ.ObjectIdentifier.tagSet: AbstractScalarPayloadDecoder(),
    univ.Enumerated.tagSet: AbstractScalarPayloadDecoder(),
    univ.Real.tagSet: AbstractScalarPayloadDecoder(),
    univ.Sequence.tagSet: SequenceOrSetPayloadDecoder(),  # conflicts with SequenceOf
    univ.Set.tagSet: SequenceOrSetPayloadDecoder(),  # conflicts with SetOf
    univ.Choice.tagSet: ChoicePayloadDecoder(),  # conflicts with Any
    # character string types
    char.UTF8String.tagSet: AbstractScalarPayloadDecoder(),
    char.NumericString.tagSet: AbstractScalarPayloadDecoder(),
    char.PrintableString.tagSet: AbstractScalarPayloadDecoder(),
    char.TeletexString.tagSet: AbstractScalarPayloadDecoder(),
    char.VideotexString.tagSet: AbstractScalarPayloadDecoder(),
    char.IA5String.tagSet: AbstractScalarPayloadDecoder(),
    char.GraphicString.tagSet: AbstractScalarPayloadDecoder(),
    char.VisibleString.tagSet: AbstractScalarPayloadDecoder(),
    char.GeneralString.tagSet: AbstractScalarPayloadDecoder(),
    char.UniversalString.tagSet: AbstractScalarPayloadDecoder(),
    char.BMPString.tagSet: AbstractScalarPayloadDecoder(),
    # useful types
    useful.ObjectDescriptor.tagSet: AbstractScalarPayloadDecoder(),
    useful.GeneralizedTime.tagSet: AbstractScalarPayloadDecoder(),
    useful.UTCTime.tagSet: AbstractScalarPayloadDecoder()
}

# Put in ambiguous & non-ambiguous types for faster codec lookup
TYPE_MAP = {
    univ.Integer.typeId: AbstractScalarPayloadDecoder(),
    univ.Boolean.typeId: AbstractScalarPayloadDecoder(),
    univ.BitString.typeId: BitStringPayloadDecoder(),
    univ.OctetString.typeId: AbstractScalarPayloadDecoder(),
    univ.Null.typeId: AbstractScalarPayloadDecoder(),
    univ.ObjectIdentifier.typeId: AbstractScalarPayloadDecoder(),
    univ.Enumerated.typeId: AbstractScalarPayloadDecoder(),
    univ.Real.typeId: AbstractScalarPayloadDecoder(),
    # ambiguous base types
    univ.Set.typeId: SequenceOrSetPayloadDecoder(),
    univ.SetOf.typeId: SequenceOfOrSetOfPayloadDecoder(),
    univ.Sequence.typeId: SequenceOrSetPayloadDecoder(),
    univ.SequenceOf.typeId: SequenceOfOrSetOfPayloadDecoder(),
    univ.Choice.typeId: ChoicePayloadDecoder(),
    univ.Any.typeId: AbstractScalarPayloadDecoder(),
    # character string types
    char.UTF8String.typeId: AbstractScalarPayloadDecoder(),
    char.NumericString.typeId: AbstractScalarPayloadDecoder(),
    char.PrintableString.typeId: AbstractScalarPayloadDecoder(),
    char.TeletexString.typeId: AbstractScalarPayloadDecoder(),
    char.VideotexString.typeId: AbstractScalarPayloadDecoder(),
    char.IA5String.typeId: AbstractScalarPayloadDecoder(),
    char.GraphicString.typeId: AbstractScalarPayloadDecoder(),
    char.VisibleString.typeId: AbstractScalarPayloadDecoder(),
    char.GeneralString.typeId: AbstractScalarPayloadDecoder(),
    char.UniversalString.typeId: AbstractScalarPayloadDecoder(),
    char.BMPString.typeId: AbstractScalarPayloadDecoder(),
    # useful types
    useful.ObjectDescriptor.typeId: AbstractScalarPayloadDecoder(),
    useful.GeneralizedTime.typeId: AbstractScalarPayloadDecoder(),
    useful.UTCTime.typeId: AbstractScalarPayloadDecoder()
}


class SingleItemDecoder(object):

    TAG_MAP = TAG_MAP
    TYPE_MAP = TYPE_MAP

    def __init__(self, **options):
        self._tagMap = options.get('tagMap', self.TAG_MAP)
        self._typeMap = options.get('typeMap', self.TYPE_MAP)

    def __call__(self, pyObject, asn1Spec, **options):

        if LOG:
            debug.scope.push(type(pyObject).__name__)
            LOG('decoder called at scope %s, working with '
                'type %s' % (debug.scope, type(pyObject).__name__))

        if asn1Spec is None or not isinstance(asn1Spec, base.Asn1Item):
            raise error.PyAsn1Error(
                'asn1Spec is not valid (should be an instance of an ASN.1 '
                'Item, not %s)' % asn1Spec.__class__.__name__)

        try:
            valueDecoder = self._typeMap[asn1Spec.typeId]

        except KeyError:
            # use base type for codec lookup to recover untagged types
            baseTagSet = tag.TagSet(asn1Spec.tagSet.baseTag, asn1Spec.tagSet.baseTag)

            try:
                valueDecoder = self._tagMap[baseTagSet]

            except KeyError:
                raise error.PyAsn1Error('Unknown ASN.1 tag %s' % asn1Spec.tagSet)

        if LOG:
            LOG('calling decoder %s on Python type %s '
                '<%s>' % (type(valueDecoder).__name__,
                          type(pyObject).__name__, repr(pyObject)))

        value = valueDecoder(pyObject, asn1Spec, self, **options)

        if LOG:
            LOG('decoder %s produced ASN.1 type %s '
                '<%s>' % (type(valueDecoder).__name__,
                          type(value).__name__, repr(value)))
            debug.scope.pop()

        return value


class Decoder(object):
    SINGLE_ITEM_DECODER = SingleItemDecoder

    def __init__(self, **options):
        self._singleItemDecoder = self.SINGLE_ITEM_DECODER(**options)

    def __call__(self, pyObject, asn1Spec=None, **kwargs):
        return self._singleItemDecoder(pyObject, asn1Spec=asn1Spec, **kwargs)


#: Turns Python objects of built-in types into ASN.1 objects.
#:
#: Takes Python objects of built-in types and turns them into a tree of
#: ASN.1 objects (e.g. :py:class:`~pyasn1.type.base.PyAsn1Item` derivative) which
#: may be a scalar or an arbitrary nested structure.
#:
#: Parameters
#: ----------
#: pyObject: :py:class:`object`
#:     A scalar or nested Python objects
#:
#: Keyword Args
#: ------------
#: asn1Spec: any pyasn1 type object e.g. :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
#:     A pyasn1 type object to act as a template guiding the decoder. It is required
#:     for successful interpretation of Python objects mapping into their ASN.1
#:     representations.
#:
#: Returns
#: -------
#: : :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
#:     A scalar or constructed pyasn1 object
#:
#: Raises
#: ------
#: ~pyasn1.error.PyAsn1Error
#:     On decoding errors
#:
#: Examples
#: --------
#: Decode native Python object into ASN.1 objects with ASN.1 schema
#:
#: .. code-block:: pycon
#:
#:    >>> seq = SequenceOf(componentType=Integer())
#:    >>> s, _ = decode([1, 2, 3], asn1Spec=seq)
#:    >>> str(s)
#:    SequenceOf:
#:     1 2 3
#:
decode = Decoder()
