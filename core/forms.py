from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

def styled(field: object, css_class: str): 
    class WrappedField(field):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def widget_attrs(self, widget):
            attrs = super().widget_attrs(widget)
            if not widget.is_hidden:
                attrs["class"] = css_class
            return attrs
        
    return WrappedField

StyledCharField = styled(forms.CharField, "form-control")
StyledSlugField = styled(forms.SlugField, "form-control")


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for field in ['username', 'email', 'password1', 'password2']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    pass

class NewSSHKeyForm(forms.Form):
    name = StyledCharField(max_length=50)
    public_key = StyledCharField(widget=forms.Textarea())
    pass

class NewRepoForm(forms.Form):
    name = StyledCharField(max_length=50)
    description = StyledCharField(widget=forms.Textarea(), required=False)
    slug = StyledSlugField(required=False)
    pass

class NewIssueForm(forms.Form):
    title = StyledCharField(max_length=50)
    description = StyledCharField(widget=forms.Textarea())
    pass

class NewIssueCommentForm(forms.Form):
    text = StyledCharField(widget=forms.Textarea())
    pass