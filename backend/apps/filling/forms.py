from django import forms
from .models import ClaimField
from ..classifiers.models import ClaimKind


class ClaimKindField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.title} ({obj.obj_kind.title})"


class ClaimFieldForm(forms.ModelForm):
    claim_kind = ClaimKindField(
        queryset=ClaimKind.objects.order_by('obj_kind_id').select_related('obj_kind'),
        label='Тип звернення'
    )

    class Meta:
        model = ClaimField
        fields = '__all__'
