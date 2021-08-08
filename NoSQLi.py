import uuid
import json
import logging
from pymongo import errors
from bson.objectid import ObjectId
from bson.json_util import dumps as bson_dumps
from datetime import datetime, timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import AssignmentCommentSerializer
from .validators import CommentAllowedValidator

from grades.models import Assignment

from api.permissions import IsNotFlagged

from app.mongodb import MongoConnection

logger = logging.getLogger(__name__)


class AssignmentCommentViewSet(viewsets.ViewSet):
    """
    API endpoint for assignment comments.
    """
    serializer_class = AssignmentCommentSerializer
    permission_classes = (IsAuthenticated, IsNotFlagged,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            mongo = MongoConnection()
            try:
                result = mongo.db.comments.insert_one({
                    'assignment_id': serializer.data.get('assignment_id'),
                    'username': str(request.user.userprofile),
                    'profile_uuid': request.user.userprofile.id,
                    'comment': serializer.data.get('comment'),
                    'created_on': datetime.now(timezone.utc).isoformat(),
                    'is_flagged': False
                })
                if result.inserted_id:
                    return Response(
                        json.loads(bson_dumps(mongo.db.comments.find_one(
                            {'_id': result.inserted_id}))))
            except errors.PyMongoError as e:
                logger.error(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        comment_allowed = CommentAllowedValidator(request, Assignment)
        try:
            mongo = MongoConnection()
            comment = mongo.db.comments.find(
                {'$where': (
                    'function() { '
                    'return this._id == "' + self.kwargs.get('object_id') + '"'
                    '}')}).limit(1)
            comment = json.loads(bson_dumps(comment))

            if not comment:
                return Response(status=status.HTTP_404_NOT_FOUND)

            return Response(comment[0])

        except errors.InvalidId as e:
            logger.error(e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        except errors.PyMongoError as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        comment_allowed = CommentAllowedValidator(request, Assignment)
        if comment_allowed.validate(self.kwargs.get('assignment_id')):
            try:
                mongo = MongoConnection()
                cursor = mongo.db.comments.find(
                    {'assignment_id': self.kwargs.get('assignment_id')})
                comments = json.loads(bson_dumps(cursor))
                if comments:
                    return Response(comments)

            except errors.PyMongoError as e:
                logger.error(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            mongo = MongoConnection()
            result = mongo.db.comments.update_one(
                {
                    '_id': ObjectId(self.kwargs.get('object_id')),
                    'username': request.user.username,
                    'profile_uuid': uuid.UUID(request.user.userprofile.pk),
                },
                {'$set': {'comment': request.POST.get('comment')}}
            )
            if result.matched_count:
                return Response(
                    json.loads(bson_dumps(mongo.db.comments.find_one(
                        {'_id': ObjectId(self.kwargs.get('object_id'))}))))

        except errors.InvalidId as e:
            logger.error(e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        except errors.PyMongoError as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_404_NOT_FOUND)
