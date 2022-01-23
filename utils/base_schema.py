from collections import OrderedDict

import graphene
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from graphene import Interface, Field
from graphene.types.mutation import MutationOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.get_unbound_function import get_unbound_function
from graphene.utils.props import props
from graphene_django.utils import is_valid_django_model


class DjangoDeleteMutation(graphene.Mutation):
    deleted = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            model=None,
            interfaces=(),
            resolver=None,
            output=None,
            arguments=None,
            _meta=None,
            **options
    ):
        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)
        if not _meta:
            _meta = MutationOptions(cls)

        output = output or getattr(cls, "Output", None)
        fields = {}

        for interface in interfaces:
            assert issubclass(interface, Interface), (
                'All interfaces of {} must be a subclass of Interface. Received "{}".'
            ).format(cls.__name__, interface)
            fields.update(interface._meta.fields)

        if not output:
            # If output is defined, we don't need to get the fields
            fields = OrderedDict()
            for base in reversed(cls.__mro__):
                fields.update(yank_fields_from_attrs(base.__dict__, _as=Field))
            output = cls

        if not arguments:
            input_class = getattr(cls, "Arguments", None)
            if not input_class:
                input_class = getattr(cls, "Input", None)
                if input_class:
                    warn_deprecation(
                        (
                            "Please use {name}.Arguments instead of {name}.Input."
                            "Input is now only used in ClientMutationID.\n"
                            "Read more:"
                            " https://github.com/graphql-python/graphene/blob/v2.0.0/UPGRADE-v2.0.md#mutation-input"
                        ).format(name=cls.__name__)
                    )

            if input_class:
                arguments = props(input_class)
            else:
                arguments = {}

        if not resolver:
            mutate = getattr(cls, "mutate", None)
            assert mutate, "All mutations must define a mutate method in it"
            resolver = get_unbound_function(mutate)

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        _meta.model = model
        _meta.interfaces = interfaces
        _meta.output = output
        _meta.resolver = resolver
        _meta.arguments = arguments

        super(DjangoDeleteMutation, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def mutate(cls, root, info, filter_kwargs=None, **kwargs):
        if filter_kwargs is None:
            filter_kwargs = {}
        assert filter_kwargs, (_("you must specify filter kwargs"))
        assert 'id' in filter_kwargs, (_("id is required in filter_kwargs"))
        if info.context.user.is_anonymous:
            raise PermissionDenied(_("anonymous users do not have access to mutation."))

        obj = cls._meta.model.objects.get(**filter_kwargs)
        obj.delete()
        return cls(deleted=True)
