"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Choreography -> "choreography" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Marker(BaseModel):
    """A point in time in the music with an optional label and 8-count."""
    time: float = Field(..., ge=0, description="Time in seconds from start of audio")
    label: Optional[str] = Field(None, description="Short name, e.g., 'Verse A', 'Kick' ")
    count: Optional[int] = Field(None, ge=1, le=64, description="Optional 8-count number or beats")

class Choreography(BaseModel):
    """Choreography document schema (collection name: choreography)"""
    title: str = Field(..., description="Name of the choreography")
    audio_url: Optional[str] = Field(None, description="Public URL to audio file (mp3/m4a/ogg)")
    bpm: Optional[float] = Field(None, ge=30, le=300, description="Beats per minute of the track")
    markers: List[Marker] = Field(default_factory=list, description="Timeline markers")
