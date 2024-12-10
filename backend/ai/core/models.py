from typing import List, Optional

from pydantic import BaseModel


class CustomSelection(BaseModel):
    selection: str
    start_line: int
    end_line: int
    file_name: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequestBody(BaseModel):
    project_id: str
    model: str
    context_files: Optional[List[str]] = None
    custom_selections: Optional[List[CustomSelection]] = None
    context_preview: Optional[str] = None
    compiled_query: Optional[str] = None
    asset_id: Optional[str] = None
    related_assets: Optional[List[dict]] = None
    asset_links: Optional[List[dict]] = None
    column_links: Optional[List[dict]] = None
    message_history: Optional[List[ChatMessage]] = None
    file_problems: Optional[List[str]] = None
