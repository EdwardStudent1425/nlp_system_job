from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Skill(Record):
    name: str
    evidence: str = Field(min_length=1)

class Profile(Record):
    skills: list[Skill]
    years_experience: float | None = Field(ge=0, le=70)
    years_evidence: str | None
    english: Literal["A1", "A2", "B1", "B2", "C1", "C2"] | None
    english_evidence: str | None
    mode: str

class Preferences(Record):
    role: str = ""
    city: str = ""
    remote_only: bool = False
    include_unknown: bool = False
    confirmed: bool = False

class Job(Record):
    id: str
    title: str
    company: str
    description: str
    source: str
    published: str | None
    retrieved_at: str
    historical: bool
    url: str | None
    category: str = ""
    skills: list[str] = Field(default_factory=list)
    min_years: float | None = None
    english: str | None = None
    remote: bool | None = None
    city: str | None = None
    ukraine: bool | None = None

class Recommendation(Record):
    job: Job
    score: float
    lexical_score: float
    matched_skills: list[str]
    unmentioned_skills: list[str]
    unknowns: list[str]
    evidence: list[dict[str, str]]
