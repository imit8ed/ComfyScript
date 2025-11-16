"""
Service for executing experiments and generating images.
"""

import asyncio
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from uuid import UUID

from app.core.config import get_settings
from app.models.schemas import (
    ExperimentCreate,
    ExperimentStatus,
    ParameterGrid,
    WorkflowConfig,
)

logger = logging.getLogger(__name__)


class ExperimentExecutor:
    """Executes XYZ plot experiments using ComfyScript."""

    def __init__(self):
        """Initialize experiment executor."""
        self.settings = get_settings()
        self._running_experiments: Dict[str, bool] = {}

    async def execute_experiment(
        self,
        experiment_id: UUID,
        parameter_grid: ParameterGrid,
        workflow_config: WorkflowConfig,
        progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute an XYZ plot experiment.

        Args:
            experiment_id: Experiment UUID
            parameter_grid: Parameter grid definition
            workflow_config: Workflow configuration
            progress_callback: Optional callback for progress updates
            error_callback: Optional callback for errors

        Returns:
            List of generated image metadata
        """
        exp_id_str = str(experiment_id)
        self._running_experiments[exp_id_str] = True

        try:
            logger.info(f"Starting experiment {experiment_id}")

            # Ensure output directory exists
            output_dir = Path(self.settings.output_dir) / exp_id_str
            output_dir.mkdir(parents=True, exist_ok=True)

            # Import ComfyScript
            from comfy_script.runtime import Workflow
            from comfy_script.runtime.nodes import (
                CheckpointLoaderSimple,
                CLIPTextEncode,
                EmptyLatentImage,
                KSampler,
                SaveImage,
                VAEDecode,
            )

            results = []
            total_combinations = parameter_grid.total_combinations
            current_index = 0

            # Get base parameters
            prompt = workflow_config.prompt
            negative_prompt = workflow_config.negative_prompt
            checkpoint = workflow_config.checkpoint
            width = workflow_config.width
            height = workflow_config.height
            seed_base = workflow_config.seed if workflow_config.seed >= 0 else random.randint(0, 2**32-1)

            # Execute workflow
            with Workflow():
                # Load base models
                model, clip, vae = CheckpointLoaderSimple(checkpoint)

                # Triple loop for XYZ
                for z_idx, z_value in enumerate(parameter_grid.z_axis.values):
                    for y_idx, y_value in enumerate(parameter_grid.y_axis.values):
                        for x_idx, x_value in enumerate(parameter_grid.x_axis.values):

                            # Check if experiment was cancelled
                            if not self._running_experiments.get(exp_id_str, False):
                                logger.info(f"Experiment {experiment_id} cancelled")
                                return results

                            # Build parameter dict
                            params = {
                                parameter_grid.x_axis.name: x_value,
                                parameter_grid.y_axis.name: y_value,
                                parameter_grid.z_axis.name: z_value,
                            }

                            # Generate unique seed
                            seed = seed_base + current_index

                            # Start timing
                            start_time = time.time()

                            # Generate filename
                            filename = f"{x_idx}_{y_idx}_{z_idx}"

                            try:
                                # Create latent
                                latent = EmptyLatentImage(width, height, 1)

                                # Encode prompts
                                positive = CLIPTextEncode(prompt, clip)
                                negative = CLIPTextEncode(negative_prompt, clip)

                                # Build KSampler arguments based on parameters
                                sampler_kwargs = self._build_sampler_kwargs(
                                    params,
                                    parameter_grid,
                                    seed,
                                )

                                # Sample
                                latent = KSampler(
                                    model,
                                    **sampler_kwargs,
                                    positive=positive,
                                    negative=negative,
                                    latent_image=latent,
                                )

                                # Decode
                                image = VAEDecode(latent, vae)

                                # Save
                                save_result = SaveImage(image, filename)

                                # Calculate generation time
                                generation_time = time.time() - start_time

                                # Get image path
                                # In real implementation, extract from save_result
                                image_path = f"{filename}.png"

                                # Store result
                                result = {
                                    "parameters": params,
                                    "image_path": image_path,
                                    "seed": seed,
                                    "generation_time": generation_time,
                                    "index": current_index,
                                }
                                results.append(result)

                                # Progress callback
                                if progress_callback:
                                    progress_callback(current_index + 1, total_combinations, result)

                                logger.debug(
                                    f"Generated image {current_index + 1}/{total_combinations}: {params}"
                                )

                            except Exception as e:
                                logger.error(f"Failed to generate image {current_index}: {e}")
                                if error_callback:
                                    error_callback(f"Image {current_index} failed: {str(e)}")

                            current_index += 1

            logger.info(f"Experiment {experiment_id} completed: {len(results)} images generated")
            return results

        except Exception as e:
            logger.error(f"Experiment {experiment_id} failed: {e}", exc_info=True)
            if error_callback:
                error_callback(str(e))
            raise

        finally:
            self._running_experiments.pop(exp_id_str, None)

    def _build_sampler_kwargs(
        self,
        params: Dict[str, Any],
        parameter_grid: ParameterGrid,
        seed: int,
    ) -> Dict[str, Any]:
        """Build KSampler keyword arguments from parameters."""
        kwargs = {
            "seed": seed,
            "steps": 20,
            "cfg": 8.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
        }

        # Override with parameter values
        if "steps" in params:
            kwargs["steps"] = int(params["steps"])
        if "cfg" in params:
            kwargs["cfg"] = float(params["cfg"])
        if "sampler_name" in params or "sampler" in params:
            kwargs["sampler_name"] = params.get("sampler_name", params.get("sampler"))
        if "scheduler" in params:
            kwargs["scheduler"] = params["scheduler"]
        if "denoise" in params:
            kwargs["denoise"] = float(params["denoise"])

        return kwargs

    async def cancel_experiment(self, experiment_id: UUID) -> bool:
        """
        Cancel a running experiment.

        Args:
            experiment_id: Experiment UUID

        Returns:
            True if cancelled, False if not running
        """
        exp_id_str = str(experiment_id)
        if exp_id_str in self._running_experiments:
            self._running_experiments[exp_id_str] = False
            logger.info(f"Experiment {experiment_id} marked for cancellation")
            return True
        return False

    def is_running(self, experiment_id: UUID) -> bool:
        """Check if experiment is currently running."""
        return self._running_experiments.get(str(experiment_id), False)


# Global instance
_executor_instance: Optional[ExperimentExecutor] = None


def get_experiment_executor() -> ExperimentExecutor:
    """Get global experiment executor instance."""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ExperimentExecutor()
    return _executor_instance
