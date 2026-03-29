from rest_framework import serializers

class CNRLookupSerializer(serializers.Serializer):
    cnr_number = serializers.CharField(min_length=16, max_length=16)

    def validate_crn_number(self, value):
        value = value.strip().upper()
        if not value.isalnum():
            raise serializers.ValidationError("CNR number must be alphanumeric without spaces or dashes.")
        if len(value) != 16:
            raise serializers.ValidationError("CNR number must be exactly 16 characters long.")
        return value