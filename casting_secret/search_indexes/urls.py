from django.conf.urls import url
# from django.db import router
from django.urls import include
from rest_framework.routers import DefaultRouter

from casting_secret.search_indexes.viewsets import UserDocumentViewSet, CompanyDocumentViewSet, JobDocumentViewSet

router = DefaultRouter()

profile = router.register(r'profile', UserDocumentViewSet, base_name='profiledocument')

company = router.register(r'company', CompanyDocumentViewSet, base_name='companydocument')

job = router.register(r'job', JobDocumentViewSet, base_name='jobdocument')

urlpatterns = [
    url(r'^', include(router.urls)),
]
