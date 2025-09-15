from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel, to_pascal
from datetime import datetime


AccountType = Literal["Publisher", "Project", "Personal use"]
OrganizationType = Literal["Startup", "Lab", "Corporate"]


class CamelModel(BaseModel):
    """Base model that converts snake_case to camelCase for JSON output"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,     # ✅ NEW: Accept snake_case field names
        validate_by_alias=True,    # ✅ NEW: Accept camelCase aliases  
        from_attributes=True,
    )


# ---------- PROFILE: CREATE / UPDATE / OUT ----------
class ProfileCreate(CamelModel):
    """
    Create a Profile during onboarding (minimal required: account_type + username).
    """
    user_id: int | None = None
    account_type: AccountType
    username: str | None = None

    # public display
    name: str | None = None
    location: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    display_role: str | None = None

    # socials
    github: str | None = None
    twitter: str | None = None
    linkedin: str | None = None
    instagram: str | None = None
    discord: str | None = None
    google_scholar: str | None = None
    orcid: str | None = None
    researchgate: str | None = None
    website: str | None = None
    cmc_cg: str | None = None

    # publisher
    organization_name: str | None = None
    institution_name: str | None = None
    verification_status: bool = False

    # project
    organization_type: OrganizationType | None = None
    mission: str | None = None
    team_size: int | None = Field(default=None, ge=1)
    founded_year: int | None = None

    # personal
    current_affiliation: str | None = None
    interests: list[str] = Field(default_factory=list)


class ProfileUpdate(CamelModel):
    """
    PATCH-style updates for Profile only.
    All fields optional. Arrays replace by default (idempotent PUT semantics).
    """

    # --- Public Display ---
    account_type: AccountType | None = None
    username: str | None = Field(None, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    name: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=500)
    profile_image: str | None = None

    display_role: str | None = Field(None, max_length=50)

    # --- Social Links ---
    github: str | None = Field(None, max_length=100)
    twitter: str | None = Field(None, max_length=100)
    linkedin: str | None = Field(None, max_length=100)
    instagram: str | None = Field(None, max_length=100)
    discord: str | None = Field(None, max_length=50)
    google_scholar: str | None = Field(None, max_length=100)
    orcid: str | None = Field(None, max_length=50)
    researchgate: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=200)
    cmc_cg: str | None = Field(None, max_length=100)

    # --- Publisher Info ---
    organization_name: str | None = Field(None, max_length=100)
    institution_name: str | None = Field(None, max_length=100)
    verification_status: bool | None = None

    # --- Project/Org Info ---
    organization_type: OrganizationType | None = None
    mission: str | None = Field(None, max_length=1000)
    team_size: int | None = Field(None, ge=1, le=10000)
    founded_year: int | None = Field(None, ge=1900, le=2100)

    # --- Personal Info ---
    current_affiliation: str | None = Field(None, max_length=100)
    interests: list[str] | None = Field(None, max_length=15)  # max 10 items


class ProfileOut(CamelModel):

    id: int
    user_id: int
    account_type: AccountType

    # public display
    username: str | None
    name: str | None
    location: str | None
    bio: str | None
    profile_image: str | None
    display_role: str

    # socials
    github: str | None
    twitter: str | None
    linkedin: str | None
    instagram: str | None
    discord: str | None
    google_scholar: str | None
    orcid: str | None
    researchgate: str | None
    website: str | None
    cmc_cg: str | None

    # publisher
    organization_name: str | None
    institution_name: str | None
    verification_status: bool

    # project
    organization_type: OrganizationType | None
    mission: str | None
    team_size: int | None
    founded_year: int | None

    # personal
    current_affiliation: str | None
    interests: list[str]

    created_at: datetime = Field(default_factory=datetime.now)

    @field_serializer("created_at")
    def _ser_created_at(self, v: datetime) -> str:
        return v.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
