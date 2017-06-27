import logging

from ask_amy.core.skill_factory import SkillFactory

from ask_amy.core.exceptions import SessionError
from ask_amy.core.object_dictionary import ObjectDictionary
from ask_amy.database.database import DynamoDB

logger = logging.getLogger()


class Session(ObjectDictionary):
    def __init__(self, session_dict):
        super().__init__(session_dict)

        self._persistence = False  # Assume no persistence until explicitlty defined
        config_dict = SkillFactory.load_configuartion(self.__class__.__name__)
        if config_dict:
            self._persistence = self.get_value_from_dict(['persistence'], config_dict)
            if self._persistence:
                self._table_name = self.get_value_from_dict(['tableName'], config_dict)
                self._fields_to_persist = self.get_value_from_dict(['fieldsToPersist'], config_dict)
                if self.get_value_from_dict(['new']):  # if new session load data
                    self.load()

    def _session_id(self):
        return self.get_value_from_dict(['sessionId'])
    session_id = property(_session_id)

    def _application_id(self):
        return self.get_value_from_dict(['application', 'applicationId'])
    application_id = property(_application_id)

    def _is_new_session(self):
        return self.get_value_from_dict(['new'])
    is_new_session = property(_is_new_session)

    def _user_id(self):
        return self.get_value_from_dict(['user', 'userId'])
    user_id = property(_user_id)

    def _access_token(self):
        return self.get_value_from_dict(['user', 'accessToken'])
    access_token = property(_access_token)

    def _consent_token(self):
        return self.get_value_from_dict(['user', 'permissions', 'consentToken'])
    consent_token = property(_consent_token)

    def _attributes(self):
        has_attributes = self.get_value_from_dict(['attributes'])
        if has_attributes is None:
            self._obj_dict['attributes'] = {}
        return self._obj_dict['attributes']
    attributes = property(_attributes)

    def attribute_exists(self,attribute):
        if attribute in self.attributes.keys():
            return True
        else:
            return False

    def put_attribute(self, name, value):
        logger.debug("**************** entering Session.put_attribute")
        logger.debug("name={} value={}".format(name, value))
        val = value
        obj_dict = self.get_value_from_dict(['attributes'])
        if obj_dict is None:
            self._obj_dict['attributes'] = {}
        try:
            self._obj_dict['attributes'][name] = value
        except KeyError:
            raise SessionError
        return val


    def get_attribute(self, path):
        path.insert(0, 'attributes')
        val = self.get_value_from_dict(path)
        return val

    def load(self):
        logger.debug("**************** entering Session.load")
        if self._persistence:
            dynamo_db = DynamoDB(self._table_name)
            session_data = dynamo_db.load(self.user_id)
            for name in session_data.keys():
                self.put_attribute(name, session_data[name]['value'])

    def save(self):
        logger.debug("**************** entering Session.save")
        if self._persistence:
            dynamo_db = DynamoDB(self._table_name)
            session_data = self.attributes
            dynamo_db.save(self.user_id, self._fields_to_persist, session_data)

    def reset_stored_values(self):
        logger.debug("**************** entering Session.reset_stored_values")
        if self._persistence:
            dynamo_db = DynamoDB(self._table_name)
            dynamo_db.update_data(self.user_id, DynamoDB.NAME, DynamoDB.SESSION_DATA, "{}")
