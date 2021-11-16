from typing import Optional

# One line of FastAPI imports here later
import sqlmodel
# from sqlmodel import Field, Session, SQLModel, create_engine, select

class FolderInfo(sqlmodel.SQLModel, table=True):
    folder: Optional[str] = sqlmodel.Field(default=None, primary_key=True)
    status: str
    querylastrun: str
