from tortoise.models import Model
from tortoise import fields

class AkariTags(Model):
    uuid = fields.UUIDField(pk=True)
    tag_name = fields.CharField(max_length=255)
    tag_content = fields.TextField()
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    guild_id = fields.BigIntField()
    author_id = fields.BigIntField()
    
    class Meta:
        table = "tags"