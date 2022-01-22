import graphene
from django import http
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers

from .models import MeetingSchedule, Meeting
from .serializers import MeetingSerializer


class MeetingScheduleNode(DjangoObjectType):
    class Meta:
        model = MeetingSchedule
        filter_fields = ['available_at', 'meeting', 'is_active']
        interfaces = (relay.Node,)


class MeetingNode(DjangoObjectType):
    schedules = graphene.List(MeetingScheduleNode)

    class Meta:
        model = Meeting
        filter_fields = ['title', 'user', 'is_active']
        interfaces = (relay.Node,)
        convert_choices_to_enum = False

    def resolve_schedules(root, info, **kwargs):
        return root.schedules.all()


class MyMeetingNode(DjangoObjectType):
    class Meta:
        model = Meeting
        filter_fields = ['title', 'user', 'is_active']
        interfaces = (relay.Node,)
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            raise PermissionDenied(_("anonymous users do not have access to this query."))
        queryset.filter(user=info.context.user)
        return queryset


class CreateUpdateMeetingMutation(SerializerMutation):
    class Meta:
        serializer_class = MeetingSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        convert_choices_to_enum = False

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if info.context.user.is_anonymous:
            raise PermissionDenied(_("anonymous users do not have access to mutation."))

        if 'id' in input:
            instance = Meeting.objects.filter(
                id=input['id'], user=info.context.user
            ).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}

            else:
                raise http.Http404
        return {'data': input, 'partial': True}

    @classmethod
    def perform_mutate(cls, serializer, info):
        obj = serializer.save(user=info.context.user)

        kwargs = {}
        for f, field in serializer.fields.items():
            if not field.write_only:
                if isinstance(field, serializers.SerializerMethodField):
                    kwargs[f] = field.to_representation(obj)
                else:
                    kwargs[f] = field.get_attribute(obj)

        return cls(errors=None, **kwargs)


class DeleteMeetingMutation(graphene.Mutation):
    deleted = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if info.context.user.is_anonymous:
            raise PermissionDenied(_("anonymous users do not have access to mutation."))

        obj = Meeting.objects.get(pk=kwargs["id"], user=info.context.user)
        obj.delete()
        return cls(deleted=True)


class MeetingQuery(ObjectType):
    meeting = relay.Node.Field(MeetingNode)
    meetings = DjangoFilterConnectionField(MeetingNode)

    my_meeting = relay.Node.Field(MyMeetingNode)
    my_meetings = DjangoFilterConnectionField(MyMeetingNode)


class MeetingMutation(graphene.ObjectType):
    create_update_meeting = CreateUpdateMeetingMutation.Field()
    delete_meeting = DeleteMeetingMutation.Field()

