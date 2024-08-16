"""Django urlpatterns declaration for containerlab app."""

from nautobot.apps.urls import NautobotUIViewSetRouter

from containerlab import views

router = NautobotUIViewSetRouter()
router.register("topology", views.TopologyUIViewSet)
router.register("clkind", views.CLKindUIViewSet)

urlpatterns = router.urls
