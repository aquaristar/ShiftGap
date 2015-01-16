from rest_framework import serializers

from .models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='user')
    start = serializers.DateTimeField(source='start_time')
    end = serializers.DateTimeField(source='end_time')

    class Meta:
        model = Shift
        read_only_fields = ('organization',)

    def to_representation(self, instance):
        # always convert to users timezone when displaying shifts
        instance.start_time = instance.start_time.astimezone(self.context['request'].user.userprofile.timezone)
        instance.end_time = instance.end_time.astimezone(self.context['request'].user.userprofile.timezone)
        return super(ShiftSerializer, self).to_representation(instance=instance)

    def to_internal_value(self, data):
        # FIXME reset organization to users matching org in case bad data was passed in
        return super(ShiftSerializer, self).to_internal_value(data=data)

    # def create(self, validated_data):
    #     return super(ShiftSerializer, self).create(validated_data)


#     convert to users local timezone when serializing
# convert to utc when deserializing
# access request from serializer? context[‘request’] - when is it available?
#
# get params should be in users local time
#
# org should be implicit when posting to api