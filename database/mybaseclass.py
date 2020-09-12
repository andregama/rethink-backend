import re
from logging import getLogger

from sqlalchemy import event

logger = getLogger()


class MyBase():

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):

        def should_print(key, value):
            if key[0] == '_':  # is private or protected
                return False
            return True

        def prune(obj):
            obj_str = '%s' % obj
            if len(obj_str) > 80:
                return re.sub('\s+', ' ', obj_str)[:80] + ' ...(pruned)'
            else:
                return obj_str

        class_name = type(self).__name__
        indentation = ' ' * (len(class_name) + 1)
        attributes = [
            "{0}{1}='{2!s}'".format(
                indentation,
                key,
                prune(self.__dict__[key])
            )
            for key in self.__dict__
            if should_print(key, self.__dict__[key])
        ]
        joined_attributes = ',\n'.join(attributes)
        return f'<{class_name}\n{joined_attributes}>'

    @staticmethod
    def log_insert(_, __, object):
        logger.info(f'Inserted at DB {object!s}\n{object!r}')

    @staticmethod
    def log_delete(_, __, object):
        logger.info(f'Deleted at DB {object!s}')

    @classmethod
    def __declare_last__(cls):
        # get called after mappings are completed
        # http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html#declare-last
        event.listen(cls, 'after_insert', cls.log_insert)
        event.listen(cls, 'after_delete', cls.log_delete)
