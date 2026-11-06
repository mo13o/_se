from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
Category = Literal["assignment", "exam", "project", "other"]
Priority = Literal["high", "medium", "low"]
Status = Literal["todo", "done"]
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    category: Category = "assignment"
    priority: Priority = "medium"
    status: Status = "todo"
    course_id: str | None = None
    due_date: date
    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value=value.strip()
        if not value: raise ValueError("任務名稱不可空白")
        return value
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    category: Category | None = None
    priority: Priority | None = None
    status: Status | None = None
    course_id: str | None = None
    course_id: str | None = None
    due_date: date | None = None
    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set: raise ValueError("至少提供一個修改欄位")
        if self.title is not None:
            self.title=self.title.strip()
            if not self.title: raise ValueError("任務名稱不可空白")
        return self
class TaskRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: str; title: str; description: str; category: Category; priority: Priority; status: Status
    course_id: str | None = None
    course_id: str | None; due_date: date; created_at: datetime; updated_at: datetime; completed_at: datetime | None
class Summary(BaseModel):
    total: int; todo: int; done: int; overdue: int; due_soon: int; completion_rate: int


