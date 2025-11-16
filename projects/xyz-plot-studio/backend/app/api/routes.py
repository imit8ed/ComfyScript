"""
API routes for XYZ Plot Studio.
"""

import asyncio
import logging
from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.models import (
    AvailableEnumsResponse,
    CodeGenerateRequest,
    CodeGenerateResponse,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatus,
    HealthResponse,
    WandbSyncRequest,
    WandbSyncResponse,
)
from app.services import (
    get_enum_service,
    get_experiment_executor,
    get_wandb_service,
    get_workflow_generator,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Health check

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()

    # Check ComfyUI connection
    comfyui_connected = False
    try:
        enum_service = get_enum_service()
        await enum_service.initialize()
        comfyui_connected = True
    except Exception as e:
        logger.warning(f"ComfyUI health check failed: {e}")

    # Check Redis (simplified - would need actual Redis client)
    redis_connected = True  # TODO: implement actual Redis check

    from app import __version__

    return HealthResponse(
        status="healthy" if comfyui_connected else "degraded",
        version=__version__,
        comfyui_connected=comfyui_connected,
        redis_connected=redis_connected,
    )


# Enums

@router.get("/enums", response_model=AvailableEnumsResponse)
async def get_all_enums():
    """Get all available enums from ComfyScript."""
    try:
        enum_service = get_enum_service()
        enums = await enum_service.get_all_enums()

        return AvailableEnumsResponse(
            samplers=enums.get("samplers", []),
            schedulers=enums.get("schedulers", []),
            checkpoints=enums.get("checkpoints", []),
            vaes=enums.get("vaes", []),
            loras=enums.get("loras", []),
            upscale_models=enums.get("upscale_models", []),
        )
    except Exception as e:
        logger.error(f"Failed to get enums: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enums: {str(e)}")


@router.get("/enums/{enum_name}")
async def get_enum_values(enum_name: str):
    """Get values for a specific enum."""
    try:
        enum_service = get_enum_service()
        values = await enum_service.get_enum_values(enum_name)

        if not values:
            raise HTTPException(status_code=404, detail=f"Enum '{enum_name}' not found")

        return {"enum_name": enum_name, "values": values}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get enum values: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enum values: {str(e)}")


# Code Generation

@router.post("/code/generate", response_model=CodeGenerateResponse)
async def generate_code(request: CodeGenerateRequest):
    """Generate ComfyScript code from parameter grid."""
    try:
        generator = get_workflow_generator()

        code = generator.generate_script(
            request.parameter_grid,
            request.workflow_config,
        )

        workflow_json = generator.generate_workflow_json(
            request.parameter_grid,
            request.workflow_config,
        )

        return CodeGenerateResponse(
            code=code,
            workflow_json=workflow_json,
        )
    except Exception as e:
        logger.error(f"Failed to generate code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate code: {str(e)}")


# Experiments

# In-memory storage for demo (would use database in production)
_experiments: Dict[str, ExperimentResponse] = {}


@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(experiment: ExperimentCreate):
    """Create a new experiment."""
    try:
        # Validate total images
        total_images = experiment.parameter_grid.total_combinations
        if experiment.multi_seed:
            total_images *= experiment.num_seeds

        settings = get_settings()
        if total_images > settings.max_images_per_experiment:
            raise HTTPException(
                status_code=400,
                detail=f"Total images ({total_images}) exceeds maximum ({settings.max_images_per_experiment})",
            )

        # Create experiment response
        exp_response = ExperimentResponse(
            id=uuid4(),
            name=experiment.name,
            description=experiment.description,
            status=ExperimentStatus.DRAFT,
            parameter_grid=experiment.parameter_grid,
            workflow_config=experiment.workflow_config,
            total_images=total_images,
            images_generated=0,
            progress=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Store (in-memory for now)
        _experiments[str(exp_response.id)] = exp_response

        logger.info(f"Created experiment: {exp_response.id} ({exp_response.name})")
        return exp_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create experiment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create experiment: {str(e)}")


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: UUID):
    """Get experiment by ID."""
    exp_id_str = str(experiment_id)
    if exp_id_str not in _experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return _experiments[exp_id_str]


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments():
    """List all experiments."""
    return list(_experiments.values())


@router.post("/experiments/{experiment_id}/execute")
async def execute_experiment(experiment_id: UUID):
    """Start experiment execution."""
    exp_id_str = str(experiment_id)
    if exp_id_str not in _experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    experiment = _experiments[exp_id_str]

    if experiment.status == ExperimentStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Experiment is already running")

    # Update status
    experiment.status = ExperimentStatus.QUEUED
    experiment.updated_at = datetime.now()

    # Execute in background
    asyncio.create_task(_execute_experiment_background(experiment))

    return {"message": "Experiment queued for execution", "experiment_id": experiment_id}


async def _execute_experiment_background(experiment: ExperimentResponse):
    """Background task to execute experiment."""
    from datetime import datetime

    try:
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        experiment.updated_at = datetime.now()

        executor = get_experiment_executor()

        def progress_callback(current: int, total: int, result: Dict):
            experiment.images_generated = current
            experiment.progress = current / total
            experiment.updated_at = datetime.now()
            logger.info(f"Experiment {experiment.id} progress: {current}/{total}")

        def error_callback(error_msg: str):
            experiment.error_message = error_msg
            experiment.updated_at = datetime.now()

        # Execute
        results = await executor.execute_experiment(
            experiment.id,
            experiment.parameter_grid,
            experiment.workflow_config,
            progress_callback=progress_callback,
            error_callback=error_callback,
        )

        # Mark complete
        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.now()
        experiment.updated_at = datetime.now()

        logger.info(f"Experiment {experiment.id} completed successfully")

    except Exception as e:
        logger.error(f"Experiment {experiment.id} failed: {e}")
        experiment.status = ExperimentStatus.FAILED
        experiment.error_message = str(e)
        experiment.updated_at = datetime.now()


@router.post("/experiments/{experiment_id}/cancel")
async def cancel_experiment(experiment_id: UUID):
    """Cancel a running experiment."""
    exp_id_str = str(experiment_id)
    if exp_id_str not in _experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    experiment = _experiments[exp_id_str]

    if experiment.status != ExperimentStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Experiment is not running")

    executor = get_experiment_executor()
    cancelled = await executor.cancel_experiment(experiment_id)

    if cancelled:
        experiment.status = ExperimentStatus.CANCELLED
        experiment.updated_at = datetime.now()
        return {"message": "Experiment cancelled"}
    else:
        raise HTTPException(status_code=500, detail="Failed to cancel experiment")


# W&B Integration

@router.post("/wandb/sync", response_model=WandbSyncResponse)
async def sync_to_wandb(request: WandbSyncRequest):
    """Sync experiment to Weights & Biases."""
    exp_id_str = str(request.experiment_id)
    if exp_id_str not in _experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    experiment = _experiments[exp_id_str]

    try:
        wandb_service = get_wandb_service()

        # Create W&B run
        run_id = wandb_service.create_run(
            experiment_id=request.experiment_id,
            experiment_name=experiment.name,
            config={
                "parameter_grid": experiment.parameter_grid.dict(),
                "workflow_config": experiment.workflow_config.dict(),
                "total_images": experiment.total_images,
            },
            tags=request.tags,
            project=request.wandb_project,
            entity=request.wandb_entity,
        )

        if not run_id:
            raise HTTPException(status_code=500, detail="Failed to create W&B run")

        # Get run URL
        run_url = wandb_service.get_run_url() or ""

        # Update experiment
        experiment.wandb_run_id = run_id
        experiment.wandb_run_url = run_url
        experiment.updated_at = datetime.now()

        # Log images (simplified - would iterate through generated images)
        artifacts_uploaded = 0

        wandb_service.finish_run()

        return WandbSyncResponse(
            success=True,
            run_id=run_id,
            run_url=run_url,
            artifacts_uploaded=artifacts_uploaded,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync to W&B: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync to W&B: {str(e)}")


# WebSocket for real-time updates

@router.websocket("/ws/experiments/{experiment_id}")
async def experiment_websocket(websocket: WebSocket, experiment_id: UUID):
    """WebSocket endpoint for real-time experiment updates."""
    await websocket.accept()

    exp_id_str = str(experiment_id)

    try:
        # Send initial status
        if exp_id_str in _experiments:
            experiment = _experiments[exp_id_str]
            await websocket.send_json({
                "type": "status",
                "data": experiment.dict(),
            })

        # Keep connection alive and send updates
        while True:
            # Poll for updates (in production, use pub/sub)
            await asyncio.sleep(1)

            if exp_id_str in _experiments:
                experiment = _experiments[exp_id_str]
                await websocket.send_json({
                    "type": "update",
                    "data": {
                        "status": experiment.status,
                        "progress": experiment.progress,
                        "images_generated": experiment.images_generated,
                    },
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for experiment {experiment_id}")
    except Exception as e:
        logger.error(f"WebSocket error for experiment {experiment_id}: {e}")
        await websocket.close()


# Import datetime for background task
from datetime import datetime
