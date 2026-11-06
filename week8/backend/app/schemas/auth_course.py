from pydantic import BaseModel, EmailStr, Field, field_validator
class Register(BaseModel):
    email: EmailStr; password: str=Field(min_length=10,max_length=128); display_name:str=Field(min_length=1,max_length=80)
    @field_validator("password")
    @classmethod
    def strong(cls,v):
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v): raise ValueError("密碼需包含英文字母與數字")
        return v
class Login(BaseModel): email:EmailStr; password:str
class ProfileUpdate(BaseModel): display_name:str|None=Field(default=None,min_length=1,max_length=80); timezone:str|None=Field(default=None,max_length=50)
class PasswordChange(BaseModel): current_password:str; new_password:str=Field(min_length=10,max_length=128)
class CourseInput(BaseModel):
    name:str=Field(min_length=1,max_length=100); semester:str=Field(min_length=1,max_length=50); teacher:str=Field(default="",max_length=80); location:str=Field(default="",max_length=100); color:str=Field(default="#315fd2",pattern=r"^#[0-9A-Fa-f]{6}$")
class SessionInput(BaseModel): weekday:int=Field(ge=1,le=7); start_time:str; end_time:str; confirm_overlap:bool=False
