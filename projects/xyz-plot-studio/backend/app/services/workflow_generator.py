"""
Service for generating ComfyScript workflows from parameter definitions.
"""

import logging
import random
from typing import Any, Dict, List, Tuple

from app.models.schemas import ParameterGrid, WorkflowConfig, WorkflowTemplate

logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """Generates ComfyScript code and workflows."""

    def __init__(self):
        """Initialize workflow generator."""
        pass

    def generate_script(
        self,
        parameter_grid: ParameterGrid,
        workflow_config: WorkflowConfig,
    ) -> str:
        """
        Generate ComfyScript code for the XYZ plot.

        Args:
            parameter_grid: Parameter grid definition
            workflow_config: Base workflow configuration

        Returns:
            Generated Python/ComfyScript code
        """
        template = workflow_config.template

        if template == WorkflowTemplate.TXT2IMG:
            return self._generate_txt2img_script(parameter_grid, workflow_config)
        elif template == WorkflowTemplate.IMG2IMG:
            return self._generate_img2img_script(parameter_grid, workflow_config)
        elif template == WorkflowTemplate.HIRES_FIX:
            return self._generate_hires_fix_script(parameter_grid, workflow_config)
        else:
            raise ValueError(f"Unsupported template: {template}")

    def _generate_txt2img_script(
        self,
        parameter_grid: ParameterGrid,
        workflow_config: WorkflowConfig,
    ) -> str:
        """Generate txt2img workflow script."""
        # Extract base parameters
        prompt = workflow_config.prompt
        negative_prompt = workflow_config.negative_prompt
        checkpoint = workflow_config.checkpoint
        width = workflow_config.width
        height = workflow_config.height
        seed = workflow_config.seed
        batch_size = workflow_config.batch_size

        # Extract parameter names
        x_param = parameter_grid.x_axis.name
        y_param = parameter_grid.y_axis.name
        z_param = parameter_grid.z_axis.name

        # Build parameter value lists
        x_values = self._format_values(parameter_grid.x_axis.values)
        y_values = self._format_values(parameter_grid.y_axis.values)
        z_values = self._format_values(parameter_grid.z_axis.values)

        # Generate script
        script = f'''"""
Auto-generated ComfyScript for XYZ Plot
X-axis: {parameter_grid.x_axis.display_name} ({len(parameter_grid.x_axis.values)} values)
Y-axis: {parameter_grid.y_axis.display_name} ({len(parameter_grid.y_axis.values)} values)
Z-axis: {parameter_grid.z_axis.display_name} ({len(parameter_grid.z_axis.values)} values)
Total combinations: {parameter_grid.total_combinations}
"""

from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

# Parameter definitions
{x_param}_values = {x_values}
{y_param}_values = {y_values}
{z_param}_values = {z_values}

# Base configuration
PROMPT = """{prompt}"""
NEGATIVE_PROMPT = """{negative_prompt}"""
CHECKPOINT = "{checkpoint}"
WIDTH = {width}
HEIGHT = {height}
SEED = {seed}
BATCH_SIZE = {batch_size}

# Results storage
results = []

with Workflow():
    # Load base models
    model, clip, vae = CheckpointLoaderSimple(CHECKPOINT)

    # XYZ loop
    for z_idx, {z_param} in enumerate({z_param}_values):
        for y_idx, {y_param} in enumerate({y_param}_values):
            for x_idx, {x_param} in enumerate({x_param}_values):

                # Generate unique filename
                filename = f"{{x_idx}}_{{y_idx}}_{{z_idx}}_{{{x_param}}}_{{{y_param}}}_{{{z_param}}}"

                # Create latent image
                latent = EmptyLatentImage(WIDTH, HEIGHT, BATCH_SIZE)

                # Encode prompts
                positive = CLIPTextEncode(PROMPT, clip)
                negative = CLIPTextEncode(NEGATIVE_PROMPT, clip)

                # Sample (using parameter sweep values)
                {self._generate_ksampler_call(x_param, y_param, z_param)}

                # Decode and save
                image = VAEDecode(latent, vae)
                result = SaveImage(image, filename)

                results.append({{
                    'x': {x_param},
                    'y': {y_param},
                    'z': {z_param},
                    'filename': filename,
                }})

print(f"Generated {{len(results)}} images")
'''
        return script

    def _generate_ksampler_call(
        self,
        x_param: str,
        y_param: str,
        z_param: str,
    ) -> str:
        """Generate KSampler call with dynamic parameters."""
        # Map common parameter names to KSampler arguments
        param_mapping = {
            'cfg': 'cfg',
            'steps': 'steps',
            'sampler_name': 'sampler_name',
            'sampler': 'sampler_name',
            'scheduler': 'scheduler',
            'denoise': 'denoise',
        }

        # Build KSampler arguments
        args = []
        args.append("model")

        # Seed
        args.append("SEED if SEED >= 0 else random.randint(0, 2**32-1)")

        # Steps - check if it's a parameter
        if any(p in param_mapping and param_mapping[p] == 'steps'
               for p in [x_param, y_param, z_param]):
            args.append("steps=steps")
        else:
            args.append("steps=20")

        # CFG - check if it's a parameter
        if any(p in param_mapping and param_mapping[p] == 'cfg'
               for p in [x_param, y_param, z_param]):
            args.append("cfg=cfg")
        else:
            args.append("cfg=8.0")

        # Sampler name - check if it's a parameter
        if any(p in param_mapping and param_mapping[p] == 'sampler_name'
               for p in [x_param, y_param, z_param]):
            args.append("sampler_name=sampler_name")
        else:
            args.append("sampler_name='euler'")

        # Scheduler - check if it's a parameter
        if any(p in param_mapping and param_mapping[p] == 'scheduler'
               for p in [x_param, y_param, z_param]):
            args.append("scheduler=scheduler")
        else:
            args.append("scheduler='normal'")

        # Positive/negative/latent
        args.append("positive=positive")
        args.append("negative=negative")
        args.append("latent_image=latent")
        args.append("denoise=1.0")

        return f"latent = KSampler({', '.join(args)})"

    def _generate_img2img_script(
        self,
        parameter_grid: ParameterGrid,
        workflow_config: WorkflowConfig,
    ) -> str:
        """Generate img2img workflow script."""
        # Simplified version - extend as needed
        return "# img2img workflow - TODO: implement"

    def _generate_hires_fix_script(
        self,
        parameter_grid: ParameterGrid,
        workflow_config: WorkflowConfig,
    ) -> str:
        """Generate hires fix workflow script."""
        # Simplified version - extend as needed
        return "# hires fix workflow - TODO: implement"

    def _format_values(self, values: List[Any]) -> str:
        """Format values list for Python code."""
        if all(isinstance(v, str) for v in values):
            # String values - quote them
            return "[" + ", ".join(f"'{v}'" for v in values) + "]"
        else:
            # Numeric values
            return str(values)

    def generate_workflow_json(
        self,
        parameter_grid: ParameterGrid,
        workflow_config: WorkflowConfig,
    ) -> Dict[str, Any]:
        """
        Generate ComfyUI workflow JSON (API format).

        Note: This is a simplified version. Full implementation would
        execute the script and extract the workflow.
        """
        return {
            "nodes": [],
            "links": [],
            "metadata": {
                "x_param": parameter_grid.x_axis.name,
                "y_param": parameter_grid.y_axis.name,
                "z_param": parameter_grid.z_axis.name,
                "total_combinations": parameter_grid.total_combinations,
            }
        }


# Global instance
_workflow_generator_instance: Optional['WorkflowGenerator'] = None


def get_workflow_generator() -> WorkflowGenerator:
    """Get global workflow generator instance."""
    global _workflow_generator_instance
    if _workflow_generator_instance is None:
        _workflow_generator_instance = WorkflowGenerator()
    return _workflow_generator_instance
