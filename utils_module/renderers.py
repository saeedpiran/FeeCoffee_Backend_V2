from rest_framework.renderers import JSONRenderer



# Response format
class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # If the response data is already wrapped, don't double wrap.
        if isinstance(data, dict) and 'success' in data:
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context.get('response')
        # Retrieve any message attached to the response
        message = getattr(response, "message", "")
        status_code = response.status_code if response else None

        if response is not None and response.exception:
            # If error data has a "detail" field, use that; otherwise use the error data as is.
            error_data = data.get("detail") if isinstance(data, dict) and "detail" in data else data
            formatted_data = {
                "success": False,
                # "status": status_code,
                "data": {},
                "error": error_data,
            }
        else:
            formatted_data = {
                "success": True,
                # "status": status_code,
                "data": data,
                "message": message,
            }
        return super().render(formatted_data, accepted_media_type, renderer_context)
