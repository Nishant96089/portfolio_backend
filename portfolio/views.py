import os
from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ContactView(APIView):
    """Receives contact form input and emails it to you."""

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

        full_body = f"From: {name} ({email})\nSubject: {subject}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject=f"[Portfolio] {subject}",
                message=full_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.PORTFOLIO_OWNER_EMAIL],
                fail_silently=False,
            )
            return Response({'message': 'Email sent successfully!'}, status=status.HTTP_200_OK)
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