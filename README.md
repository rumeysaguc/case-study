# DestechChallenge Projesi

## 1. Proje Klonlama

```bash
git clone https://github.com/destechhasar/destechchallenge.git
cd destechchallenge
```



> Not: `requests` kütüphanesi Celery task’larım için ekledim.

## 4. Docker Servislerini Başlatma

```bash
docker compose up -d
```

* Servisler:

  * `web`: Django uygulaması
  * `worker`: Celery worker
  * `db`: PostgreSQL
  * `redis`: Celery broker

## 5. Veritabanı Ayarları ve Migration

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

* Superuser oluşturmak için kullanıcı adı, e-mail ve şifre girilecek


## 6. Test Kayıtlarını Oluşturma Shell açıp
```bash
docker compose exec web python manage.py shell
```

Shell içinde:

```python
from assistance.models import Provider
Provider.objects.create(name="Towing A", lat=40.0, lon=29.0, is_available=True)
Provider.objects.create(name="Towing B", lat=41.0, lon=29.5, is_available=True)

# Check
print(Provider.objects.all())

from assistance.services import AssistanceService

req = AssistanceService.create_request({
    "customer_name": "Rümeysa Güç",
    "policy_number": "123456789",
    "lat": 39.1,
    "lon": 25.0,
    "issue_desc": "Corsa Araba arızası"
})

print(req.id, req.customer_name, req.status)
```

* Bu şekilde Provider ve AssistanceRequest kayıtları oluşturuldu.
* `AssistanceService` üzerinden request oluşturulduktan sonra Celery task’ları otomatik tetiklenir.

## 7. API Testleri

### Yeni Talep Oluşturma

```bash
curl -X POST http://localhost:8000/api/request/ \
-H "Content-Type: application/json" \
-d '{
  "customer_name": "Rümeysa Güç",
  "policy_number": "123456789",
  "lat": 40.1,
  "lon": 29.1,
  "issue_desc": "Corsa Araba arızası"
}'
```

* Dönen JSON:

```json
{"status":"Created","id":1}
```

### Talebi Tamamlama

```bash
curl -X POST http://localhost:8000/api/request/1/complete/
```

* Dönen JSON:

```json
{"status":"Completed"}
```

## 8. Celery Task Kontrolü

Worker loglarını takip etmek için terminalde çalıştırdığım kod:

```bash
docker compose logs -f worker
```

* `notify_insurance_company_task` tetiklenir
* Retry mekanizması aktif (`max_retries=5`, exponential backoff)

## 9. Önemli Notlar

* `requests` modülü Docker container içinde yüklü olmalı (`requirements.txt`).
* Docker container rebuild ve restart işlemleri yaptım:

```bash
docker compose build web
docker compose up -d
```
