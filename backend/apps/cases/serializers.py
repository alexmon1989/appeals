from django.template.loader import render_to_string

from rest_framework import serializers
from .models import Document, Sign, Case
from ..classifiers.models import DocumentType, ClaimKind, ObjKind
from ..filling.models import Claim


class ClaimKindSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClaimKind
        fields = (
            'id',
            'title',
        )


class ObjKindSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ObjKind
        fields = (
            'id',
            'title',
        )


class ClaimSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    obj_kind = ObjKindSerializer()
    claim_kind = ClaimKindSerializer()
    submission_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')

    class Meta:
        model = Claim
        fields = (
            'id',
            'obj_kind',
            'claim_kind',
            'obj_number',
            'obj_title',
            'third_person',
            'submission_date',
        )


class DocumentTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentType
        fields = (
            'id',
            'title',
        )


class SignTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Sign
        fields = (
            'id',
            'subject',
            'serial_number',
            'issuer',
            'timestamp',
        )


class DocumentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    document_type = DocumentTypeSerializer()
    document_type_title = serializers.ReadOnlyField(source='document_type.title')
    registration_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    output_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    input_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    signs_count = serializers.ReadOnlyField()
    signs_info = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    def get_signs_info(self, document: Document):
        return render_to_string(
            'cases/_partials/document_signs_info.html',
            {
                'document': document
            }
        )

    def get_actions(self, document: Document):
        return render_to_string(
            'cases/_partials/actions.html',
            {
                'document': document,
                'request': self.context['request']
            }
        )

    class Meta:
        model = Document
        fields = (
            'id',
            'document_type_title',
            'registration_number',
            'registration_date',
            'output_date',
            'input_date',
            'signs_count',
            'signs_info',
            'actions',

            'document_type',
        )


class CaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    case_number_link = serializers.SerializerMethodField()
    claim = ClaimSerializer()
    stage_verbal = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = (
            'id',
            'case_number',
            'case_number_link',
            'claim',
            'stage_verbal',
        )

    def get_case_number_link(self, case: Case):
        return render_to_string(
            'cases/_partials/case_number_link.html',
            {
                'case': case
            }
        )

    def get_stage_verbal(self, case: Case):
        return render_to_string(
            'cases/_partials/case_stage.html',
            {
                'case': case
            }
        )
