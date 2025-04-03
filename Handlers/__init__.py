from .common import register_common_handlers
from .tenant import register_tenant_handlers
from .landlord import register_landlord_handlers

def register_all_handlers(bot):
    register_common_handlers(bot)
    register_tenant_handlers(bot)
    register_landlord_handlers(bot)
