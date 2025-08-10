from django import forms
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Publication, PublicationAuthor, PublicationMetrics, PublicationType

class PublicationAdminForm(forms.ModelForm):
    """Enhanced admin form for Publication model"""
    
    class Meta:
        model = Publication
        fields = '__all__'
        widgets = {
            'abstract': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'keywords': forms.TextInput(attrs={'size': 80}),
            'submitted_at': widgets.AdminDateWidget(),
            'published_at': widgets.AdminDateWidget(),
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }

class BulkActionForm(forms.Form):
    """Form for bulk actions on publications"""
    action = forms.ChoiceField(choices=[
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected'),
        ('delete', 'Delete Selected'),
    ])
    publications = forms.ModelMultipleChoiceField(
        queryset=Publication.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

class PublicationSearchForm(forms.Form):
    """Form for advanced publication search"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in title, abstract, keywords...'
        })
    )
    
    publication_type = forms.MultipleChoiceField(
        choices=PublicationType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    status = forms.MultipleChoiceField(
        choices=[
            ('draft', 'Draft'),
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('published', 'Published'),
            ('rejected', 'Rejected'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    research_area = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Research area'
        })
    )

class PublicationFilterForm(forms.Form):
    """Form for filtering publications in list views"""
    
    status = forms.ChoiceField(
        choices=[('', 'All')] + [
            ('draft', 'Draft'),
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('published', 'Published'),
            ('rejected', 'Rejected'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    publication_type = forms.ChoiceField(
        choices=[('', 'All')] + list(PublicationType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_featured = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Featured'), ('false', 'Not Featured')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )



class PublicationMetricsForm(forms.Form):
    """Form for updating publication metrics"""
    
    citation_count = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Citation count'
        })
    )
    
    altmetric_score = forms.FloatField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Altmetric score'
        })
    )
    
    twitter_mentions = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Twitter mentions'
        })
    )
    
    facebook_shares = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Facebook shares'
        })
    )
    
    linkedin_shares = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'LinkedIn shares'
        })
    )
    
    mendeley_readers = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mendeley readers'
        })
    )
    
    researchgate_reads = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'ResearchGate reads'
        })
    )

    def clean(self):
        """Validate that at least one field is provided"""
        cleaned_data = super().clean()
        
        # Check if at least one metric is provided
        metrics_fields = [
            'citation_count', 'altmetric_score', 'twitter_mentions',
            'facebook_shares', 'linkedin_shares', 'mendeley_readers',
            'researchgate_reads'
        ]
        
        if not any(cleaned_data.get(field) is not None for field in metrics_fields):
            raise ValidationError('At least one metric must be provided')
        
        return cleaned_data