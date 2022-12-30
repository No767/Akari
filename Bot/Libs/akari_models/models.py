from tortoise import fields
from tortoise.models import Model


class Guilds(Model):
    id = fields.BigIntField(pk=True)
    admin_logs_enabled = fields.BooleanField(default=False)
    modmail_enabled = fields.BooleanField(default=False)
    suggestions_enabled = fields.BooleanField(default=False)
    tags_enabled = fields.BooleanField(default=False)
    modmail_channel_name = fields.CharField(null=True, max_length=255)
    modmail_channel_id = fields.BigIntField(null=True)
    admin_logs: fields.ReverseRelation["AdminLogs"]
    modmail: fields.ReverseRelation["ModMail"]
    tags: fields.ReverseRelation["Tags"]

    class Meta:
        table = "guilds"

    def __str__(self):
        return f"Guilds({self.id}, {self.admin_logs_enabled}, {self.modmail_enabled}, {self.suggestions_enabled}, {self.tags_enabled}, {self.modmail_channel_name}, {self.modmail_channel_id}, {self.admin_logs}, {self.modmail}, {self.tags})"


class Users(Model):
    id = fields.BigIntField(pk=True)
    tags: fields.ReverseRelation["Tags"]
    username = fields.CharField(max_length=255)
    user_id = fields.BigIntField()

    class Meta:
        table = "users"

    def __str__(self):
        return f"Users({self.id}, {self.tags}, {self.username}, {self.user_id})"


class Tags(Model):
    id = fields.UUIDField(pk=True)
    guild: fields.ForeignKeyRelation["Guilds"] = fields.ForeignKeyField(
        "models.Guilds", related_name="tags", on_delete=fields.CASCADE
    )
    user: fields.ForeignKeyRelation["Users"] = fields.ForeignKeyField(
        "models.Users", related_name="tags", on_delete=fields.CASCADE
    )
    date_created = fields.DatetimeField(auto_now_add=True)
    name = fields.CharField(max_length=255)
    content = fields.TextField()

    class Meta:
        table = "tags"

    def __str__(self):
        return f"Tags({self.id}, {self.guild}, {self.user}, {self.date_created}, {self.name}, {self.content})"


class ModMail(Model):
    id = fields.UUIDField(pk=True)
    guild: fields.ForeignKeyRelation["Guilds"] = fields.ForeignKeyField(
        "models.Guilds", related_name="modmail", on_delete=fields.CASCADE
    )
    user: fields.ForeignKeyRelation["Users"] = fields.ForeignKeyField(
        "models.Users", related_name="modmail", on_delete=fields.CASCADE
    )
    date_created = fields.DatetimeField(auto_now_add=True)
    message = fields.TextField()

    class Meta:
        table = "modmail"

    def __str__(self):
        return f"ModMail({self.id}, {self.guild}, {self.user}, {self.date_created}, {self.message})"


class AdminLogs(Model):
    id = fields.UUIDField(pk=True)
    guild: fields.ForeignKeyRelation["Guilds"] = fields.ForeignKeyField(
        "models.Guilds", related_name="admin_logs", on_delete=fields.CASCADE
    )
    date_issued = fields.DatetimeField(auto_now_add=True)
    affected_username = fields.CharField(max_length=255)
    type_of_action = fields.CharField(max_length=255)
    reason = fields.TextField()

    def __str__(self):
        return f"AdminLogs({self.id}, {self.guild}, {self.date_issued}, {self.affected_username}, {self.type_of_action}, {self.reason})"
