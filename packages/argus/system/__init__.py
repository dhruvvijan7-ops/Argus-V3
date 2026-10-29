"""Host introspection: operating system, privileges, interfaces and capabilities.

Everything platform-specific that the rest of Argus needs to *know* about lives
here, so detection, scoring and response stay free of ``sys.platform`` checks.
"""

from argus.system.environment import HostEnvironment, detect_environment
from argus.system.interfaces import cached_local_addresses, list_interfaces, local_addresses
from argus.system.privileges import (
    PrivilegeCheck,
    capture_privilege,
    firewall_privilege,
    is_elevated,
)

__all__ = [
    "HostEnvironment",
    "PrivilegeCheck",
    "cached_local_addresses",
    "capture_privilege",
    "detect_environment",
    "firewall_privilege",
    "is_elevated",
    "list_interfaces",
    "local_addresses",
]
