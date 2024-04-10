from pydantic import BaseModel, ConfigDict, Field


class UserMeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., description="Email")
    is_active: bool = Field(..., description="Is Active")
