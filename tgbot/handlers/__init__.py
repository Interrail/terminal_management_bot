"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .document import document_router
from .menu import menu_router

from .order import user_router
from .statistics import statistic_router

routers_list = [
    admin_router,
    statistic_router,
    menu_router,
    user_router,
    document_router,

]

__all__ = [
    "routers_list",
]
