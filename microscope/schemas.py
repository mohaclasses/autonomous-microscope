from pydantic import BaseModel, ConfigDict, Field

class CaptureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    seed: int = Field(ge=0, le=2**31-1)
    z_um: float = Field(ge=-8, le=8, allow_inf_nan=False)
    exposure_ms: int = Field(ge=5, le=80)