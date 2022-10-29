from tortoise import fields
from tortoise.models import Model


class AkariTags(Model):
    uuid = fields.CharField(pk=True, max_length=255)
    tag_name = fields.CharField(max_length=255)
    tag_content = fields.TextField()
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    guild_id = fields.BigIntField()
    author_id = fields.BigIntField()
    author_name = fields.CharField(max_length=255)

    class Meta:
        table = "tags"

    def __str__(self):
        return self.name
