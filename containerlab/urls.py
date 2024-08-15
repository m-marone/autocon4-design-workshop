"""Django urlpatterns declaration for containerlab app."""

from nautobot.apps.urls import NautobotUIViewSetRouter

from containerlab import views

router = NautobotUIViewSetRouter()
router.register("topology", views.TopologyUIViewSet)

urlpatterns = router.urls
