"""
Email notification helpers.
All functions silently log failures so a broken mail config never crashes the app.
"""
import logging

from flask import current_app
from flask_mail import Message

from . import mail

logger = logging.getLogger(__name__)

# ── Allowed statuses that trigger a student notification ──────────────────────
NOTIFIABLE_STATUSES = {'Submitted', 'Under Review', 'Approved', 'Rejected', 'More Info Needed'}

# ── Status-specific subject lines and body snippets ───────────────────────────
_STATUS_COPY = {
    'Submitted': {
        'subject': 'Application #{id} Received – SCSU',
        'body': (
            "We have received your application (#{id}) and it is now under initial review.\n"
            "You will hear from us once a decision has been made."
        ),
    },
    'Under Review': {
        'subject': 'Application #{id} Is Being Reviewed – SCSU',
        'body': "Your application (#{id}) is currently being reviewed by our admissions team.",
    },
    'Approved': {
        'subject': 'Congratulations! Application #{id} Approved – SCSU',
        'body': (
            "Great news! Your application (#{id}) has been approved.\n"
            "Please log in to view next steps."
        ),
    },
    'Rejected': {
        'subject': 'Application #{id} Status Update – SCSU',
        'body': (
            "Thank you for applying to SCSU. After careful review, we are unable to\n"
            "move forward with your application (#{id}) at this time.\n"
            "Please contact the admissions office if you have any questions."
        ),
    },
    'More Info Needed': {
        'subject': 'Action Required: Application #{id} – SCSU',
        'body': (
            "Our team needs additional information to continue reviewing your\n"
            "application (#{id}). Please log in to check the admin notes and\n"
            "contact the admissions office."
        ),
    },
}

_DEFAULT_COPY = {
    'subject': 'Application #{id} Status Update – SCSU',
    'body': "The status of your application (#{id}) has been updated to: {status}.",
}


def _build_message(to_address, application_id, status, admin_notes=None):
    copy = _STATUS_COPY.get(status, _DEFAULT_COPY)
    subject = copy['subject'].format(id=application_id)
    body_lines = [
        f"Dear Applicant,\n",
        copy['body'].format(id=application_id, status=status),
    ]
    if admin_notes:
        body_lines.append(f"\nNote from admissions:\n{admin_notes}")
    body_lines.append(
        "\n\nYou can log in at any time to view your application details:\n"
        f"{current_app.config.get('APP_BASE_URL', 'https://student-application-288f.onrender.com/')}/my-submissions\n"
        "\nSt. Cloud State University Admissions"
    )
    return Message(
        subject=subject,
        recipients=[to_address],
        body="\n".join(body_lines),
    )


def send_submission_confirmation(to_address, application_id):
    """Send a confirmation email when a student submits an application."""
    if not to_address:
        logger.warning("send_submission_confirmation: no email address, skipping")
        return
    if not current_app.config.get('MAIL_USERNAME'):
        logger.warning("send_submission_confirmation: MAIL_USERNAME not configured, skipping email")
        return
    try:
        msg = _build_message(to_address, application_id, 'Submitted')
        mail.send(msg)
        logger.info("Submission confirmation sent to %s for application #%s", to_address, application_id)
    except Exception as exc:
        logger.exception("Failed to send submission confirmation for application #%s: %s", application_id, exc)


def send_status_update(to_address, application_id, new_status, admin_notes=None):
    """Send a status-change notification to the student."""
    if not to_address:
        logger.warning("send_status_update: no email address, skipping")
        return
    if new_status not in NOTIFIABLE_STATUSES:
        return
    if not current_app.config.get('MAIL_USERNAME'):
        logger.warning("send_status_update: MAIL_USERNAME not configured, skipping email")
        return
    try:
        msg = _build_message(to_address, application_id, new_status, admin_notes)
        mail.send(msg)
        logger.info("Status update email sent to %s (app #%s \u2192 %s)", to_address, application_id, new_status)
    except Exception as exc:
        logger.exception("Failed to send status update for application #%s: %s", application_id, exc)
