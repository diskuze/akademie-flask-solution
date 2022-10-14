import graphene
import requests
from flask import request
from graphene import Field
from graphene import InputObjectType
from graphene import Int
from graphene import List
from graphene import Mutation
from graphene import NonNull
from graphene import ObjectType
from graphene import Schema
from graphene import String

from diskuze import db
from diskuze import models


class Discussion(ObjectType):
    id = Int(required=True)
    canonical = String(required=True)

    comments = List(
        lambda: NonNull(Comment),
        required=True,
        first=Int(default_value=10),
        offset=Int(default_value=0),
    )

    @staticmethod
    def resolve_comments(root: models.Discussion, info, first, offset):
        return (
            db.session.query(models.Comment)
            .filter(models.Comment.discussion_id == root.id)
            .limit(first)
            .offset(offset)
            .all()
        )


class User(ObjectType):
    id = Int(required=True)
    nick = String(required=True)

    name = String()

    @staticmethod
    def resolve_name(root: models.User, info):
        response = requests.get(f"https://randomuser.me/api/?seed={root.id}")

        if response.status_code != 200:
            return None

        name = response.json()["results"][0]["name"]
        first, last = name["first"], name["last"]
        return f"{first} {last}"


class Comment(ObjectType):
    id = Int(required=True)
    content = String(required=True)

    reply_to = Field(lambda: Comment)
    replies = List(lambda: NonNull(Comment), required=True)

    discussion = NonNull(Discussion)
    user = NonNull(User)

    @staticmethod
    def resolve_reply_to(root: models.Comment, info):
        # TODO: data loader
        return root.reply_to

    @staticmethod
    def resolve_replies(root: models.Comment, info):
        return root.replies

    @staticmethod
    def resolve_discussion(root: models.Comment, info):
        # TODO: data loader
        return root.discussion

    @staticmethod
    def resolve_user(root: models.Comment, info):
        # TODO: data loader
        # return await user_loader.load(root.user_id)
        return root.user


class Query(ObjectType):
    hello = String(required=True, description="Says \"Hello World!\"")
    total = Int(required=True, description="Gives boring statistics about comments total")

    discussion = Field(
        Discussion,
        description="Discussion obtained by its canonical identifier",
        canonical=String(required=True),
    )

    @staticmethod
    def resolve_hello(root, info):
        return "Hello World!"

    @staticmethod
    def resolve_total(root, info):
        return db.session.query(models.Comment).count()

    @staticmethod
    def resolve_discussion(root, info, canonical):
        return db.session.query(models.Discussion).filter(models.Discussion.canonical == canonical).first()


class CommentInput(InputObjectType):
    content = String(required=True)
    discussion_canonical = String(required=True)
    reply_to = Int()


class CreateComment(Mutation):
    class Arguments:
        input_ = CommentInput(required=True, name="input")

    comment = graphene.Field(Comment)

    @staticmethod
    def mutate(root, info, input_):
        authorization = (request.headers.get("Authorization") or "").split(" ", 1)
        if len(authorization) < 2:
            return CreateComment()

        auth_type, nick = authorization
        if auth_type != "User":
            return CreateComment()

        session = db.session()

        user = (
            session.query(models.User)
            .filter(models.User.nick == nick)
            .first()
        )
        if not user:
            return CreateComment()

        if not input_.content:
            return CreateComment()

        discussion_id = (
            session.query(models.Discussion.id)
            .filter(models.Discussion.canonical == input_.discussion_canonical)
            .scalar()
        )

        if not discussion_id:
            return CreateComment()

        if input_.reply_to:
            reply_exists = (
                session.query(models.Comment)
                .filter(models.Comment.id == input_.reply_to)
                .exists()
            )

            if not reply_exists:
                return None

        comment = models.Comment(
            content=input_.content,
            reply_to_id=input_.reply_to,
            discussion_id=discussion_id,
            user_id=user.id,
        )
        session.add(comment)
        session.commit()

        return CreateComment(comment=comment)


class Mutation(ObjectType):
    create_comment = CreateComment.Field()


schema = Schema(Query, Mutation)
