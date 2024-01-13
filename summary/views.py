# import json
import re
# from django.http import HttpResponse, JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
from .Summarization import Summarizer  # 같은 디렉토리의 Summarization.py에서 Summarizer 클래스를 import
from .Classifier import EmotionClassifier
import requests
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import VideoDataSerializer

# spring에서 post 요청을 받아서 다시 post로 쏴주는 함수

# def get_youtube_data(request):
#     try:
#         # 요청 본문에서 JSON 데이터 파싱
#         data = json.loads(request.body)
#         video_ids = data.get('video_ids', [])
#
#         # 각 비디오 ID에 대한 처리
#         results = []
#         for video_id in video_ids:
#             result = process_video(video_id)  # process_video는 비디오 처리 로직을 구현한 함수
#             results.append(result)
#
#         spring_url = 'http://spring-server-url/api/endpoint'
#         response = requests.post(spring_url, json=results)
#
#         if response.status_code == 200:
#             return HttpResponse("Data successfully sent to Spring", status=200)
#         else:
#             return JsonResponse({'error': 'Failed to send data to Spring'}, status=500)
#
#     except TranscriptsDisabled:
#         return JsonResponse({'error': 'Transcripts are disabled for this video'}, status=400)
#
#     except NoTranscriptFound:
#         return JsonResponse({'error': 'No transcript found for this video'}, status=404)
#
#     except Exception as e:
#         return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)

#데이터 가공 함수

class YouTubeDataAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            # JSON 구조에 맞춰 video_ids를 추출합니다.
            video_ids = [item['id'] for item in data]  # 여기를 수정합니다.

            results = [process_video(video_id) for video_id in video_ids]
            print("여기 왔어요")
            print(results)

            # 데이터를 serializer로 변환
            serializer = VideoDataSerializer(data=results, many=True)
            if serializer.is_valid():
                # React로 데이터 전송
                react_url = 'https://dda8-219-255-207-98.ngrok-free.app/api/video-result'
                #react_url = 'http://127.0.0.1:8080/api/video-result'
                response = requests.post(react_url, json=serializer.validated_data)
                if response.status_code == 200:
                    return Response({"message": "Data successfully sent to react"})
                else:
                    return Response({"error": "Failed to send data to react"}, status=500)
            else:
                return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

def process_video(video_id):
    # Summarizer 인스턴스 생성
    summarizer = Summarizer()

    # YouTube Transcript API 호출
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        paragraph = ' '.join([re.sub(r'[^\w\s]', '', item['text']) for item in transcript_list])
        summaries = summarizer.summarize([paragraph])
    except:
        summaries = ['요약 할 수 없어요.']

    # YouTube Data API 호출
    api_key = 'AIzaSyDtTwu1u- S-WhZL5EWAq1GAPnjIGGjaQoo'
    youtube = build('youtube', 'v3', developerKey=api_key)

    # 댓글 가져오기
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100
    ).execute()
    comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]

    # 댓글 감정 분석
    classifier = EmotionClassifier()
    input_sentences = comments
    ratio = classifier.predict_and_calculate_ratio(input_sentences)

    # 비디오 정보 가져오기
    video_response = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    ).execute()

    title, uploadDate, = None, None
    if video_response['items']:
        video_info = video_response['items'][0]['snippet']
        title = video_info['title']
        upload_datetime = datetime.strptime(video_info['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        uploadDate = upload_datetime.strftime('%Y-%m-%d %H:%M:%S')
        #thumbnails url
        url = video_info['thumbnails']['default']['url']

    # JSON 응답 생성
    return {
        'video_id': video_id,
        'title': title,
        'uploadDate': uploadDate,
        'summary': summaries[0],
        'ratio': ratio,
        'url': url
    }
