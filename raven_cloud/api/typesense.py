import typesense
import frappe


def get_typesense_client():

    typesense_configuration = frappe.get_cached_doc(
        "RC Typesense Configuration")

    host = typesense_configuration.host
    port = typesense_configuration.port
    api_key = typesense_configuration.api_key
    protocol = typesense_configuration.protocol

    client = typesense.Client({
        'nodes': [{
            'host': host,
            'port': port,
            'protocol': protocol,
        }],
        'api_key': api_key,
        'connection_timeout_seconds': 5,
    })

    return client


def get_collection_schema(hash):

    return {
        'name': f'{hash}_messages',
        'fields': [
                {'name': 'id', 'type': 'string'},
                {'name': 'parent_channel_id', 'type': 'string', 'facet': True},
                {'name': 'channel_id', 'type': 'string'},
                {'name': 'content', 'type': 'string', 'stem': True},
                {'name': 'message_type', 'type': 'string'},
                {'name': 'file_type', 'type': 'string', 'optional': True},
                {'name': 'is_thread', 'type': 'int32'},
                {'name': 'is_bot_message', 'type': 'int32'},
                {'name': 'bot', 'type': 'string', 'optional': True},
                {'name': 'owner', 'type': 'string'},
                {'name': 'creation', 'type': 'string'},
                {'name': 'mentions', 'type': 'string[]', 'optional': True}
        ]
    }
