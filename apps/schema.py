from graphene import ObjectType, Schema

from apps.meetings.schema import (MeetingQuery, MeetingMutation)


class Query(MeetingQuery, ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass


class Mutation(MeetingMutation, ObjectType):
    pass


schema = Schema(query=Query, mutation=Mutation)
