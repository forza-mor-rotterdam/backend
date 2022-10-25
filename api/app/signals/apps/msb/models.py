from enum import unique
from signal import signal
import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from pytz import utc
from django.contrib.gis.geos import GEOSGeometry

from signals.apps.signals.managers import SignalManager
from signals.apps.signals.models import Signal
from signals.apps.signals.models.mixins import CreatedUpdatedModel
from signals.apps.signals.querysets import SignalQuerySet
from signals.apps.api.validation.address.pdok import PDOKAddressValidation
import json
from django.contrib.gis.geos import Point
from signals.apps.signals.managers import (
    create_note,
    update_category_assignment,
    update_location,
    update_priority,
    update_status,
    update_type
)


class Melding(CreatedUpdatedModel):
    msb_id = models.PositiveBigIntegerField(unique=True)
    signal = models.OneToOneField(
        to=Signal,
        on_delete=models.CASCADE,
    )
    msb_list_item = models.TextField(null=True, blank=True)
    msb_item = models.TextField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def set_signal_location(self):
        data = json.loads(self.msb_list_item)
        address = {
            'openbare_ruimte': data["locatie"]["adres"]["straatNaam"], 
            'huisnummer': data["locatie"]["adres"]["huisnummer"],
            'woonplaats': "Rotterdam",
        }
        location_data = {}
        location_validator = PDOKAddressValidation()
        validated_address = location_validator.validate_address(address=address)
        if 'extra_properties' not in location_data or location_data["extra_properties"] is None:
            location_data["extra_properties"] = {}

        location_data["extra_properties"]["original_address"] = address
        location_data["address"] = validated_address
        location_data["bag_validated"] = True
        print(validated_address["geometrie"])
        geometrie = validated_address.pop("geometrie")
        location_data["geometrie"] = GEOSGeometry(geometrie)
        print(location_data)
        Signal.actions.update_location(location_data, self.signal)

    def update_signal(self):
        # location
        if not self.signal.location:
            self.set_signal_location()
