"""
Tests for service layer.
"""

import pytest

from app.services import (
    get_workflow_generator,
)
from app.models import WorkflowTemplate


class TestWorkflowGenerator:
    """Tests for WorkflowGenerator service."""

    def test_generate_txt2img_script(self, sample_parameter_grid, sample_workflow_config):
        """Test generating txt2img script."""
        generator = get_workflow_generator()

        script = generator.generate_script(
            sample_parameter_grid,
            sample_workflow_config,
        )

        # Verify script contains expected elements
        assert "from comfy_script.runtime import *" in script
        assert "load()" in script
        assert "CheckpointLoaderSimple" in script
        assert "KSampler" in script
        assert "SaveImage" in script

        # Verify parameter loops
        assert "for z_idx, sampler_name in enumerate(sampler_name_values)" in script
        assert "for y_idx, steps in enumerate(steps_values)" in script
        assert "for x_idx, cfg in enumerate(cfg_values)" in script

        # Verify parameter values
        assert "[4.0, 6.0, 8.0, 10.0]" in script
        assert "[15, 20, 25, 30]" in script
        assert "['euler', 'dpmpp_2m', 'uni_pc']" in script

    def test_generate_workflow_json(self, sample_parameter_grid, sample_workflow_config):
        """Test generating workflow JSON."""
        generator = get_workflow_generator()

        workflow_json = generator.generate_workflow_json(
            sample_parameter_grid,
            sample_workflow_config,
        )

        # Verify metadata
        assert "metadata" in workflow_json
        assert workflow_json["metadata"]["total_combinations"] == 48

    def test_unsupported_template_raises_error(self, sample_parameter_grid):
        """Test that unsupported template raises error."""
        from app.models import WorkflowConfig

        generator = get_workflow_generator()

        # Create config with CUSTOM template (not implemented)
        config = WorkflowConfig(
            template=WorkflowTemplate.CUSTOM,
            prompt="test",
            checkpoint="test.safetensors",
        )

        with pytest.raises(ValueError, match="Unsupported template"):
            generator.generate_script(sample_parameter_grid, config)


class TestEnumService:
    """Tests for EnumService."""

    @pytest.mark.asyncio
    async def test_enum_service_initialization(self):
        """Test enum service can initialize (may fail without ComfyUI)."""
        from app.services import get_enum_service

        enum_service = get_enum_service()

        # This may fail if ComfyUI is not running - that's expected
        try:
            await enum_service.initialize()
            assert enum_service._initialized
        except RuntimeError:
            # ComfyUI not available - skip test
            pytest.skip("ComfyUI not available")

    @pytest.mark.asyncio
    async def test_get_samplers(self):
        """Test getting sampler enums."""
        from app.services import get_enum_service

        enum_service = get_enum_service()

        try:
            samplers = await enum_service.get_samplers()
            # If ComfyUI is available, we should get samplers
            assert isinstance(samplers, list)
        except RuntimeError:
            pytest.skip("ComfyUI not available")

    @pytest.mark.asyncio
    async def test_get_all_enums(self):
        """Test getting all enums."""
        from app.services import get_enum_service

        enum_service = get_enum_service()

        try:
            all_enums = await enum_service.get_all_enums()
            assert isinstance(all_enums, dict)
            assert "samplers" in all_enums
            assert "schedulers" in all_enums
            assert "checkpoints" in all_enums
        except RuntimeError:
            pytest.skip("ComfyUI not available")


class TestExperimentExecutor:
    """Tests for ExperimentExecutor."""

    @pytest.mark.asyncio
    async def test_cancel_experiment(self):
        """Test cancelling an experiment."""
        from uuid import uuid4
        from app.services import get_experiment_executor

        executor = get_experiment_executor()
        exp_id = uuid4()

        # Cancel non-running experiment
        result = await executor.cancel_experiment(exp_id)
        assert result is False

    def test_is_running(self):
        """Test checking if experiment is running."""
        from uuid import uuid4
        from app.services import get_experiment_executor

        executor = get_experiment_executor()
        exp_id = uuid4()

        assert executor.is_running(exp_id) is False


class TestWandbService:
    """Tests for WandbService."""

    def test_wandb_service_initialization(self):
        """Test W&B service initialization."""
        from app.services import get_wandb_service

        wandb_service = get_wandb_service()

        # Initialize (may not work without API key - that's ok)
        wandb_service.initialize()

    def test_create_run_without_wandb(self):
        """Test creating run when W&B not available."""
        from uuid import uuid4
        from app.services import get_wandb_service

        wandb_service = get_wandb_service()

        # Without W&B initialized, should return None
        run_id = wandb_service.create_run(
            experiment_id=uuid4(),
            experiment_name="Test",
            config={},
        )

        # May be None if W&B not configured
        assert run_id is None or isinstance(run_id, str)
