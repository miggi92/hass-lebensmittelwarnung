"""Einzelne Sensoren für die jüngste Meldung, je Feld eine eigene Datei."""

from __future__ import annotations

from .affected_states import LmwAffectedStatesSensor
from .batch import LmwBatchSensor
from .count import LmwCountSensor
from .expiry import LmwExpirySensor
from .last_success import LmwLastSuccessSensor
from .latest import LmwLatestSensor
from .manufacturer import LmwManufacturerSensor
from .package import LmwPackageSensor
from .previous import LmwPreviousSensor
from .product import LmwProductSensor
from .published import LmwPublishedSensor
from .reason import LmwReasonSensor
from .recent_count import LmwRecentCountSensor

SENSOR_CLASSES = (
    LmwLatestSensor,
    LmwPreviousSensor,
    LmwReasonSensor,
    LmwBatchSensor,
    LmwExpirySensor,
    LmwProductSensor,
    LmwPackageSensor,
    LmwManufacturerSensor,
    LmwAffectedStatesSensor,
    LmwPublishedSensor,
    LmwCountSensor,
    LmwRecentCountSensor,
    LmwLastSuccessSensor,
)
