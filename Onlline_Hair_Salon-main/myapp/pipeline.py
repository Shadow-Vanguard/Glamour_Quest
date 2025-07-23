from django.shortcuts import redirect
from .models import Client

def custom_pipeline(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        if not Client.objects.filter(email=user.email).exists():
            # Create a new Client object if it doesn't exist
            Client.objects.create(
                email=user.email,
                first_name=response.get('given_name', ''),
                last_name=response.get('family_name', ''),
                # Add other fields as necessary
            )
        
        # Set session variables
        kwargs['request'].session['user_id'] = user.id
        kwargs['request'].session['user_type'] = 'client'
        
        # Redirect to client dashboard
        return redirect('client_dashboard')