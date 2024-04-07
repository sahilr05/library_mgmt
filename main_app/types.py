import enum
from typing import List
from typing import Tuple


class StateEnumMeta(enum.EnumMeta):
    """Metaclass for enums that allows checking if a value is a valid member."""

    def __contains__(self, item):
        try:
            self(item)
        except ValueError:
            return False
        else:
            return True


class BaseState(enum.Enum, metaclass=StateEnumMeta):
    """Base class for enums with metaclass StateEnumMeta."""

    pass


class CirculationStatus(str, BaseState):
    """Enum for circulation status."""

    CHECKOUT = "CHECKOUT"
    RETURN = "RETURN"


class ReservationStatus(str, BaseState):
    """Enum for reservation status."""

    RESERVED = "RESERVED"
    FULFILLED = "FULFILLED"


def states_as_list(state_type: BaseState) -> List[Tuple[str, str]]:
    """Return a list of (value, name) tuples for the given enum type."""
    return list(map(lambda c: (c.value, c.name), state_type))


def states_as_values(state_type: BaseState) -> List[str]:
    """Return a list of values for the given enum type."""
    return list(map(lambda c: c.value, state_type))
