"""
Tests for Pydantic models and schemas.
"""

import pytest
from pydantic import ValidationError

from app.models import (
    ParameterDefinition,
    ParameterGrid,
    ParameterType,
    NumericParameterRange,
    WorkflowConfig,
    WorkflowTemplate,
    ExperimentCreate,
)


class TestParameterDefinition:
    """Tests for ParameterDefinition model."""

    def test_valid_numeric_parameter(self):
        """Test creating a valid numeric parameter."""
        param = ParameterDefinition(
            name="cfg",
            display_name="CFG Scale",
            type=ParameterType.NUMERIC,
            values=[4.0, 6.0, 8.0, 10.0],
        )
        assert param.name == "cfg"
        assert param.count == 4
        assert all(isinstance(v, float) for v in param.values)

    def test_valid_categorical_parameter(self):
        """Test creating a valid categorical parameter."""
        param = ParameterDefinition(
            name="sampler",
            display_name="Sampler",
            type=ParameterType.CATEGORICAL,
            values=["euler", "dpmpp_2m", "uni_pc"],
        )
        assert param.name == "sampler"
        assert param.count == 3

    def test_empty_values_raises_error(self):
        """Test that empty values list raises error."""
        with pytest.raises(ValidationError):
            ParameterDefinition(
                name="test",
                display_name="Test",
                type=ParameterType.NUMERIC,
                values=[],
            )

    def test_mixed_types_raises_error(self):
        """Test that mixed value types raise error."""
        with pytest.raises(ValidationError):
            ParameterDefinition(
                name="test",
                display_name="Test",
                type=ParameterType.NUMERIC,
                values=[1, 2.0, "3"],  # Mixed types
            )


class TestNumericParameterRange:
    """Tests for NumericParameterRange helper."""

    def test_linear_range(self):
        """Test linear range generation."""
        range_def = NumericParameterRange(
            min_value=1.0,
            max_value=5.0,
            step=1.0,
            logarithmic=False,
        )
        values = range_def.to_values()
        assert len(values) == 5
        assert values == [1.0, 2.0, 3.0, 4.0, 5.0]

    def test_fractional_steps(self):
        """Test range with fractional steps."""
        range_def = NumericParameterRange(
            min_value=0.0,
            max_value=1.0,
            step=0.25,
            logarithmic=False,
        )
        values = range_def.to_values()
        assert len(values) == 5
        assert abs(values[2] - 0.5) < 0.01


class TestParameterGrid:
    """Tests for ParameterGrid model."""

    def test_total_combinations(self, sample_parameter_grid):
        """Test total combinations calculation."""
        # 4 CFG × 4 Steps × 3 Samplers = 48
        assert sample_parameter_grid.total_combinations == 48

    def test_get_combination(self, sample_parameter_grid):
        """Test getting specific combination by index."""
        # First combination
        combo = sample_parameter_grid.get_combination(0)
        assert combo["cfg"] == 4.0
        assert combo["steps"] == 15
        assert combo["sampler_name"] == "euler"

        # Last combination
        combo = sample_parameter_grid.get_combination(47)
        assert combo["cfg"] == 10.0
        assert combo["steps"] == 30
        assert combo["sampler_name"] == "uni_pc"


class TestWorkflowConfig:
    """Tests for WorkflowConfig model."""

    def test_valid_txt2img_config(self, sample_workflow_config):
        """Test valid txt2img configuration."""
        assert sample_workflow_config.template == WorkflowTemplate.TXT2IMG
        assert sample_workflow_config.width == 512
        assert sample_workflow_config.height == 512

    def test_dimension_validation(self):
        """Test image dimension validation."""
        # Too small
        with pytest.raises(ValidationError):
            WorkflowConfig(
                template=WorkflowTemplate.TXT2IMG,
                prompt="test",
                checkpoint="test.safetensors",
                width=32,  # Below minimum
                height=512,
            )

        # Too large
        with pytest.raises(ValidationError):
            WorkflowConfig(
                template=WorkflowTemplate.TXT2IMG,
                prompt="test",
                checkpoint="test.safetensors",
                width=4096,  # Above maximum
                height=512,
            )


class TestExperimentCreate:
    """Tests for ExperimentCreate model."""

    def test_valid_experiment(self, sample_experiment_create):
        """Test creating a valid experiment."""
        assert sample_experiment_create.name == "Test XYZ Plot"
        assert not sample_experiment_create.enable_wandb
        assert sample_experiment_create.num_seeds == 1

    def test_multi_seed_experiment(self, sample_parameter_grid, sample_workflow_config):
        """Test experiment with multiple seeds."""
        experiment = ExperimentCreate(
            name="Multi-seed Test",
            description="Testing with multiple seeds",
            parameter_grid=sample_parameter_grid,
            workflow_config=sample_workflow_config,
            multi_seed=True,
            num_seeds=5,
        )
        assert experiment.multi_seed
        assert experiment.num_seeds == 5

    def test_empty_name_raises_error(self, sample_parameter_grid, sample_workflow_config):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError):
            ExperimentCreate(
                name="",  # Empty name
                description="Test",
                parameter_grid=sample_parameter_grid,
                workflow_config=sample_workflow_config,
            )
