from django.conf import settings
import requests
from django.core.cache import cache


class MSBService:
    url_base = f"{settings.MSB_API_URL}/sbmob/api"
    api_slug = "api"
    melding_mutatieregels_slug = "mutatieregels"
    user_info_slug = "gebruikersinfo"
    default_timeout = (5, 10)
    cache_timeout = 60 * 5
    GET = "get"
    POST = "post"

    @staticmethod
    def get_user_token_from_request(request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        auth_parts = auth_header.split(" ") if auth_header else []
        if len(auth_parts) == 2 and auth_parts[0] == "Bearer":
            return auth_parts[1]


    @staticmethod
    def do_request(url, user_token, method=GET, data={}):
        json_response = cache.get(url)
        action = getattr(requests, method, MSBService.GET)
        if not json_response:
            response = action(
                url=url,
                data=data,
                headers={
                    "Authorization": f"Bearer user_token"
                },
                timeout=MSBService.default_timeout,
            )
            json_response = response.json()
            cache.set(url, json_response, MSBService.cache_timeout)
        else:
            print(f"fetch from cache: {url}")
        return json_response

    @staticmethod
    def login():
        url=f"{MSBService.url_base}/login"
        return MSBService.do_request(url, MSBService.POST)

    @staticmethod
    def get_user_info(user_token):
        url=f"{MSBService.url_base}/{MSBService.user_info_slug}"
        return MSBService.do_request(url)

    @staticmethod
    def get_list(user_token, data={}):
        default_data = {"x":92441,"y":437718,"radius":400}
        data = data.dict()
        data.update(default_data)
        url=f"{MSBService.url_base}/msb/openmeldingen"
        return MSBService.do_request(url, user_token, MSBService.POST, data)

    @staticmethod
    def get_detail(melding_id, user_token):
        url=f"{MSBService.url_base}/msb/melding/{melding_id}"
        return MSBService.do_request(url, user_token)

    @staticmethod
    def get_mutatieregels(melding_id, user_token):
        url=f"{MSBService.url_base}/msb/melding/{melding_id}/mutatieregels"
        return MSBService.do_request(url, user_token)

