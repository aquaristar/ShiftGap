from rest_framework import serializers

from .models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='user')
    start = serializers.DateTimeField(source='start_time')
    end = serializers.DateTimeField(source='end_time')

    class Meta:
        model = Shift


    def to_representation(self, instance):
        instance.start_time = instance.start_time.astimezone(self.context['request'].user.userprofile.timezone)
        instance.end_time = instance.end_time.astimezone(self.context['request'].user.userprofile.timezone)
        return super(ShiftSerializer, self).to_representation(instance=instance)

    def to_internal_value(self, data):
        # FIXME reset organization to users matching org in case bad data was passed in
        return super(ShiftSerializer, self).to_internal_value(data=data)