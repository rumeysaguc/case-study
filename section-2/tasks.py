from celery import shared_task
import requests
from requests.exceptions import RequestException

@shared_task(bind=True, max_retries=5)
def notify_insurance_company_task(self, request_id):
    """
    Sigorta şirketine bildirim yapan task
    - Hata olursa retry eder (exponential backoff)
    """
    url = f"https://mock-insurance-service.com/notify/{request_id}"

    try:
        response = requests.post(url, timeout=5)  # 5 saniye timeout
        response.raise_for_status()  # HTTP error varsa exception fırlatır

    except RequestException as exc:
        # Exponential backoff: 2^retry * 10 saniye
        countdown = 2 ** self.request.retries * 10
        raise self.retry(exc=exc, countdown=countdown)

    return {"status": "success", "request_id": request_id}

