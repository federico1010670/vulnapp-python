import base64
import json
import pickle


def restore(blob):
    if not blob:
        return {}
    return pickle.loads(base64.b64decode(blob))


def restore_json(blob):
    if not blob:
        return {}
    return json.loads(base64.b64decode(blob))
