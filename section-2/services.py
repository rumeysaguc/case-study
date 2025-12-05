import math
from django.db import transaction
from .models import AssistanceRequest, Provider, ServiceAssignment
from .tasks import notify_insurance_company_task


class AssistanceService:
    
    @classmethod
    def create_request(cls, data: dict) -> AssistanceRequest:
        return AssistanceRequest.objects.create(**data)

    @classmethod
    def find_nearest_available_provider(cls, lat: float, lon: float) -> Provider:
        providers = Provider.objects.filter(is_available=True) #MEVCUT TÜM KULLANILABİLİR SAĞLAYICILARI ÇEKTİM

        if not providers.exists():
            raise Exception("No available provider")

        nearest = None
        min_dist = 99999999 #ÇOK YÜKSEK BİR DEĞERLE BAŞLATTIM

        for p in providers: #EN YAKIN SAĞLAYICIYI BULMAK İÇİN BASİT MESAFE HESABI YAPTIM (BU KONUDA BİLGİM YOKTU İNTERNETTEN BAKTIM)
            dist = math.sqrt(
                (p.lat - lat)**2 +
                (p.lon - lon)**2
            )
            if dist < min_dist:
                min_dist = dist
                nearest = p

        return nearest

    @classmethod
    def assign_provider_atomic(cls, request_id: int, provider_id: int = None):
        with transaction.atomic(): #TRANSACTION ATOMIC BLOĞU İLE İÇERİSİNDEKİ İŞLEMLERİN YA TAMAMININ YA DA HİÇBİRİNİN GERÇEKLEŞMESİNİ SAĞLADIM
            req = AssistanceRequest.objects.get(id=request_id)

            if provider_id:
                provider = Provider.objects.select_for_update().get(id=provider_id) #SELECT FOR UPDATE İLE SATIRI KİTLERİZ O ESNA DA BAŞKA NOKTADAN OREAD YA DA UPDAGTE İSTEYEN İŞLEMLER İÇİN KİLİTLENMİŞ OLUR
            else:
                provider = cls.find_nearest_available_provider(req.lat, req.lon)
                provider = Provider.objects.select_for_update().get(id=provider.id) #YİNE KİLİTLEDİM

            if not provider.is_available:
                raise Exception("Provider is busy!")

            provider.is_available = False
            provider.save()

            ServiceAssignment.objects.create(request=req, provider=provider)
            req.status = 'DISPATCHED'
            req.save()

            notify_insurance_company_task.delay(req.id)


    
    @classmethod
    def complete_request(cls, request_id: int):
         with transaction.atomic(): #TRANSACTION ATOMIC BLOĞU İLE İÇERİSİNDEKİ İŞLEMLERİN YA TAMAMININ YA DA HİÇBİRİNİN GERÇEKLEŞMESİNİ SAĞLADIM
            req = AssistanceRequest.objects.select_for_update().get(id=request_id)
            if req.status == "DISPATCHED": #SADECE GÖNDERİLMİŞ İSE TAMAMLANABİLİR
                assignment = ServiceAssignment.objects.get(request=req)
                provider = Provider.objects.select_for_update().get(id=assignment.provider.id)

                provider.is_available = True
                provider.save()

                req.status = "COMPLETED"
                req.save()
    
    @classmethod  
    def cancel_request(cls, request_id: int): #İPTAL İŞLEMİ
        with transaction.atomic(): 
            req = AssistanceRequest.objects.select_for_update().get(id=request_id)

            if req.status == "DISPATCHED":
                assignment = ServiceAssignment.objects.get(request=req)
                provider = Provider.objects.select_for_update().get(id=assignment.provider.id)

                provider.is_available = True
                provider.save()

            req.status = "CANCELLED"
            req.save()
