"""
Service for W&B (Weights & Biases) integration.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WandbService:
    """Service for logging experiments to Weights & Biases."""

    def __init__(self):
        """Initialize W&B service."""
        self.settings = get_settings()
        self._initialized = False
        self._wandb = None

    def initialize(self) -> None:
        """Initialize W&B with API key."""
        if self._initialized:
            return

        try:
            import wandb
            self._wandb = wandb

            if self.settings.wandb_api_key:
                wandb.login(key=self.settings.wandb_api_key)
                self._initialized = True
                logger.info("W&B initialized successfully")
            else:
                logger.warning("W&B API key not set - W&B logging disabled")

        except ImportError:
            logger.warning("wandb package not installed - W&B logging disabled")
        except Exception as e:
            logger.error(f"Failed to initialize W&B: {e}")

    def create_run(
        self,
        experiment_id: UUID,
        experiment_name: str,
        config: Dict[str, Any],
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
        entity: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a new W&B run for an experiment.

        Args:
            experiment_id: Experiment UUID
            experiment_name: Experiment name
            config: Experiment configuration
            tags: Optional tags
            project: Optional project name (overrides default)
            entity: Optional entity name (overrides default)

        Returns:
            Run ID if successful, None otherwise
        """
        if not self._initialized:
            self.initialize()

        if not self._wandb or not self._initialized:
            logger.warning("W&B not available - skipping run creation")
            return None

        try:
            run = self._wandb.init(
                project=project or self.settings.wandb_project,
                entity=entity or self.settings.wandb_entity or None,
                name=experiment_name,
                id=str(experiment_id),
                config=config,
                tags=tags or [],
                reinit=True,
            )

            logger.info(f"Created W&B run: {run.id} ({run.url})")
            return run.id

        except Exception as e:
            logger.error(f"Failed to create W&B run: {e}")
            return None

    def log_image(
        self,
        image_path: str,
        caption: str,
        parameters: Dict[str, Any],
    ) -> bool:
        """
        Log an image to current W&B run.

        Args:
            image_path: Path to image file
            caption: Image caption
            parameters: Parameter values for this image

        Returns:
            True if successful, False otherwise
        """
        if not self._wandb or not self._initialized:
            return False

        try:
            import wandb

            # Create W&B Image object
            image = wandb.Image(
                image_path,
                caption=caption,
                metadata=parameters,
            )

            # Log to W&B
            wandb.log({"images": image, **parameters})

            return True

        except Exception as e:
            logger.error(f"Failed to log image to W&B: {e}")
            return False

    def log_images_batch(
        self,
        images_data: List[Dict[str, Any]],
    ) -> int:
        """
        Log multiple images to W&B in a batch.

        Args:
            images_data: List of dicts with 'path', 'caption', 'parameters'

        Returns:
            Number of images successfully logged
        """
        if not self._wandb or not self._initialized:
            return 0

        try:
            import wandb

            images = []
            for data in images_data:
                image = wandb.Image(
                    data["path"],
                    caption=data.get("caption", ""),
                    metadata=data.get("parameters", {}),
                )
                images.append(image)

            # Log all images at once
            wandb.log({"experiment_images": images})

            logger.info(f"Logged {len(images)} images to W&B")
            return len(images)

        except Exception as e:
            logger.error(f"Failed to log image batch to W&B: {e}")
            return 0

    def log_table(
        self,
        table_name: str,
        columns: List[str],
        data: List[List[Any]],
    ) -> bool:
        """
        Log a table to W&B.

        Args:
            table_name: Name of the table
            columns: Column names
            data: Table data (list of rows)

        Returns:
            True if successful, False otherwise
        """
        if not self._wandb or not self._initialized:
            return False

        try:
            import wandb

            table = wandb.Table(columns=columns, data=data)
            wandb.log({table_name: table})

            logger.info(f"Logged table '{table_name}' to W&B")
            return True

        except Exception as e:
            logger.error(f"Failed to log table to W&B: {e}")
            return False

    def log_metrics(self, metrics: Dict[str, float]) -> bool:
        """
        Log metrics to W&B.

        Args:
            metrics: Dictionary of metric name -> value

        Returns:
            True if successful, False otherwise
        """
        if not self._wandb or not self._initialized:
            return False

        try:
            import wandb
            wandb.log(metrics)
            return True

        except Exception as e:
            logger.error(f"Failed to log metrics to W&B: {e}")
            return False

    def finish_run(self) -> None:
        """Finish the current W&B run."""
        if self._wandb and self._initialized:
            try:
                import wandb
                wandb.finish()
                logger.info("Finished W&B run")
            except Exception as e:
                logger.error(f"Failed to finish W&B run: {e}")

    def get_run_url(self) -> Optional[str]:
        """Get URL of current W&B run."""
        if self._wandb and self._initialized:
            try:
                import wandb
                if wandb.run:
                    return wandb.run.url
            except Exception as e:
                logger.error(f"Failed to get W&B run URL: {e}")
        return None


# Global instance
_wandb_service_instance: Optional[WandbService] = None


def get_wandb_service() -> WandbService:
    """Get global W&B service instance."""
    global _wandb_service_instance
    if _wandb_service_instance is None:
        _wandb_service_instance = WandbService()
    return _wandb_service_instance
