from django.template.loader import render_to_string
from django.contrib.auth import get_user_model


from rest_framework import serializers


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    user_fullname = serializers.ReadOnlyField(source='get_full_name')
    user_fullname_sort = serializers.ReadOnlyField()
    specialities = serializers.SerializerMethodField()
    present = serializers.IntegerField()
    at_work = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    def get_specialities(self, user):
        return ', '.join([speciality.title for speciality in user.specialities.all()])

    def get_at_work(self, user):
        return 'Так' if user.at_work else 'Ні'

    def get_actions(self, user):
        return '123'

    class Meta:
        model = UserModel
        fields = [
            'user_fullname',
            'user_fullname_sort',
            'position',
            'specialities',
            'present',
            'at_work',
            'actions',
        ]
