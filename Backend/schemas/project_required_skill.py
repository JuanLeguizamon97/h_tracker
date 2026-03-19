from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

LEVEL_LABELS = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}


class ProjectRequiredSkillCreate(BaseModel):
    skill_id: str
    min_level: int = 2  # 1–4


class ProjectRequiredSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    skill_id: str
    skill_name: str
    skill_category: str
    min_level: int
    min_level_label: str
    created_at: datetime


# ── Assignable employees ──────────────────────────────────────────────────────

class SkillBrief(BaseModel):
    name: str
    category: str
    level: int
    level_label: str
    years: Optional[float] = None


class AssignableEmployeeOut(BaseModel):
    id: str          # employees.id (UUID primary key)
    name: str
    title: Optional[str] = None
    skills: List[SkillBrief]
    match_score: int           # 0–100
    matched_skills: List[str]
    missing_skills: List[str]
    already_assigned: bool
    suggested_role: Optional[str] = None


# ── Skill coverage ────────────────────────────────────────────────────────────

class SkillCoverageOut(BaseModel):
    skill_id: str
    skill_name: str
    skill_category: str
    min_level: int
    min_level_label: str
    coverage_status: str   # "covered" | "partial" | "missing"
    covered_by_names: List[str]
