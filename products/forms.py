from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class ProductUrlForm(forms.Form):
    """
    Form for adding a product by URL
    """
    url = forms.URLField(
        label='Product URL',
        validators=[URLValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter product URL'
        })
    )

    def clean_url(self):
        """
        Additional URL validation
        """
        url = self.cleaned_data['url']
        
        # Add any specific URL validation for your parsing site
        if 'tweakers.net/pricewatch' not in url:
            raise ValidationError('Please enter a valid Tweakers.net product URL')
        
        return url