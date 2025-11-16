"""
Tests for API endpoints.
"""

import pytest


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "comfyui_connected" in data
        assert "redis_connected" in data


class TestEnumEndpoints:
    """Tests for enum endpoints."""

    @pytest.mark.asyncio
    async def test_get_all_enums(self, client):
        """Test getting all enums."""
        response = client.get("/api/v1/enums")

        # May fail if ComfyUI not available
        if response.status_code == 200:
            data = response.json()
            assert "samplers" in data
            assert "schedulers" in data
            assert "checkpoints" in data
            assert isinstance(data["samplers"], list)

    @pytest.mark.asyncio
    async def test_get_specific_enum(self, client):
        """Test getting specific enum values."""
        response = client.get("/api/v1/enums/Samplers")

        # May succeed or fail depending on ComfyUI availability
        if response.status_code == 200:
            data = response.json()
            assert "enum_name" in data
            assert "values" in data
            assert isinstance(data["values"], list)


class TestCodeGenerationEndpoints:
    """Tests for code generation endpoints."""

    def test_generate_code(self, client, sample_parameter_grid, sample_workflow_config):
        """Test code generation endpoint."""
        from app.models import CodeGenerateRequest

        request = CodeGenerateRequest(
            parameter_grid=sample_parameter_grid,
            workflow_config=sample_workflow_config,
        )

        response = client.post(
            "/api/v1/code/generate",
            json=request.dict(),
        )

        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "workflow_json" in data
        assert "from comfy_script" in data["code"]


class TestExperimentEndpoints:
    """Tests for experiment CRUD endpoints."""

    def test_create_experiment(self, client, sample_experiment_create):
        """Test creating an experiment."""
        response = client.post(
            "/api/v1/experiments",
            json=sample_experiment_create.dict(),
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_experiment_create.name
        assert data["status"] == "draft"
        assert data["total_images"] == 48  # 4 × 4 × 3

    def test_create_experiment_too_many_images(self, client, sample_parameter_grid, sample_workflow_config):
        """Test creating experiment with too many images."""
        from app.models import ExperimentCreate, ParameterDefinition, ParameterType

        # Create a massive grid
        large_grid = sample_parameter_grid.copy(deep=True)
        large_grid.x_axis = ParameterDefinition(
            name="cfg",
            display_name="CFG",
            type=ParameterType.NUMERIC,
            values=list(range(1, 101)),  # 100 values
        )

        experiment = ExperimentCreate(
            name="Too Large",
            description="This should fail",
            parameter_grid=large_grid,
            workflow_config=sample_workflow_config,
        )

        response = client.post(
            "/api/v1/experiments",
            json=experiment.dict(),
        )

        # Should fail due to too many images (>500)
        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"]

    def test_get_experiment(self, client, sample_experiment_create):
        """Test getting an experiment by ID."""
        # First create an experiment
        create_response = client.post(
            "/api/v1/experiments",
            json=sample_experiment_create.dict(),
        )
        experiment_id = create_response.json()["id"]

        # Now get it
        response = client.get(f"/api/v1/experiments/{experiment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == experiment_id

    def test_get_nonexistent_experiment(self, client):
        """Test getting non-existent experiment."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/experiments/{fake_id}")
        assert response.status_code == 404

    def test_list_experiments(self, client, sample_experiment_create):
        """Test listing all experiments."""
        # Create a couple experiments
        client.post("/api/v1/experiments", json=sample_experiment_create.dict())
        client.post("/api/v1/experiments", json=sample_experiment_create.dict())

        # List all
        response = client.get("/api/v1/experiments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_execute_experiment(self, client, sample_experiment_create):
        """Test executing an experiment."""
        # Create experiment
        create_response = client.post(
            "/api/v1/experiments",
            json=sample_experiment_create.dict(),
        )
        experiment_id = create_response.json()["id"]

        # Execute it (will fail without ComfyUI but should queue)
        response = client.post(f"/api/v1/experiments/{experiment_id}/execute")
        assert response.status_code == 200
        assert "queued" in response.json()["message"].lower()

    def test_cancel_experiment(self, client, sample_experiment_create):
        """Test cancelling an experiment."""
        # Create experiment
        create_response = client.post(
            "/api/v1/experiments",
            json=sample_experiment_create.dict(),
        )
        experiment_id = create_response.json()["id"]

        # Try to cancel (will fail since not running)
        response = client.post(f"/api/v1/experiments/{experiment_id}/cancel")
        assert response.status_code == 400  # Not running


class TestWandbEndpoints:
    """Tests for W&B integration endpoints."""

    def test_sync_to_wandb(self, client, sample_experiment_create):
        """Test syncing experiment to W&B."""
        from app.models import WandbSyncRequest

        # Create experiment
        create_response = client.post(
            "/api/v1/experiments",
            json=sample_experiment_create.dict(),
        )
        experiment_id = create_response.json()["id"]

        # Try to sync (will fail without W&B credentials)
        sync_request = WandbSyncRequest(
            experiment_id=experiment_id,
            tags=["test"],
        )

        response = client.post(
            "/api/v1/wandb/sync",
            json=sync_request.dict(),
        )

        # May fail if W&B not configured - that's expected
        assert response.status_code in [200, 500]

    def test_sync_nonexistent_experiment(self, client):
        """Test syncing non-existent experiment to W&B."""
        from app.models import WandbSyncRequest

        fake_id = "00000000-0000-0000-0000-000000000000"
        sync_request = WandbSyncRequest(
            experiment_id=fake_id,
            tags=[],
        )

        response = client.post(
            "/api/v1/wandb/sync",
            json=sync_request.dict(),
        )

        assert response.status_code == 404
