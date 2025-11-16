"""
SQLAlchemy database models for persistence.
"""

import json
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Experiment(Base):
    """Experiment database model."""

    __tablename__ = "experiments"

    # Primary key - compatible with both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Basic info
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, default="")
    status = Column(String(20), nullable=False, default="draft", index=True)

    # Configuration stored as JSON
    parameter_grid_json = Column(JSON, nullable=False)
    workflow_config_json = Column(JSON, nullable=False)

    # Statistics
    total_images = Column(Integer, nullable=False)
    images_generated = Column(Integer, default=0)
    progress = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # W&B integration
    wandb_run_id = Column(String(100), nullable=True)
    wandb_run_url = Column(String(500), nullable=True)

    # Relationships
    images = relationship("Image", back_populates="experiment", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "parameter_grid": json.loads(self.parameter_grid_json) if isinstance(self.parameter_grid_json, str) else self.parameter_grid_json,
            "workflow_config": json.loads(self.workflow_config_json) if isinstance(self.workflow_config_json, str) else self.workflow_config_json,
            "total_images": self.total_images,
            "images_generated": self.images_generated,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "wandb_run_id": self.wandb_run_id,
            "wandb_run_url": self.wandb_run_url,
        }


class Image(Base):
    """Generated image database model."""

    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False, index=True)

    # Parameter values for this image
    parameters_json = Column(JSON, nullable=False)

    # Image paths
    image_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)

    # Generation metadata
    seed = Column(Integer, nullable=False)
    generation_time = Column(Float, nullable=False)

    # Metrics
    metrics_json = Column(JSON, default=dict)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    experiment = relationship("Experiment", back_populates="images")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "parameters": json.loads(self.parameters_json) if isinstance(self.parameters_json, str) else self.parameters_json,
            "image_path": self.image_path,
            "thumbnail_path": self.thumbnail_path,
            "seed": self.seed,
            "generation_time": self.generation_time,
            "metrics": json.loads(self.metrics_json) if isinstance(self.metrics_json, str) else self.metrics_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
