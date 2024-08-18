"""Django API urlpatterns declaration for containerlab app."""

from nautobot.apps.api import OrderedDefaultRouter
from django.urls import path

from containerlab.api import views

urlpatterns = [
    path('create-guacamole-device/<uuid:pk>', views.CreateGuacamoleDevice.as_view(), name='create-guacamole-device'),
    path('get-guacamole-clientid/<uuid:pk>', views.GetGuacamoleClient.as_view(), name='get-guacamole-clientid'),
]

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("topology", views.TopologyViewSet)
router.register("clkind", views.CLKindViewSet)

urlpatterns.extend(router.urls)
