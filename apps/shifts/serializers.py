from rest_framework import serializers

from .models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='user', read_only=True)
    start = serializers.DateTimeField(source='start_time', read_only=True)
    end = serializers.DateTimeField(source='end_time', read_only=True)

    class Meta:
        model = Shift
        read_only_fields = ('organization', 'title', 'start', 'end',)

    def to_representation(self, instance):
        # always convert to users timezone when displaying shifts
        instance.start_time = instance.start_time.astimezone(self.context['request'].user.userprofile.timezone)
        instance.end_time = instance.end_time.astimezone(self.context['request'].user.userprofile.timezone)
        return super(ShiftSerializer, self).to_representation(instance=instance)

    def create(self, validated_data):
        # organization is always inferred from user data - never set externally
        validated_data['organization'] = self.context['request'].user.userprofile.organization

        # timezones in validated_data are presented in UTC, even though they are really in the users
        # local timezone - this is a messy way to strip out the tz data and re-localize it based on the
        # users timezone in their profile. It should probably be reviewed and fixed
        import datetime
        start = datetime.datetime(*validated_data['start_time'].timetuple()[:6])
        start = self.context['request'].user.userprofile.timezone.localize(start)
        end = datetime.datetime(*validated_data['end_time'].timetuple()[:6])
        end = self.context['request'].user.userprofile.timezone.localize(end)

        validated_data['start_time'] = start
        validated_data['end_time'] = end

        return super(ShiftSerializer, self).create(validated_data)