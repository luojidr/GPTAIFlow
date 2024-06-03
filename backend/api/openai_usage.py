from models import (
    OpenAIAppUsage,
)

class TokenUsageAPI:
    name = "token_usages"

    def create(self, payload):
        app_name = payload.get("app_name")
        input_tokens = payload.get("input_tokens")
        output_tokens = payload.get("output_tokens")
        input_str = payload.get("input_str")
        output_str = payload.get("output_str")
        model_type = payload.get("model_type")
        user_id = payload.get("user_id")
        try:
            OpenAIAppUsage.insert(
                {
                    OpenAIAppUsage.app_name: app_name,
                    OpenAIAppUsage.input_tokens: input_tokens,
                    OpenAIAppUsage.output_tokens: output_tokens,
                    OpenAIAppUsage.input_str: input_str,
                    OpenAIAppUsage.output_str: output_str,
                    OpenAIAppUsage.model_type: model_type,
                    OpenAIAppUsage.user_id: user_id,
                }
            ).execute()
            response = {"status": 200, "msg": "success", "data": {}}
            return response
        except Exception as e:
            print(e)
            response = {"status": 500, "msg": "failled", "data": {}}
            return response
