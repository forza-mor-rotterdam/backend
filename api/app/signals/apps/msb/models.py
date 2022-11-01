from enum import unique
from signal import signal
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from pytz import utc
from django.contrib.gis.geos import GEOSGeometry
from django.utils.text import slugify

from signals.apps.signals.managers import SignalManager
from signals.apps.signals.models import Signal
from signals.apps.signals.models.category import Category
from signals.apps.signals.models.mixins import CreatedUpdatedModel
from signals.apps.signals.querysets import SignalQuerySet
from signals.apps.signals.models import Status
from signals.apps.api.validation.address.pdok import PDOKAddressValidation
import json
from signals.apps.msb.tasks import check_mutatieregels, check_detail
from signals.apps.msb.statics import MSB_TO_SIGNALS_STATE, MSB_NIEUW, MSB_INBEHANDELING, MSB_DOORVERWEZEN, MSB_HEROPEND
from signals.apps.signals import workflow


class Melding(CreatedUpdatedModel):
    msb_id = models.PositiveBigIntegerField(unique=True)
    signal = models.OneToOneField(
        to=Signal,
        on_delete=models.CASCADE,
    )
    msb_list_item = models.TextField(null=True, blank=True)
    msb_item = models.TextField(null=True, blank=True)
    msb_item_mutatieregels = models.TextField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Melding: {self.msb_id}"

    def set_signal_location(self, data=None):
        if not data:
            data = json.loads(self.msb_list_item)
        address = {
            'openbare_ruimte': data["locatie"]["adres"]["straatNaam"], 
            'huisnummer': data["locatie"]["adres"]["huisnummer"],
            'woonplaats': "Rotterdam",
        }
        location_data = {}
        location_validator = PDOKAddressValidation()
        validated_address = None
        alternative_address = dict(address)
        try:
            validated_address = location_validator.validate_address(address=address)
        except:
            alternative_address.update({
                "huisnummer": 1,
            })
            try:
                validated_address = location_validator.validate_address(address=alternative_address)
            except:
                pass

        if 'extra_properties' not in location_data or location_data["extra_properties"] is None:
            location_data["extra_properties"] = {}

        location_data["extra_properties"]["original_address"] = address
        location_data["extra_properties"]["alternative_address"] = alternative_address
        if validated_address:
            location_data["address"] = validated_address
            location_data["bag_validated"] = True
            geometrie = validated_address.pop("geometrie")
            location_data["geometrie"] = GEOSGeometry(geometrie)
            Signal.actions.update_location(location_data, self.signal)
        return False

    def set_signal_category(self, msb_data):
        data = msb_data
        sub_category_slug = slugify(data["onderwerp"]["omschrijving"])
        sub_category = Category.objects.filter(slug=sub_category_slug, parent__isnull=False).first()
        if not sub_category:
            sub_category = Category.objects.filter(slug="overig", parent__isnull=False).first()

        Signal.actions.update_category_assignment({"category": sub_category}, self.signal)

    def set_reporter(self):
        Signal.actions.update_reporter({
            "email": "",
            "phone": "",
            "sharing_allowed": True,
        }, self.signal)

    def set_status(self, data=None):
        status = data.get("status")
        if not status:
            print("No status key found in msb data")
            return

        from_status_to_datefield_name = {
            MSB_NIEUW: "datumMelding",
            MSB_INBEHANDELING: "datumInbehandeling",
            MSB_DOORVERWEZEN: "datumDoorverwezen",
            MSB_HEROPEND: "datumHeropend",
        }
        date_keys = ["datumMelding", "datumInbehandeling", "datumDoorverwezen", "datumAfhandeling", "datumRappel", "datumHeropend"]
        dt_format = "%Y-%m-%dT%H:%M:%S"
        print(status)
        status_str_date = data.get(from_status_to_datefield_name.get(status, {}))
        if status_str_date is not None:
            status_date = datetime.strptime(status_str_date, dt_format)
        else:
            status_date = sorted([datetime.strptime(v, dt_format) for k, v in data.items() if k in date_keys and v is not None])[0]

        if not Status.objects.filter(created_at=status_date):
            status_data = {
                "state": MSB_TO_SIGNALS_STATE.get(data.get("status"),  workflow.GEMELD),
                "text": "",
                "send_email": False,
                "_signal": self.signal,
            }
            status_instance = Status.objects.create(**status_data)
            status_instance.created_at = status_date
            status_instance.save(update_fields=['created_at'])
            self.signal.status = status_instance
            self.signal.save(update_fields=['status'])

    def update_signal(self):
        
        if not self.signal.location:
            self.set_signal_location()
        if not self.signal.category_assignment:
            self.set_signal_category()
        if not self.signal.reporter:
            self.set_reporter()
        
        # check_mutatieregels.delay(self.msb_id)
        # check_detail.delay(self.msb_id)
