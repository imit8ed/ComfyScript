"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """Create FastAPI test client."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_parameter_grid():
    """Sample parameter grid for testing."""
    from app.models import ParameterGrid, ParameterDefinition, ParameterType

    return ParameterGrid(
        x_axis=ParameterDefinition(
            name="cfg",
            display_name="CFG Scale",
            type=ParameterType.NUMERIC,
            values=[4.0, 6.0, 8.0, 10.0],
        ),
        y_axis=ParameterDefinition(
            name="steps",
            display_name="Steps",
            type=ParameterType.NUMERIC,
            values=[15, 20, 25, 30],
        ),
        z_axis=ParameterDefinition(
            name="sampler_name",
            display_name="Sampler",
            type=ParameterType.ENUM,
            values=["euler", "dpmpp_2m", "uni_pc"],
        ),
    )


@pytest.fixture
def sample_workflow_config():
    """Sample workflow configuration for testing."""
    from app.models import WorkflowConfig, WorkflowTemplate

    return WorkflowConfig(
        template=WorkflowTemplate.TXT2IMG,
        prompt="A beautiful landscape, highly detailed",
        negative_prompt="low quality, blurry",
        checkpoint="v1-5-pruned-emaonly.safetensors",
        width=512,
        height=512,
        seed=42,
    )


@pytest.fixture
def sample_experiment_create(sample_parameter_grid, sample_workflow_config):
    """Sample experiment creation request."""
    from app.models import ExperimentCreate

    return ExperimentCreate(
        name="Test XYZ Plot",
        description="Testing CFG vs Steps vs Sampler",
        parameter_grid=sample_parameter_grid,
        workflow_config=sample_workflow_config,
        enable_wandb=False,
    )
