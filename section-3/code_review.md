# **Potansiyel Hata 1**

Kodu incelediğimde ilk hata çok net bir şekilde göze çarpan tüm objeleri sadece count’a erişmek için çekmesi oldu.
Bu çok performanssız bir yöntem. Eğer bir modele ait tabloda kaç veri olduğuna erişmek istiyorsak bunun için RAM'i şişirmeyen yöntemle yapmak daha profesyonel olur.

Doğru ve profesyonel yaklaşımla aynı işlemi şöyle yapardım:

```python
total_count = AssistanceRequest.objects.count()
```

---

# **Potansiyel Hata 2**

Yine kodda ikinci göze çarpan nokta provider'ların tamamını alıp (ki bu binlerce veya on binlerce olabilir) döngüyle dönerken aktiflik kontrolü yapmak çok verimsiz bir yaklaşımdır.
Gereksiz işlem yükü oluşturur.

Aynı şekilde modelde zaten `last_ping` field'ı varsa neden 5 dakika kontrolünü Django’nun QuerySet metotlarıyla yapmayalım?

Aynı işlemin performanslı halinin şöyle olması gerektiğini düşünüyorum:

```python
from django.utils import timezone
from datetime import timedelta

five_minutes_ago = timezone.now() - timedelta(minutes=5)

active_count = Provider.objects.filter(
    is_active=True,
    last_ping__gt=five_minutes_ago
).count()
```

---

# **Potansiyel Hata 3**

Log tablosu büyük projelerde çok büyük veri içerebilir.
Bu nedenle orada sorgu atarken çok dikkat etmek gerekir. Daraltılabilir filterlar mümkün olduğunca kullanılmalı. Ayrıca sorgudan sonra aldığımız veride tek bir sütunu kullanacaksak, veritabanından çekerken de sadece o sütunu çekmek performans açısından önemlidir.

Benim yaklaşımım aşağıdaki gibi olurdu:

```python
logs = Log.objects.filter(level='ERROR') \
    .order_by('-created_at') \
    .values_list('message', flat=True)[:5]
```
