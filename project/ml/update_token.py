import os
import json
import requests


def update_token():
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    data = {"yandexPassportOauthToken":
            "y0_AgAAAAASxNSsAATuwQAAAAEMjb_-AAB-j8XVzcdFiaQsi2_SrstkwVHi8A"}
    response = requests.post(url, data=json.dumps(data)).json()
    os.environ["YC_IAM_TOKEN"] = response["iamToken"]
