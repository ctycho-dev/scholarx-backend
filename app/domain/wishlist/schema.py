from pydantic import BaseModel, ConfigDict


class WishlistCreate(BaseModel):
    email: str


class WishlistOut(BaseModel):

    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)
