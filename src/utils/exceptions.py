class ServiceError(Exception):
    """Base class for all service-layer errors."""


class PatientNotFoundError(ServiceError):
    """Raised when identity verification doesn't match any patient record."""


class SlotNotFoundError(ServiceError):
    """Raised when a referenced appointment slot doesn't exist."""


class SlotUnavailableError(ServiceError):
    """Raised when a slot exists but is already booked (race condition or
    stale data — e.g. two callers requesting the same slot at once)."""


class AppointmentNotFoundError(ServiceError):
    """Raised when a referenced appointment doesn't exist."""


class InvalidAppointmentStateError(ServiceError):
    """Raised when an action is attempted on an appointment in a state that
    doesn't allow it (e.g. cancelling an already-completed appointment)."""