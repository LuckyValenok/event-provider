import datetime
import random
import string
from io import BytesIO

import qrcode
from PIL import Image
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from pyzbar.pyzbar import decode
from sqlalchemy import create_engine, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from data import config
from enums.friend_request_status import FriendRequestStatus
from enums.ranks import Rank
from enums.status_attendion import StatusAttendion
from enums.status_event import StatusEvent
from enums.steps import Step
from exceptions import NotFoundObjectError, ObjectAlreadyCreatedError
from models import User, EventUsers, Event, EventEditors, Achievement
from models.achievement import OrganizerToUserAchievement
from models.dbsession import DBSession
from models.event import EventCodes, EventFeedbacks, EventGroups, EventInterests
from models.user import UserFriends, OrganizerRateUser, UserGroups, UserInterests


def get_code_from_photo(_bytes: BytesIO):
    img = Image.open(_bytes)
    try:
        return decode(img)[-1].data.decode("utf-8")
    except IndexError:
        return None
    finally:
        img.close()
        _bytes.close()


def generate_image_achievements(user: User):
    achievements = user.achievements
    size = len(achievements)
    if size == 0:
        return None
    line_size = int(size / 4)
    if size % 4 != 0:
        line_size += 1
    new_image = Image.new('RGB', (size * 200 if line_size == 1 else 800, 200 * line_size), (250, 250, 250))
    x, y = 0, 0
    for achievement in user.achievements:
        _bytes = BytesIO(achievement.image)
        image = Image.open(_bytes)
        try:
            new_image.paste(image, (x, y))
        finally:
            _bytes.close()
            image.close()

        x += 200

        if x / 200 >= 4:
            y += 200
            x = 0
    try:
        output = BytesIO()
        new_image.save(output, 'JPEG')
        output.seek(0)
        return output
    finally:
        new_image.close()


