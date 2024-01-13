from rest_framework import serializers

class VideoDataSerializer(serializers.Serializer):
    video_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    uploadDate = serializers.CharField(max_length=100)
    summary = serializers.CharField(max_length=1000)
    ratio = serializers.FloatField()
    url = serializers.CharField(max_length=200)
