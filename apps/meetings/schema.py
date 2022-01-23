import graphene
from django import http
from django.contrib.auth.models import User
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers

from utils.base_schema import DjangoDeleteMutation
from .models import MeetingSchedule, Meeting
from .serializers import MeetingSerializer, ReservedMeetingSerializer


class UserNode(DjangoObjectType):
    object_id = graphene.ID(source='pk', required=True)

    class Meta:
        model = User
        filter_fields = ['id', 'email', 'username', 'first_name', 'last_name']
        interfaces = (relay.Node,)


class MeetingScheduleNode(DjangoObjectType):
    object_id = graphene.ID(source='pk', required=True)
    is_reserved = graphene.Boolean(source='is_reserved')

    class Meta:
        model = MeetingSchedule
        filter_fields = ['available_at', 'meeting', 'is_active', 'id']
        interfaces = (relay.Node,)


class MeetingNode(DjangoObjectType):
    schedules = DjangoFilterConnectionField(MeetingScheduleNode)
    object_id = graphene.ID(source='pk', required=True)
    user = graphene.Field(UserNode)

    class Meta:
        model = Meeting
        filter_fields = ['title', 'user', 'is_active', 'id']
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
            try:
                instance = Meeting.objects.get(
                    id=input['id'], user=info.context.user
                )
                return {'instance': instance, 'data': input, 'partial': True}

            except Meeting.DoesNotExist:
                raise http.Http404(_("object does not exist."))
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


class DeleteMeetingMutation(DjangoDeleteMutation):
    class Meta:
        model = Meeting

    @classmethod
    def mutate(cls, root, info, filter_kwargs=None, **kwargs):
        filter_kwargs = {'id': kwargs['id'], "user": info.context.user}
        return super(DeleteMeetingMutation, cls).mutate(root, info, filter_kwargs, **kwargs)


class DeleteMeetingScheduleMutation(DjangoDeleteMutation):
    class Meta:
        model = MeetingSchedule

    @classmethod
    def mutate(cls, root, info, filter_kwargs=None, **kwargs):
        filter_kwargs = {'id': kwargs['id'], "meeting__user": info.context.user}
        return super(DeleteMeetingScheduleMutation, cls).mutate(root, info, filter_kwargs, **kwargs)


class CreateReservedMeetingMutation(SerializerMutation):
    class Meta:
        serializer_class = ReservedMeetingSerializer
        model_operations = ['create']


class MeetingQuery(ObjectType):
    meeting = relay.Node.Field(MeetingNode)
    meetings = DjangoFilterConnectionField(MeetingNode)

    my_meeting = relay.Node.Field(MyMeetingNode)
    my_meetings = DjangoFilterConnectionField(MyMeetingNode)


class MeetingMutation(graphene.ObjectType):
    create_update_meeting = CreateUpdateMeetingMutation.Field()
    delete_meeting = DeleteMeetingMutation.Field()

    delete_meeting_schedule = DeleteMeetingScheduleMutation.Field()

    create_reserved_meeting = CreateReservedMeetingMutation.Field()
