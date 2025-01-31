from marshmallow import Schema, fields, ValidationError

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class TaskSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str(validate=lambda x: x in ['pending', 'completed'])
    due_date = fields.Str()