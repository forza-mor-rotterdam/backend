from signals.apps.api.views import PrivateSignalViewSet
from rest_framework.exceptions import ValidationError
from django.conf import settings
from signals.apps.msb.models import Melding
from signals.apps.msb.serializers import PrivateSignalMSBSerializerList, PrivateSignalMSBSerializerDetail
from signals.apps.signals.models.category import Category
import requests
import json
from signals.apps.msb.services import MSBService

class PrivateSignalMSBViewSet(PrivateSignalViewSet):

    serializer_class = PrivateSignalMSBSerializerList
    serializer_detail_class = PrivateSignalMSBSerializerDetail

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(melding__isnull=False)
        return qs

    def list(self, request, *args, **kwargs):
        user_token = MSBService.get_user_token_from_request(request)

        

        mapped_data = MSBService.get_list(user_token, request.GET).get("result")
        for msbm in mapped_data:
            m = Melding.objects.filter(msb_id=msbm["id"]).first()
            if not m:
                m = Melding.objects.create(msb_id=msbm["id"], msb_list_item=json.dumps(msbm))
            elif m.msb_list_item != json.dumps(msbm):
                m.msb_list_item = json.dumps(msbm)
                m.save()
            # m.update_signal()
            
        return super().list(request, *args, **kwargs)