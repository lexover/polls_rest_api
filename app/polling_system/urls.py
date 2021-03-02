from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from rest_framework import permissions
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from polls import views


router = routers.DefaultRouter()

router.register(r'polls', views.PollsViewSet, basename='polls')
router.register(r'questions', views.QuestionsViewSet, basename='questions')
router.register(r'answers', views.AnswerViewSet, basename='answers')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),
    path('token/',
         jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('token/verify/',
         jwt_views.TokenVerifyView.as_view(),
         name='token_verify'),
]
urlpatterns += router.urls


