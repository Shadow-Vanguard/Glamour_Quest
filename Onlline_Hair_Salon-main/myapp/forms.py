from django import forms
from .models import Client

class ClientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'dob','gender', 'contact']

    def __init__(self, *args, **kwargs):
        super(ClientProfileUpdateForm, self).__init__(*args, **kwargs)
        # Make the email field read-only
        self.fields['email'].widget.attrs['readonly'] = True

class EmployeeProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'dob', 'contact', ]

    def __init__(self, *args, **kwargs):
        super(EmployeeProfileUpdateForm, self).__init__(*args, **kwargs)
        # Make the email field read-only
        self.fields['email'].widget.attrs['readonly'] = True


from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'description', 'rate', 'image', 'subcategory']

from django import forms
from .models import Booking, Employee
from django.utils import timezone
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    # Generate time slots from 8 AM to 8 PM with "Choose time" as first option
    TIME_CHOICES = [('', 'Choose time')] + [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(8, 21)]
    
    booking_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id':'time'})
    )
    staff = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        empty_label="Choose staff",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control','id':'staff'})
    )

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'staff', 'additional_notes']
        widgets = {
            'booking_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': timezone.now().date().strftime('%d-%m-%Y'),
                    'class': 'form-control',
                    'id': 'dates'
                }
            ),
            'additional_notes': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Any special requests or notes?',
                    'id': 'desc'

                }
            ),
        }

    def __init__(self, *args, **kwargs):
        specialized_employees = kwargs.pop('specialized_employees', None)
        super().__init__(*args, **kwargs)
        
        if specialized_employees:
            self.fields['staff'].queryset = specialized_employees
        
        self.fields['booking_date'].label = "Select Date"
        self.fields['booking_time'].label = "Select Time"
        self.fields['staff'].label = "Select Staff"
        self.fields['additional_notes'].label = "Additional Notes"
        
        self.fields['staff'].label_from_instance = self.label_from_instance
        self.fields['booking_time'].widget.attrs.update({'class': 'form-control'})

    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')
        staff = cleaned_data.get('staff')

        if booking_date and booking_time:
            # Check if booking is in the past
            now = timezone.now()
            booking_datetime = datetime.combine(booking_date, datetime.strptime(booking_time, '%H:%M').time())
            booking_datetime = timezone.make_aware(booking_datetime)

            if booking_datetime <= now:
                raise forms.ValidationError("Cannot book appointments in the past.")

            # Check if the selected time slot is available
            if staff:
                existing_bookings = Booking.objects.filter(
                    staff=staff,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    status__in=['Pending', 'Confirmed']
                )
                if existing_bookings.exists():
                    raise forms.ValidationError(
                        "This time slot is already booked for the selected employee. Please choose another time or employee."
                    )

        return cleaned_data

from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'id':'rating'}),
            'comment': forms.Textarea(attrs={'rows': 4,'id':'comment'}),
        }
