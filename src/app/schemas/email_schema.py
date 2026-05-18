from pydantic import BaseModel

class EmailPayload(BaseModel):
    to_email: str
    subject: str
    body: str