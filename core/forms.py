from django import forms
from .models import Resident, Project, KKProfile, SKMember
from datetime import date

# -------------------------
# RESIDENT FORM
# -------------------------
class ResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = [
            'firstname',
            'lastname',
            'birthday',
            'gender',
            'civil_status',
            'purok',
            'zone',
            'contact_number',
            'email',
            'occupation',
            'address',
        ]

        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------------
# PROJECT FORM
# -------------------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'date_started',
            'status',
            'budget',
        ]

        widgets = {
            'date_started': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------------
# KK PROFILING FORM (USER SIDE)
# -------------------------
class KKProfileForm(forms.ModelForm):
    # --- Resident fields ---
    firstname = forms.CharField(label="First Name")
    lastname = forms.CharField(label="Last Name")
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    purok = forms.CharField(label="Purok")

    # Read-only age
    age = forms.IntegerField(
        required=False,
        disabled=True,
        label="Age"
    )

    class Meta:
        model = KKProfile
        fields = [
            'school_status',
            'email',
        ]

    def __init__(self, *args, **kwargs):
        resident = kwargs.pop('resident', None)
        super().__init__(*args, **kwargs)

        if resident:
            self.fields['firstname'].initial = resident.firstname
            self.fields['lastname'].initial = resident.lastname
            self.fields['birthday'].initial = resident.birthday
            self.fields['purok'].initial = resident.purok

            if resident.birthday:
                today = date.today()
                self.fields['age'].initial = (
                    today.year - resident.birthday.year -
                    ((today.month, today.day) <
                     (resident.birthday.month, resident.birthday.day))
                )

    def save(self, commit=True):
        kk_profile = super().save(commit=False)

        # Create or update Resident
        resident = getattr(kk_profile, 'resident', None)
        if not resident:
            resident = Resident()

        resident.firstname = self.cleaned_data['firstname']
        resident.lastname = self.cleaned_data['lastname']
        resident.birthday = self.cleaned_data['birthday']
        resident.purok = self.cleaned_data['purok']

        if commit:
            resident.save()
            kk_profile.resident = resident
            kk_profile.save()

        return kk_profile

# -------------------------
# SK MEMBER FORM
# -------------------------
class SKMemberForm(forms.ModelForm):
    class Meta:
        model = SKMember
        fields = [
            'name',
            'role',
            'photo',
            'order',
        ]
