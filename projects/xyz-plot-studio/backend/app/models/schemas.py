"""
Pydantic models for API request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# Enums

class ExperimentStatus(str, Enum):
    """Experiment execution status."""
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ParameterType(str, Enum):
    """Parameter value type."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    ENUM = "enum"


class WorkflowTemplate(str, Enum):
    """Available workflow templates."""
    TXT2IMG = "txt2img"
    IMG2IMG = "img2img"
    HIRES_FIX = "hires_fix"
    LORA_COMPARISON = "lora_comparison"
    CUSTOM = "custom"


# Parameter Definitions

class ParameterDefinition(BaseModel):
    """Definition of a sweep parameter (X, Y, or Z axis)."""
    name: str = Field(..., description="Parameter name (e.g., 'cfg', 'steps', 'sampler_name')")
    display_name: str = Field(..., description="Human-readable name")
    type: ParameterType = Field(..., description="Parameter type")
    values: List[Union[int, float, str]] = Field(
        ..., description="List of values to sweep", min_length=1
    )

    @field_validator("values")
    @classmethod
    def validate_values(cls, v: List[Any]) -> List[Any]:
        """Ensure all values are of the same type."""
        if not v:
            raise ValueError("Values list cannot be empty")

        first_type = type(v[0])
        if not all(isinstance(val, first_type) for val in v):
            raise ValueError("All parameter values must be of the same type")

        return v

    @property
    def count(self) -> int:
        """Number of values in this parameter."""
        return len(self.values)


class NumericParameterRange(BaseModel):
    """Helper for defining numeric parameter ranges."""
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    step: float = Field(..., description="Step size", gt=0)
    logarithmic: bool = Field(default=False, description="Use logarithmic scale")

    def to_values(self) -> List[float]:
        """Convert range to list of values."""
        import numpy as np

        if self.logarithmic:
            # Logarithmic scale
            num_steps = int((np.log(self.max_value) - np.log(self.min_value)) / np.log(self.step)) + 1
            return list(np.logspace(
                np.log10(self.min_value),
                np.log10(self.max_value),
                num_steps
            ))
        else:
            # Linear scale
            return list(np.arange(self.min_value, self.max_value + self.step / 2, self.step))


class ParameterGrid(BaseModel):
    """Complete parameter grid definition (X × Y × Z)."""
    x_axis: ParameterDefinition = Field(..., description="X-axis parameter")
    y_axis: ParameterDefinition = Field(..., description="Y-axis parameter")
    z_axis: ParameterDefinition = Field(..., description="Z-axis parameter")

    @property
    def total_combinations(self) -> int:
        """Total number of parameter combinations."""
        return self.x_axis.count * self.y_axis.count * self.z_axis.count

    def get_combination(self, index: int) -> Dict[str, Any]:
        """Get parameter values for a specific combination index."""
        x_count = self.x_axis.count
        y_count = self.y_axis.count
        z_count = self.z_axis.count

        z_idx = index // (x_count * y_count)
        y_idx = (index % (x_count * y_count)) // x_count
        x_idx = index % x_count

        return {
            self.x_axis.name: self.x_axis.values[x_idx],
            self.y_axis.name: self.y_axis.values[y_idx],
            self.z_axis.name: self.z_axis.values[z_idx],
        }


# Workflow Configuration

class WorkflowConfig(BaseModel):
    """Base workflow configuration."""
    template: WorkflowTemplate = Field(..., description="Workflow template to use")
    prompt: str = Field(..., description="Positive prompt")
    negative_prompt: str = Field(default="", description="Negative prompt")
    checkpoint: str = Field(..., description="Model checkpoint name")
    width: int = Field(default=512, ge=64, le=2048, description="Image width")
    height: int = Field(default=512, ge=64, le=2048, description="Image height")
    batch_size: int = Field(default=1, ge=1, le=4, description="Batch size")
    seed: int = Field(default=-1, description="Random seed (-1 for random)")

    # Optional workflow-specific parameters
    vae: Optional[str] = Field(default=None, description="VAE model name")
    loras: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="LoRA configurations"
    )
    controlnet: Optional[Dict[str, Any]] = Field(
        default=None, description="ControlNet configuration"
    )


# Experiment Models

