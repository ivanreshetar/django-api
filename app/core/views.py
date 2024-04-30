'''Core views for the app'''
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    '''Health check API returns status ok.'''
    return Response({'status': 'ok'})
