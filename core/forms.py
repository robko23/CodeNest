from django import forms

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

class NewSSHKeyForm(forms.Form):
    name = StyledCharField(max_length=50)
    public_key = StyledCharField(widget=forms.Textarea())
    pass

class NewRepoForm(forms.Form):
    name = StyledCharField(max_length=50)
    description = StyledCharField(widget=forms.Textarea(), required=False)
    slug = StyledSlugField(required=False)

    pass
