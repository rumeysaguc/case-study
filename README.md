# case-study

#Shell başlatıp oluşturmak istediğim testlerim için kullanacağım kayıtları oluşturdum.
docker compose exec web python manage.py shell

from assistance.models import Provider
Provider.objects.create(name="Towing A", lat=40.0, lon=29.0, is_available=True)
Provider.objects.create(name="Towing B", lat=41.0, lon=29.5, is_available=True)

Check için terminale bastım.
print(Provider.objects.all())
