from rest_framework import serializers

class ConsultaSerializer(serializers.Serializer):
    codigo = serializers.CharField(required=True)
    data_nascimento = serializers.DateField(required=True, input_formats=['%Y-%m-%d'])  