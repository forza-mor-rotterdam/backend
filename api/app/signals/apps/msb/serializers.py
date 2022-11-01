from signals.apps.api.serializers import PrivateSignalSerializerList, PrivateSignalSerializerDetail
from rest_framework import serializers
from signals.apps.msb.services import MSBService
from signals.apps.api.serializers.nested import (
    _NestedCategoryModelSerializer,
    _NestedDepartmentModelSerializer,
    _NestedLocationModelSerializer,
    _NestedNoteModelSerializer,
    _NestedPriorityModelSerializer,
    _NestedPublicStatusModelSerializer,
    _NestedReporterModelSerializer,
    _NestedStatusModelSerializer,
    _NestedTypeModelSerializer
)
from signals.apps.msb.tasks import check_mutatieregels
from signals.apps.msb.statics import MSB_TO_SIGNALS_STATE, MSB_NIEUW
import json
from signals.apps.signals import workflow



class PrivateSignalMSBFieldsMixin:
    def get_attachments(self, obj):
        user_token = MSBService.get_user_token_from_request(self.context['request'])
        if hasattr(obj, "melding"):
            return MSBService.get_detail(obj.melding.msb_id, user_token).get("result", {}).get("fotos", [])
        return []

    def get_location(self, obj):
        user_token = MSBService.get_user_token_from_request(self.context['request'])
        if hasattr(obj, "melding"):
            if not obj.location:
                # msb_data = MSBService.get_detail(obj.melding.msb_id, user_token).get("result", {})
                msb_data = json.loads(obj.melding.msb_list_item)
                address = {
                    "huisnummer": msb_data.get("locatie", {}).get("adres", {}).get("huisnummer"),
                    "openbare_ruimte": msb_data.get("locatie", {}).get("adres", {}).get("straatNaam"),
                    "woonplaats": "Rotterdam",
                }
                if not obj.melding.set_signal_location(msb_data):
                    return {
                        "address": address,
                        "geometrie": {
                            "coordinates": [
                                msb_data.get("locatie", {}).get("x"),
                                msb_data.get("locatie", {}).get("y"),
                            ],
                            "type": "Point",
                        }
                    }
            serializer = _NestedLocationModelSerializer(obj.location)
            return serializer.data
        return {}

    def get_status(self, obj):
        user_token = MSBService.get_user_token_from_request(self.context['request'])
        if hasattr(obj, "melding"):
            status = json.loads(obj.melding.msb_list_item).get("status", MSB_NIEUW)
            # msb_data = MSBService.get_detail(obj.melding.msb_id, user_token).get("result", {})

            # check_mutatieregels(obj.melding.msb_id, msb_data)
            # obj.melding.set_status(msb_data)
            # serializer = _NestedStatusModelSerializer(obj.status)
            # return serializer.data
            print(status)
            return {
                "state": MSB_TO_SIGNALS_STATE.get(status,  workflow.GEMELD),
            }
        return {}

    def get_category(self, obj):
        user_token = MSBService.get_user_token_from_request(self.context['request'])
        if hasattr(obj, "melding"):

            msb_data = json.loads(obj.melding.msb_list_item)

            obj.melding.set_signal_category(msb_data)
            serializer = _NestedCategoryModelSerializer(obj.category_assignment, context=self.context)
            return serializer.data
            print(status)

            return {
                "sub_category": MSB_TO_SIGNALS_STATE.get(status,  workflow.GEMELD),
            }
        return {}


class PrivateSignalMSBSerializerList(PrivateSignalMSBFieldsMixin, PrivateSignalSerializerList):
    # attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)
    location = serializers.SerializerMethodField(source='get_location', read_only=True)
    status = serializers.SerializerMethodField(source='get_status', read_only=True)
    category = serializers.SerializerMethodField(source='get_category', read_only=True)

    # category = _NestedCategoryModelSerializer(
    #     source='category_assignment',
    #     permission_classes=(SignalCreateInitialPermission,)
    # )


class PrivateSignalMSBSerializerDetail(PrivateSignalMSBFieldsMixin, PrivateSignalSerializerDetail):
    attachments = serializers.SerializerMethodField(source='get_attachments', read_only=True)
