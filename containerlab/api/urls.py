"""Django API urlpatterns declaration for containerlab app."""

from nautobot.apps.api import OrderedDefaultRouter

from containerlab.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("topology", views.TopologyViewSet)
router.register("clkind", views.CLKindViewSet)

urlpatterns = router.urls
