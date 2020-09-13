import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.orm import  sessionmaker
from logging import getLogger

import urllib
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

logger = getLogger(__name__)


def get_secret(secret:str)->str:
    credential = DefaultAzureCredential()
    KVUri = f"https://rethink-keyvault.vault.azure.net"
    client = SecretClient(vault_url=KVUri, credential=credential)
    retrieved_secret = client.get_secret(secret)
    return retrieved_secret.value

def start_session():
    server = "rethink-db.database.windows.net"
    database = "rethink-bd"
    username = get_secret("rethinkdb-username")
    password = get_secret("rethinkdb-password")

    driver = '{ODBC Driver 17 for SQL Server}'

    odbc_str = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;UID='+username+';DATABASE='+ database + ';PWD='+ password
    connect_str = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(odbc_str)

    engine = create_engine(connect_str)

    Session = sessionmaker(bind=engine)
    session = Session()
    event.listen(session, "after_flush", log_updates)

    return session


def log_updates(session, flush_context):

    def log_update(changed_attributes):
        logger.debug(f'Starting with {changed_attributes}')
        INDENTATION = ' ' * 4
        # changed_attributes_str = ''
        # for changed_attribute in changed_attributes:
        #     object_, key, value, old_value = changed_attribute
        #     changed_attributes_str += \
        #         f'{INDENTATION}{key}: {old_value} -> {value}\n'
        changed_attributes_str = tabulate(
            [[INDENTATION, c['key'], ':', str(c['old']), '->', str(c['new'])]
             for c in changed_attributes],
            tablefmt='plain'
        )
        logger.info(f'Updated at DB {object!s}\n' + changed_attributes_str)

    def get_old_value(attribute_state):
        history = attribute_state.history
        return history.deleted[0] if history.deleted else None

    def trigger_attribute_change_loggings(object_):

        changed_attributes = []
        for mapper_property in object_mapper(object_).iterate_properties:
            if isinstance(mapper_property, ColumnProperty):
                key = mapper_property.key
                attribute_state = inspect(object_).attrs.get(key)
                history = attribute_state.history

                if history.has_changes():
                    value = attribute_state.value
                    # old_value is None for new objects and old value for dirty objects
                    old_value = get_old_value(attribute_state)
                    changed_attributes.append(
                        {
                            'object': object_,
                            'key': key,
                            'new': value,
                            'old': old_value
                        }
                    )
        if(changed_attributes):
            log_update(changed_attributes)

    logger.debug(f'Starting with {session}')
    changed_objects = session.dirty  # session.new.union(session.dirty)
    for object in changed_objects:
        trigger_attribute_change_loggings(object)

