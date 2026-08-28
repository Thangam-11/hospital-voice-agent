from dataclasses import dataclass
from src.database.policy_chunk import PolicyChunk


@dataclass
class RetrievedChunk:
    chunk: PolicyChunk
    distance: float

    @property
    def score(self) -> float:
        """
        Convert cosine distance into a simple similarity score.

        Smaller cosine distance means more similar.
        """
        return 1.0 - self.distance