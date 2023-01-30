from tortoise import fields
from tortoise.models import Model


class AkariAdminLogs(Model):
    uuid = fields.UUIDField(pk=True)
    guild_id = fields.BigIntField()
    action_username = fields.CharField(max_length=255)
    affected_username = fields.CharField(max_length=255)
    type_of_action = fields.CharField(max_length=255)
    reason = fields.TextField()
    date_issued = fields.DatetimeField(null=True, auto_now_add=True)
    duration = fields.BigIntField()

    class Meta:
        table = "admin_logs"

    def __str__(self):
        return self.name
