from django import forms


class NewSSHKeyForm(forms.Form):
    name = forms.CharField(max_length=50)
    public_key = forms.CharField(widget=forms.Textarea())
    pass


class NewRepoForm(forms.Form):
    name = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea())
    slug = forms.SlugField()
    pass
