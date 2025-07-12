"""
DEPRECATED: Legacy Import Wrapper for CustomerSectionV2

This file exists only for backward compatibility. The actual CustomerSectionV2
implementation has been moved to welcome_screen_components/customer_section_v2.py.

Please update your imports to:
    from welcome_screen_components.customer_section_v2 import CustomerSectionV2

This wrapper will be removed in a future version.
"""

import warnings
from welcome_screen_components.customer_section_v2 import CustomerSectionV2

# Issue deprecation warning
warnings.warn(
    "customer_section_v2.py in root directory is deprecated. "
    "Please import from welcome_screen_components.customer_section_v2 instead.",
    DeprecationWarning,
    stacklevel=2
)

# Export for backward compatibility
__all__ = ['CustomerSectionV2']
