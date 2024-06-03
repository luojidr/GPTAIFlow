from .base import BaseModel, db


class WorkflowRunRecord(BaseModel):
    __tablename__ = "workflowrunrecord"

    rid = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, index=True)
    workflow_id = db.Column(db.String(255), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=False)
    schedule_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    used_credits = db.Column(db.Integer, nullable=False)
    general_details = db.Column(db.Text)
    cost = db.Column(db.Double, nullable=False)
    parent_wid = db.Column(db.String(255), nullable=False)

    data_id = db.Column(db.Integer, nullable=False, server_default='0')
    general_details_id = db.Column(db.Integer, nullable=False, server_default='0')

