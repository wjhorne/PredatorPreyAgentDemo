"""
Plain-language query parser for the simulation pipeline.

Extracts intent, species, timestep, and parameter overrides from user queries.
"""
import re
from typing import Optional, Dict, Any


class QueryParser:
    """Parse plain-language queries into structured parameters."""

    def __init__(self):
        """Initialize the parser with keyword mappings."""
        self.species_keywords = {
            "rabbit": "rabbit",
            "rabbits": "rabbit",
            "bunny": "rabbit",
            "bunnies": "rabbit",
            "hare": "rabbit",
            "prey": "rabbit",
            "fox": "fox",
            "foxes": "fox",
            "predator": "fox",
            "carnivore": "fox",
        }

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a plain-language query into structured parameters.

        Args:
            query: User-provided query string

        Returns:
            Dict with keys:
            - intent: "population" or "analysis"
            - species: "rabbit", "fox", or "both"
            - timestep: int or None
            - params: dict of parameter overrides

        Raises:
            ValueError: If query is malformed or ambiguous
        """
        query_lower = query.lower().strip()

        # Determine intent
        intent = self._extract_intent(query_lower)

        # Determine species
        species = self._extract_species(query_lower)

        # Extract timestep if present
        timestep = self._extract_timestep(query_lower)

        # Extract parameter overrides
        params = self._extract_parameters(query_lower)

        return {
            "intent": intent,
            "species": species,
            "timestep": timestep,
            "params": params,
        }

    def _extract_intent(self, query: str) -> str:
        """Determine whether the user wants a population value or analysis report."""
        if any(
            keyword in query
            for keyword in ["report", "generate", "create", "show", "plot", "analysis", "pdf"]
        ):
            return "analysis"
        elif any(
            keyword in query
            for keyword in ["how many", "what", "population", "count", "at step", "at time"]
        ):
            return "population"
        else:
            # Default to population query
            return "population"

    def _extract_species(self, query: str) -> str:
        """Extract the target species (rabbit, fox, or both)."""
        has_rabbit = any(kw in query for kw in ["rabbit", "prey", "bunny", "hare"])
        has_fox = any(kw in query for kw in ["fox", "predator", "carnivore"])

        if has_rabbit and has_fox:
            return "both"
        elif has_rabbit:
            return "rabbit"
        elif has_fox:
            return "fox"
        else:
            # Default to both
            return "both"

    def _extract_timestep(self, query: str) -> Optional[int]:
        """Extract the timestep if specified."""
        # Match patterns like "step 50", "at step 100", "timestep 200", "time step 50", etc.
        patterns = [
            r"(?:at\s+)?(?:step|timestep|time\s+step|time\s*-?\s*step|t=)\s*(\d+)",
            r"after\s+(\d+)\s+(?:steps|steps?|time steps?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))

        return None

    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """Extract parameter overrides like nx=40, nt=200, seed=999."""
        params = {}

        # Match patterns like "nx=50", "nt: 200", "seed = 999", etc.
        # Also support human-readable forms like "50x50 grid", "200 steps", etc.

        # Explicit key=value patterns with multiple options per key
        patterns = {
            "nx": [r"nx\s*[:=]\s*(\d+)"],
            "ny": [r"ny\s*[:=]\s*(\d+)"],
            "grid": [r"(\d+)\s*x\s*(\d+)\s*grid"],
            "nt": [
                r"(?:nt|steps|time\s+steps)\s*[:=]\s*(\d+)",
                r"(?:for|Simulate\s+for)?\s*(\d+)\s+(?:steps|time\s+steps?)",
            ],
            "seed": [
                r"seed\s*[:=]\s*(\d+)",
                r"(?:seed|with\s+seed)\s+(\d+)",
            ],
            "rabbit_growth": [r"rabbit[_\s]*growth\s*[:=]\s*([0-9.]+)"],
            "carrying_capacity": [r"carrying[_\s]*capacity\s*[:=]\s*([0-9.]+)"],
            "predation_rate": [r"predation[_\s]*rate\s*[:=]\s*([0-9.]+)"],
            "fox_growth": [r"fox[_\s]*growth\s*[:=]\s*([0-9.]+)"],
            "fox_mortality": [r"fox[_\s]*mortality\s*[:=]\s*([0-9.]+)"],
            "rabbit_diffusion": [r"rabbit[_\s]*diffusion\s*[:=]\s*([0-9.]+)"],
            "fox_diffusion": [r"fox[_\s]*diffusion\s*[:=]\s*([0-9.]+)"],
        }

        for key, patterns_list in patterns.items():
            # patterns_list is always a list of patterns
            for pattern in patterns_list:
                match = re.search(pattern, query)
                if match:
                    if key == "grid":
                        # Special case: "50x50 grid" -> nx=50, ny=50
                        params["nx"] = int(match.group(1))
                        params["ny"] = int(match.group(2))
                    elif key in ("nx", "ny", "nt", "seed", "init_patch_size"):
                        params[key] = int(match.group(1))
                    else:
                        # Float parameters
                        params[key] = float(match.group(1))
                    break  # Found a match, stop trying other patterns for this key

        return params
