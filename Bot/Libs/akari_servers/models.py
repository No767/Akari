from tortoise import fields
from tortoise.models import Model


class AkariServers(Model):
    id = fields.BigIntField(pk=True)
    guild_id = fields.BigIntField(unique=True)
    admin_logs = fields.BooleanField(default=True)
    modmail = fields.BooleanField(default=False)
    suggestions = fields.BooleanField(default=False)
    tags = fields.BooleanField(default=True)

    class Meta:
        table = "servers"

    def __str__(self):
        return self.name
