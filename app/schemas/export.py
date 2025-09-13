from typing import Literal

from pydantic import BaseModel


class Branding(BaseModel):
    logo_path: str | None = None
    client_name: str | None = None
    watermark: str | None = "Sandbox"


ModuleType = Literal["advisor", "dashboard", "pip", "jd"]


class ExportRequest(BaseModel):
    trace_id: str
    client: str
    module: ModuleType
    title: str
    content: str
    branding: Branding


class ExportResponse(BaseModel):
    path: str
    export_branding_compliance: bool
    export_manifest_hash: str
    trace_id: str
