"""Django urlpatterns declaration for containerlab app."""

from django.templatetags.static import static
from django.views.generic import RedirectView
from django.urls import path
from nautobot.apps.urls import NautobotUIViewSetRouter

from containerlab import views

router = NautobotUIViewSetRouter()
router.register("topology", views.TopologyUIViewSet)
router.register("clkind", views.CLKindUIViewSet)

urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("containerlab/docs/index.html")), name="docs"),
] + router.urls
