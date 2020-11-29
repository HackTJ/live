from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import judge.routing

application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        # 'websocket': AuthMiddlewareStack(
        #     URLRouter(
        #         judge.routing.websocket_urlpatterns
        #     )
        # ),
    }
)
