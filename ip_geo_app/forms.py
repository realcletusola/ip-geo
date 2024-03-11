from django import forms 

# ip form 
class IpForm(forms.Form):
    ip_address = forms.CharField(required=True)

