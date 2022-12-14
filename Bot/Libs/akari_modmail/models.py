from tortoise import fields
from tortoise.models import Model


class AkariModMail(Model):
    uuid = fields.CharField(max_length=255, pk=True)
    guild_id = fields.BigIntField()
    title = fields.CharField(max_length=255)
    message = fields.TextField()
    author = fields.CharField(max_length=255)
    date_created = fields.CharField(max_length=255)

    class Meta:
        table = "modmail"

    def __str__(self):
        return self.name


class AkariModMailConfig(Model):
    guild_id = fields.BigIntField(pk=True)
    channel_name = fields.CharField(max_length=255)
    channel_id = fields.BigIntField()

    class Meta:
        table = "modmail_config"

    def __str__(self):
        return self.name
