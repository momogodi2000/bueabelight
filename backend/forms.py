from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import ContactMessage, CateringInquiry, Order

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': '+237 6 XX XX XX XX'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Subject of your message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Your message here...',
                'rows': 5
            })
        }

class CateringInquiryForm(forms.ModelForm):
    class Meta:
        model = CateringInquiry
        fields = [
            'name', 'phone', 'email', 'event_type', 'guest_count',
            'preferred_date', 'preferred_time', 'location', 'special_requirements'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': '+237 6 XX XX XX XX',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'your.email@example.com (optional)'
            }),
            'event_type': forms.Select(attrs={
                'class': 'input-field',
                'required': True
            }),
            'guest_count': forms.NumberInput(attrs={
                'class': 'input-field',
                'placeholder': 'Number of guests',
                'min': 10,
                'max': 1000,
                'required': True
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'input-field',
                'type': 'date',
                'required': True
            }),
            'preferred_time': forms.TimeInput(attrs={
                'class': 'input-field',
                'type': 'time',
                'required': True
            }),
            'location': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Enter the complete venue address...',
                'rows': 3,
                'required': True
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Tell us about dietary restrictions, preferred dishes, service style, timing, or any other special requests...',
                'rows': 4
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to 2 days from now (48 hours advance notice)
        from datetime import date, timedelta
        min_date = date.today() + timedelta(days=2)
        self.fields['preferred_date'].widget.attrs['min'] = min_date.strftime('%Y-%m-%d')
        
        # Make required fields more explicit
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True
                if 'placeholder' in field.widget.attrs:
                    field.widget.attrs['placeholder'] += ' *'

class CheckoutForm(forms.ModelForm):
    PAYMENT_METHOD_CHOICES = [
        ('whatsapp_contact', 'Contact via WhatsApp'),
        ('mobile_money', 'Mobile Money (Delivery Fee Only)'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'})
    )
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'customer_location', 'special_instructions', 'payment_method'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': '+237 6 XX XX XX XX',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'your.email@example.com (optional)'
            }),
            'customer_location': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Your delivery address (include landmarks)',
                'rows': 3,
                'required': True
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Any special instructions for your order...',
                'rows': 3
            })
        }

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Password'
        })
    )

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'Enter your email address'
        })
    )

class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'New Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Confirm New Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data