import requests
import json
url = "http://127.0.0.1:5000/kill_rid"
payload = json.dumps({
  "rid": "69f0f1cc97d54c23917034bc7a5fbe6b"
})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
