"""
Views for GTFS Chat Django application.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings


def index(request):
    """Landing page with information about the application."""
    context = {
        'title': 'GTFS Chat - Swedish Public Transit Query Interface',
        'description': 'Ask questions about Swedish public transit data in natural language',
    }
    return render(request, 'index.html', context)


def chat(request):
    """Main chat interface with Vanna web component."""
    context = {
        'vanna_server_url': settings.VANNA_SERVER_URL,
        'sse_endpoint': settings.VANNA_SSE_ENDPOINT,
        'ws_endpoint': settings.VANNA_WS_ENDPOINT,
        'poll_endpoint': settings.VANNA_POLL_ENDPOINT,
    }
    return render(request, 'chat.html', context)


def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'GTFS Chat Django',
        'vanna_server': settings.VANNA_SERVER_URL
    })