class ExperimentCreate(BaseModel):
    """Request to create a new experiment."""
    name: str = Field(..., description="Experiment name", min_length=1, max_length=200)
    description: Optional[str] = Field(default="", description="Experiment description")
    parameter_grid: ParameterGrid = Field(..., description="Parameter grid definition")
    workflow_config: WorkflowConfig = Field(..., description="Base workflow configuration")

    # Optional settings
    multi_seed: bool = Field(default=False, description="Generate multiple seeds per combination")
    num_seeds: int = Field(default=1, ge=1, le=10, description="Number of seeds if multi_seed")
    enable_wandb: bool = Field(default=False, description="Enable W&B logging")
    wandb_tags: List[str] = Field(default_factory=list, description="W&B tags")


class ExperimentResponse(BaseModel):
    """Experiment response model."""
    id: UUID = Field(default_factory=uuid4, description="Experiment UUID")
    name: str
    description: str
    status: ExperimentStatus
    parameter_grid: ParameterGrid
    workflow_config: WorkflowConfig

    total_images: int = Field(..., description="Total images to generate")
    images_generated: int = Field(default=0, description="Images generated so far")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress (0.0-1.0)")

    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None
    wandb_run_id: Optional[str] = None
    wandb_run_url: Optional[str] = None

    class Config:
        from_attributes = True


class ExperimentUpdate(BaseModel):
    """Update experiment fields."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ExperimentStatus] = None


# Generated Image Models

class GeneratedImage(BaseModel):
    """Single generated image with metadata."""
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID

    # Parameter values for this image
    parameters: Dict[str, Any] = Field(..., description="Parameter combination")

    # Image info
    image_path: str = Field(..., description="Relative path to image file")
    thumbnail_path: Optional[str] = Field(None, description="Relative path to thumbnail")

    # Generation metadata
    seed: int
    generation_time: float = Field(..., description="Generation time in seconds")

    # Optional metrics
    metrics: Dict[str, float] = Field(default_factory=dict, description="Quality metrics")

    created_at: datetime

    class Config:
        from_attributes = True


# Enum Response Models

class EnumValuesResponse(BaseModel):
    """Response containing enum values."""
    enum_name: str = Field(..., description="Enum identifier")
    values: List[str] = Field(..., description="Available values")
    display_names: Optional[Dict[str, str]] = Field(
        default=None, description="Mapping of values to display names"
    )


class AvailableEnumsResponse(BaseModel):
    """Response with all available enums."""
    samplers: List[str]
    schedulers: List[str]
    checkpoints: List[str]
    vaes: List[str]
    loras: List[str]
    upscale_models: List[str]


# Code Generation Models

class CodeGenerateRequest(BaseModel):
    """Request to generate ComfyScript code."""
    parameter_grid: ParameterGrid
    workflow_config: WorkflowConfig


class CodeGenerateResponse(BaseModel):
    """Response with generated code."""
    code: str = Field(..., description="Generated ComfyScript code")
    workflow_json: Optional[Dict[str, Any]] = Field(
        None, description="Workflow in ComfyUI API format"
    )


# Wandb Models

class WandbSyncRequest(BaseModel):
    """Request to sync experiment to W&B."""
    experiment_id: UUID
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class WandbSyncResponse(BaseModel):
    """Response from W&B sync."""
    success: bool
    run_id: str
    run_url: str
    artifacts_uploaded: int


# WebSocket Messages

class WSMessage(BaseModel):
    """Base WebSocket message."""
    type: str
    timestamp: datetime = Field(default_factory=datetime.now)


class WSGenerationStarted(WSMessage):
    """WebSocket: Generation started."""
    type: str = "generation_started"
    experiment_id: UUID
    total_images: int


class WSImageGenerated(WSMessage):
    """WebSocket: Single image generated."""
    type: str = "image_generated"
    experiment_id: UUID
    image_index: int
    image_path: str
    parameters: Dict[str, Any]
    progress: float


class WSBatchCompleted(WSMessage):
    """WebSocket: Batch of images completed."""
    type: str = "batch_completed"
    experiment_id: UUID
    z_value: Any
    images_count: int


class WSExperimentCompleted(WSMessage):
    """WebSocket: Experiment completed."""
    type: str = "experiment_completed"
    experiment_id: UUID
    total_images: int
    total_time: float


class WSError(WSMessage):
    """WebSocket: Error occurred."""
    type: str = "error"
    experiment_id: Optional[UUID] = None
    message: str
    code: str


# Health Check

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    comfyui_connected: bool
    redis_connected: bool
