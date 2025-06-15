# listings/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.utils import timezone
from .models import User, Property, Booking, Review, Payment, Message, Notification
from .serializers import (
    PropertySerializer, PropertyListSerializer, BookingSerializer, 
    BookingListSerializer, ReviewSerializer, UserSerializer, 
    PaymentSerializer, MessageSerializer, NotificationSerializer
)
from .permissions import IsOwnerOrReadOnly, IsBookingOwnerOrPropertyHost


class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing property listings.
    
    Provides CRUD operations for properties with additional features:
    - Search by name, description, location
    - Filter by property type, price range, availability
    - Order by price, created date, rating
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields
    search_fields = ['name', 'description', 'location']
    
    # Filter fields
    filterset_fields = {
        'property_type': ['exact'],
        'price_per_night': ['gte', 'lte'],
        'max_guests': ['gte'],
        'bedrooms': ['gte'],
        'bathrooms': ['gte'],
        'is_available': ['exact'],
        'location': ['icontains'],
    }
    
    # Ordering fields
    ordering_fields = ['price_per_night', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer
    
    def get_queryset(self):
        queryset = Property.objects.select_related('host').prefetch_related('reviews', 'images')
        
        # Additional custom filters
        min_price = self.request.query_params
