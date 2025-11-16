"""
Service for extracting and managing ComfyScript enums.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EnumService:
    """Service for accessing ComfyScript enums."""

    def __init__(self):
        """Initialize enum service."""
        self._enums_cache: Optional[Dict[str, List[str]]] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize ComfyScript and load enums."""
        if self._initialized:
            return

        try:
            logger.info("Initializing ComfyScript runtime...")

            # Import ComfyScript runtime
            from comfy_script.runtime import load

            # Load ComfyScript (connects to ComfyUI)
            load()

            # Import nodes to get enums
            from comfy_script.runtime import nodes

            logger.info("ComfyScript runtime initialized successfully")

            # Cache enums
            self._enums_cache = self._extract_enums(nodes)
            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize ComfyScript: {e}")
            raise RuntimeError(f"Failed to initialize ComfyScript: {e}")

    def _extract_enums(self, nodes_module) -> Dict[str, List[str]]:
        """Extract all enums from nodes module."""
        enums = {}

        # Extract global enums
        for attr_name in dir(nodes_module):
            attr = getattr(nodes_module, attr_name)

            # Check if it's an enum class
            if isinstance(attr, type) and issubclass(attr, Enum):
                try:
                    # Get enum values
                    values = [item.value if hasattr(item, 'value') else str(item) for item in attr]
                    if values:
                        enums[attr_name] = values
                        logger.debug(f"Found enum {attr_name} with {len(values)} values")
                except Exception as e:
                    logger.warning(f"Failed to extract values from {attr_name}: {e}")

        # Extract node-specific enums
        # Check KSampler for sampler_name and scheduler
        try:
            if hasattr(nodes_module, 'KSampler'):
                ksampler = nodes_module.KSampler

                # Check for sampler_name enum
                if hasattr(ksampler, 'sampler_name'):
                    sampler_enum = ksampler.sampler_name
                    if hasattr(sampler_enum, '__members__'):
                        enums['Samplers'] = list(sampler_enum.__members__.keys())
                        logger.debug(f"Found Samplers enum with {len(enums['Samplers'])} values")

                # Check for scheduler enum
                if hasattr(ksampler, 'scheduler'):
                    scheduler_enum = ksampler.scheduler
                    if hasattr(scheduler_enum, '__members__'):
                        enums['Schedulers'] = list(scheduler_enum.__members__.keys())
                        logger.debug(f"Found Schedulers enum with {len(enums['Schedulers'])} values")

        except Exception as e:
            logger.warning(f"Failed to extract KSampler enums: {e}")

        return enums

    async def get_samplers(self) -> List[str]:
        """Get available sampler names."""
        if not self._initialized:
            await self.initialize()

        return self._enums_cache.get('Samplers', [])

    async def get_schedulers(self) -> List[str]:
        """Get available scheduler names."""
        if not self._initialized:
            await self.initialize()

        return self._enums_cache.get('Schedulers', [])

    async def get_checkpoints(self) -> List[str]:
        """Get available checkpoint names."""
        if not self._initialized:
            await self.initialize()

        return self._enums_cache.get('Checkpoints', [])

    async def get_vaes(self) -> List[str]:
        """Get available VAE names."""
        if not self._initialized:
            await self.initialize()

        return self._enums_cache.get('VAEs', [])

    async def get_loras(self) -> List[str]:
        """Get available LoRA names."""
        if not self._initialized:
            await self.initialize()

        return self._enums_cache.get('Loras', [])

    async def get_upscale_models(self) -> List[str]:
        """Get available upscale model names."""
        if not self._initialized:
            await self.initialize()

        return self._enums_cache.get('UpscaleModels', [])

    async def get_all_enums(self) -> Dict[str, List[str]]:
        """Get all available enums."""
        if not self._initialized:
            await self.initialize()

        return {
            "samplers": await self.get_samplers(),
            "schedulers": await self.get_schedulers(),
            "checkpoints": await self.get_checkpoints(),
            "vaes": await self.get_vaes(),
            "loras": await self.get_loras(),
            "upscale_models": await self.get_upscale_models(),
        }

    async def get_enum_values(self, enum_name: str) -> List[str]:
        """Get values for a specific enum."""
        if not self._initialized:
            await self.initialize()

        # Try direct lookup
        if enum_name in self._enums_cache:
            return self._enums_cache[enum_name]

        # Try case-insensitive lookup
        for key, values in self._enums_cache.items():
            if key.lower() == enum_name.lower():
                return values

        logger.warning(f"Enum '{enum_name}' not found")
        return []


# Global instance
_enum_service_instance: Optional[EnumService] = None


def get_enum_service() -> EnumService:
    """Get global enum service instance."""
    global _enum_service_instance
    if _enum_service_instance is None:
        _enum_service_instance = EnumService()
    return _enum_service_instance
