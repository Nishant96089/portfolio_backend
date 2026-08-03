import os
import resend
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView


class ContactThrottle(AnonRateThrottle):
    """Limits unauthenticated contact form submissions to 3 per hour per IP address."""

    rate = '3/hour'


class ContactView(APIView):
    """Receives contact form submissions via HTTP API with spam protection."""

    throttle_classes = [ContactThrottle]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject', 'Portfolio Contact')
        message = request.data.get('message')

        if not name or not email or not message:
            return Response(
                {'error': 'Name, email, and message are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resend.api_key = os.environ.get('RESEND_API_KEY')
        recipient = os.environ.get('PORTFOLIO_OWNER_EMAIL', 'your-email@gmail.com')

        try:
            resend.Emails.send({
                'from': 'onboarding@resend.dev',
                'to': [recipient],
                'subject': f'[Portfolio] {subject}',
                'html': f"""
                    <h3>New Contact Form Submission</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Message:</strong></p>
                    <p>{message}</p>
                """,
            })
            return Response(
                {'message': 'Email sent successfully!'}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResumeDownloadView(APIView):
    """Serves resume PDF for download."""

    def get(self, request):
        resume_path = os.path.join(
            settings.BASE_DIR, 'portfolio', 'static', 'files', 'resume.pdf'
        )

        if os.path.exists(resume_path):
            return FileResponse(
                open(resume_path, 'rb'),
                content_type='application/pdf',
                filename='Nishant_Resume.pdf',
                as_attachment=True,
            )
        raise Http404('Resume file not found.')