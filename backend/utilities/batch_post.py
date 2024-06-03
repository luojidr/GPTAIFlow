import requests

from config import BACKEND_URL


def post_bulk(path, data, user_id):
    url = f'http://{BACKEND_URL}//root'
    json = {
            "parameter": data,
            "path": path,
            "user_id": user_id
        }
    headers = {
        'X-Token': "cb3b666e3becfe56b90efa7a68749bd3b13f132f3ea2587b0819e03cdd31b9bf81e66e3ef11ddb604ecf599ba3af2643"
    }
    res = requests.post(url=url, json=json, headers=headers)
    return res