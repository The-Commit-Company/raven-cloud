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
                {'name': 'channel_id', 'type': 'string', 'facet': True},
                {'name': 'content', 'type': 'string'},
                {'name': 'message_type', 'type': 'string'},
                {'name': 'is_thread', 'type': 'int32'},
                {'name': 'is_bot_message', 'type': 'int32'},
                {'name': 'bot', 'type': 'string'},
                {'name': 'owner', 'type': 'string'},
                {'name': 'creation', 'type': 'string'},
                {'name': 'mentions', 'type': 'string[]'}
        ]
    }
