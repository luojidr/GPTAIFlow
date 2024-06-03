from .base import BaseModel, db


class OpenAIHistory(BaseModel):
    __tablename__ = "openaihistory"

    id = db.Column(db.BigInteger, primary_key=True)
    chat_id = db.Column(db.String(255), nullable=False, unique=True)
    user_id = db.Column(db.String(50), nullable=False)
    input_tokens = db.Column(db.BigInteger, nullable=False)
    output_tokens = db.Column(db.BigInteger, nullable=False)
    input_str = db.Column(db.Text, nullable=False, server_default='')
    output_str = db.Column(db.Text, nullable=False, server_default='')
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    model_type = db.Column(db.String(255), nullable=False)
    rid = db.Column(db.String(255), nullable=False)

    input_str_id = db.Column(db.Integer, nullable=False, server_default='0')
    output_str_id = db.Column(db.Integer, nullable=False, server_default='0')

