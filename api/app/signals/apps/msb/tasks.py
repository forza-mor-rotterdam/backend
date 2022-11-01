
from signals.celery import app
import json
import celery
from datetime import datetime
from celery import shared_task

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


# @shared_task(bind=True, base=BaseTaskWithRetry)
def check_mutatieregels(melding_id, mutatieregels):
    from signals.apps.msb.services import MSBService
    from signals.apps.msb.models import Melding
    from signals.apps.signals.models import Status
    from signals.apps.signals.models import Attachment
    from signals.apps.signals import workflow

    melding = Melding.objects.filter(msb_id=melding_id).first()
    translate_msb_status_to_signal = {
        "Nieuw": workflow.GEMELD,
        "Doorverwezen gekregen": workflow.VERZOEK_TOT_AFHANDELING,
        "In behandeling": workflow.BEHANDELING,
    }
    # mutatieregels = {}
    # mutatieregels = MSBService.get_mutatieregels(melding_id)
    if melding and melding.msb_item_mutatieregels != json.dumps(mutatieregels):
        statuses_created_at = melding.signal.statuses.all().values_list("created_at", flat=True)
        print(melding.msb_id)
        def get_status(status_details: list):
            status_parts = next(iter([t.get("value") for t in status_details if t.get("key") == "Status"]), "Nieuw").split("->")
            status = status_parts[-1].strip()
            print(status)
            return translate_msb_status_to_signal.get(status, "Nieuw")
                
        not_existing_statusen = [
            Status(
                state=get_status(m.get("details", [])), 
                text=m.get("opmerking"), 
                send_email=False,
                _signal=melding.signal,
                extra_properties=json.dumps(m),
            ) for m in mutatieregels 
            if datetime.strptime(m.get("datum"), "%Y-%m-%dT%H:%M:%S") not in statuses_created_at
        ]
        created_statusen = Status.objects.bulk_create(not_existing_statusen)
        melding.signal.status = melding.signal.statuses.first()

        melding.signal.save()
        melding.msb_item_mutatieregels = json.dumps(mutatieregels)
        melding.save()

    return True


@shared_task(bind=True, base=BaseTaskWithRetry)
def check_detail(self, melding_id, user_token):
    from signals.apps.msb.services import MSBService
    from signals.apps.msb.models import Melding
    from signals.apps.signals.models import Status
    try:
        melding = Melding.objects.filter(msb_id=melding_id).first()
        detail = {}
        detail = MSBService.get_detail(melding_id)
        if melding and melding.msb_item != json.dumps(detail):
            update_attachements.delay(melding_id)
            melding.msb_item = json.dumps(detail)
            melding.save()

    except Exception as e:
        print(e)
    return True


@shared_task(bind=True, base=BaseTaskWithRetry)
def update_attachements(self, melding_id):
    from signals.apps.msb.services import MSBService
    from signals.apps.msb.models import Melding
    from signals.apps.signals.models import Status
    try:
        melding = Melding.objects.filter(msb_id=melding_id).first()
        fotos = json.loads(melding.msb_item).get("fotos", [])
        current_attachments = melding.signal.attachments.all().values_list("file__url", flat=True)
        print(current_attachments)

        

    except Exception as e:
        print(e)
    return True