class Controller:
    db_session = DBSession(sessionmaker(bind=create_engine(f'sqlite:///{config.DATABASE_NAME}', echo=True))())

    def manage_something_model(self, model, model_column, new_name, _lambda_creating_object, removing):
        if removing:
            try:
                self.db_session.delete_model(self.get_entity_by_model_with_name(model, model_column, new_name))
            except NoResultFound:
                raise NotFoundObjectError
        else:
            try:
                self.get_entity_by_model_with_name(model, model_column, new_name)
                raise ObjectAlreadyCreatedError
            except NoResultFound:
                self.db_session.add_model(_lambda_creating_object(new_name))

    def generate_qr_code(self, event, user) -> (str, BytesIO):
        code = self.get_new_code()

        self.add_code(event, user, code)

        img = qrcode.make(code)

        output = BytesIO()
        img.save(output, "PNG")
        output.seek(0)

        return code, output

    def create_event(self, name, creator):
        event = Event(name=name, status=StatusEvent.UNFINISHED)
        event.users.append(creator)
        self.db_session.add_model(event)

    def get_user_by_id(self, uid: int) -> User:
        return self.db_session.query(User).filter(User.id == uid).one()

    def has_user_by_id(self, uid: int) -> bool:
        return self.db_session.query(User).filter(User.id == uid).one_or_none() is not None

    def has_user_in_event(self, ev_id, uid: int) -> bool:
        return self.db_session.query(EventUsers).filter(EventUsers.user_id == uid,
                                                        EventUsers.event_id == ev_id).one_or_none() is not None

    def get_event_by_id(self, eid: int) -> Event:
        return self.db_session.query(Event).filter(Event.id == eid).one()

    def get_events_by_user(self, uid: int):
        return self.db_session.query(Event).filter(Event.users.any(User.id == uid)).all()

    def get_events_by_user_without_finished(self, uid: int):
        return self.db_session.query(Event).filter(Event.users.any(User.id == uid)).filter(
            Event.status == StatusEvent.UNFINISHED).all()

    def get_events_not_participate_user(self, uid: int):
        now = datetime.datetime.now()
        return self.db_session.query(Event).filter(~Event.users.any(User.id == uid)).filter(
            and_(Event.date != None, Event.date > now, Event.status == StatusEvent.UNFINISHED,
                 Event.description != None, Event.lng != None, Event.lat != None)).all()

    def get_count_visited(self, eid: int) -> int:
        return len(self.db_session.query(User).filter(
            and_(EventUsers.event_id == eid, EventUsers.status_attendion == StatusAttendion.ARRIVED)).all())

    def get_visited_users(self, eid: int):
        return self.db_session.query(User).filter(
            and_(EventUsers.user_id == User.id, EventUsers.event_id == eid,
                 EventUsers.status_attendion == StatusAttendion.ARRIVED, User.rank == Rank.USER)).all()

    def get_editor_event(self, uid: int) -> EventEditors:
        return self.db_session.query(EventEditors).filter(EventEditors.user_id == uid).one()

    def get_event_by_editor(self, uid: int) -> Event:
        event_id = self.db_session.query(EventEditors).filter(EventEditors.user_id == uid).one().event_id
        return self.get_event_by_id(event_id)

    def get_new_code(self) -> str:
        code = None
        while code is None or self.db_session.query(EventCodes).filter(EventCodes.code == code).count() > 0:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return code

    def get_code_model_by_id(self, eid: int, uid: int) -> EventCodes:
        return self.db_session.query(EventCodes).filter(
            and_(EventCodes.event_id == eid, EventCodes.user_id == uid)).one()

    def get_feedbacks(self, eid: int):
        return self.db_session.query(EventFeedbacks).filter(EventFeedbacks.event_id == eid).all()

    def get_feedbacks_statistics(self, eid):
        tokenizer = RegexTokenizer()
        model = FastTextSocialNetworkModel(tokenizer=tokenizer)

        messages = []

        for feedback in self.get_feedbacks(eid):
            messages.append(str(feedback.fb_text))

        results = model.predict(messages, k=2)
        neutral_list = []
        negative_list = []
        positive_list = []
        for sentiment in results:
            neutral = sentiment.get('neutral')
            negative = sentiment.get('negative')
            positive = sentiment.get('positive')
            if neutral is not None:
                neutral_list.append(sentiment.get('neutral'))
            if negative is not None:
                negative_list.append(sentiment.get('negative'))
            if positive is not None:
                positive_list.append(sentiment.get('positive'))

        return messages, neutral_list, negative_list, positive_list

    def get_entity_by_model_id(self, model, mid):
        return self.db_session.query(model).filter(model.id == mid).one()

    def get_entities_by_model(self, model):
        return self.db_session.query(model).all()

    def add_new_user(self, uid):
        self.db_session.add_model(model=User(id=uid, rank=Rank.USER, step=Step.FIRST_NAME, rating=0))

    def get_entity_by_model_with_name(self, model, model_column, name):
        return self.db_session.query(model).filter(model_column == name).one()

    def set_step_to_user(self, user, step):
        user.step = step
        self.db_session.commit_session()

    def add_feedback_to_event(self, user, feedback):
        editor = self.get_editor_event(user.id)
        eid = editor.event_id
        self.db_session.add_model(EventFeedbacks(event_id=eid, fb_text=feedback))
        self.db_session.delete_model(editor)

    def mark_presents(self, user, code):
        event_codes = self.db_session.query(EventCodes).filter(EventCodes.code == code).one()

        event_users = self.db_session.query(EventUsers).filter(
            and_(EventUsers.event_id == event_codes.event_id, EventUsers.user_id == event_codes.user_id)).one()
        event_users.status_attendion = StatusAttendion.ARRIVED

        self.db_session.delete_model(event_codes)
        self.db_session.delete_model(self.get_editor_event(user.id))

    def add_event_editor(self, event_id, user_id):
        self.db_session.add_model(EventEditors(event_id=event_id, user_id=user_id))

    def remove_code(self, event, user):
        self.db_session.delete_model(self.get_code_model_by_id(event.id, user.id))

    def add_code(self, event, user, code):
        self.db_session.add_model(EventCodes(event_id=event.id, user_id=user.id, code=code))

    def get_entities_by_model_with_relationship(self, entity, model, relation_model, relation_column,
                                                relation_column_entity_id, de_attach):
        return self.db_session.query(model).filter(model.id.not_in(
            self.db_session.query(relation_model).with_entities(relation_column).filter(
                relation_column_entity_id == entity.id))).all() if not de_attach \
            else self.db_session.query(model).filter(
            model.id.in_(self.db_session.query(relation_model).with_entities(relation_column)
                         .filter(relation_column_entity_id == entity.id))).all()

    def save(self):
        self.db_session.commit_session()

    def get_friend_list(self, user):
        return self.db_session.query(UserFriends, User).filter(UserFriends.user_id == user.id,
                                                               UserFriends.friend_id == User.id,
                                                               UserFriends.friend_request_status == FriendRequestStatus.ACCEPTED) \
            .with_entities(User.first_name, User.middle_name, User.last_name, UserFriends.friend_id).all()

    def add_friend(self, uid, fid, status):
        self.db_session.add_model(UserFriends(user_id=uid, friend_id=fid, friend_request_status=status))

    def get_friend_requests(self, uid):
        return self.db_session.query(UserFriends, User).filter(UserFriends.user_id == uid,
                                                               UserFriends.friend_id == User.id,
                                                               UserFriends.friend_request_status == FriendRequestStatus.WAITING) \
            .with_entities(User.first_name, User.middle_name, User.last_name, UserFriends.friend_id).all()

    def accept_friend_request(self, uid, fid):
        request = self.db_session.query(UserFriends).filter(UserFriends.user_id == uid,
                                                            UserFriends.friend_id == fid).one()
        request.friend_request_status = FriendRequestStatus.ACCEPTED
        self.db_session.commit_session()

    def decline_friend_request(self, uid, fid):
        request = self.db_session.query(UserFriends).filter(UserFriends.user_id == uid,
                                                            UserFriends.friend_id == fid).one()
        request2 = self.db_session.query(UserFriends).filter(UserFriends.user_id == fid,
                                                             UserFriends.friend_id == uid).one()
        self.db_session.delete_model(request)
        self.db_session.delete_model(request2)
        self.db_session.commit_session()

    def delete_friend(self, uid, fid):
        request = self.db_session.query(UserFriends).filter(UserFriends.user_id == uid, UserFriends.friend_id == fid,
                                                            UserFriends.friend_request_status == FriendRequestStatus.ACCEPTED).one()
        request2 = self.db_session.query(UserFriends).filter(UserFriends.user_id == fid, UserFriends.friend_id == uid,
                                                             UserFriends.friend_request_status == FriendRequestStatus.ACCEPTED).one()
        self.db_session.delete_model(request)
        self.db_session.delete_model(request2)
        self.db_session.commit_session()

    def give_rate(self, uid, amount: int):
        request = self.db_session.query(User).filter(User.id == uid).one()
        request.rating += amount
        self.db_session.commit_session()

    def get_rate_editor(self, oid):
        return self.db_session.query(OrganizerRateUser).filter(OrganizerRateUser.org_id == oid).one()

    def get_achievement_by_creator(self, user: User) -> Achievement:
        return self.db_session.query(Achievement).filter(
            and_(Achievement.creator == user.id, Achievement.image == None)).one()

    def get_achievement_list(self):
        return self.db_session.query(Achievement).all()

    def get_achievement_reciever(self, oid):
        return self.db_session.query(OrganizerToUserAchievement).filter(
            OrganizerToUserAchievement.organizer_id == oid).one()

    def get_achievement_by_id(self, aid: int):
        return self.db_session.query(Achievement).filter(Achievement.id == aid).one()

    def get_users_not_at_event(self, event: Event):
        query = self.db_session.query(User).filter(
            User.id.not_in(self.db_session.query(EventUsers).with_entities(EventUsers.user_id).filter(
                EventUsers.event_id == event.id)))
        if len(event.groups) > 0:
            query = query.filter(User.id.in_(
                self.db_session.query(EventGroups).join(UserGroups, EventGroups.group_id == UserGroups.group_id).filter(
                    EventGroups.event_id == event.id).with_entities(UserGroups.user_id)))
        if len(event.interests) > 0:
            query = query.filter(User.id.in_(self.db_session.query(EventInterests).join(UserInterests,
                                                                                        EventInterests.interest_id == UserInterests.interest_id).filter(
                EventInterests.event_id == event.id).with_entities(UserInterests.user_id)))
        return query.all()
