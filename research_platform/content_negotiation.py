"""
Custom content negotiation for Django REST Framework
"""

from rest_framework.content_negotiation import DefaultContentNegotiation
from rest_framework.renderers import JSONRenderer


class FlexibleContentNegotiation(DefaultContentNegotiation):
    """
    Custom content negotiation that falls back to JSON when Accept header
    cannot be satisfied by available renderers.
    
    This fixes the "Could not satisfy the request Accept header" error
    that occurs when clients send Accept headers that don't match available renderers.
    """
    
    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select the most appropriate renderer for the request.
        Falls back to JSON if no suitable renderer is found.
        """
        try:
            # Try the default content negotiation first
            return super().select_renderer(request, renderers, format_suffix)
        except Exception:
            # If default negotiation fails, fall back to JSON renderer
            json_renderer = None
            
            # Find JSON renderer in available renderers
            for renderer in renderers:
                if isinstance(renderer, JSONRenderer):
                    json_renderer = renderer
                    break
            
            # If no JSON renderer found, use the first available renderer
            if json_renderer is None and renderers:
                json_renderer = renderers[0]
            
            # Return the fallback renderer with JSON media type
            if json_renderer:
                return (json_renderer, 'application/json')
            
            # If all else fails, raise the original exception
            return super().select_renderer(request, renderers, format_suffix)
