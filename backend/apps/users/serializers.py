from django.template.loader import render_to_string
from django.contrib.auth import get_user_model


from rest_framework import serializers


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    specialities = serializers.SerializerMethodField()
    absent = serializers.IntegerField()
    absent_display = serializers.SerializerMethodField()
    cases_finished_num = serializers.SerializerMethodField()
    cases_current_num = serializers.SerializerMethodField()

    def get_specialities(self, user):
        return ', '.join([speciality.title for speciality in user.specialities.all()])

    def get_at_work(self, user):
        return 'Так' if user.at_work else 'Ні'

    def get_absent_display(self, user):
        return render_to_string(
            'users/list/_partials/user_absent.html',
            {
                'user': user,
                'request': self.context['request']
            }
        )

    def get_cases_finished_num(self, user):
        return render_to_string(
            'users/list/_partials/cases_finished_link.html',
            {
                'user': user,
                'request': self.context['request']
            }
        )

    def get_cases_current_num(self, user):
        return render_to_string(
            'users/list/_partials/cases_current_link.html',
            {
                'user': user,
                'request': self.context['request']
            }
        )

    class Meta:
        model = UserModel
        fields = [
            'last_name',
            'first_name',
            'middle_name',
            'position',
            'specialities',
            'cases_finished_num',
            'cases_current_num',
            'absent',
            'absent_display',
        ]
