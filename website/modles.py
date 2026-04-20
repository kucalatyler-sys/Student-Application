from copy import deepcopy
from datetime import datetime


# In-memory store for submitted applications.
# This is reset when the Flask app restarts.
SUBMITTED_APPLICATIONS = []


def save_submitted_application(application_data):
	new_application = {
		'id': len(SUBMITTED_APPLICATIONS) + 1,
		'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'status': 'Submitted',
		'data': deepcopy(application_data)
	}
	SUBMITTED_APPLICATIONS.append(new_application)
	return new_application


def get_submitted_applications():
	# Show newest submissions first for faster admin review.
	return list(reversed(SUBMITTED_APPLICATIONS))


def get_submitted_application_by_id(application_id):
	for application in SUBMITTED_APPLICATIONS:
		if application['id'] == application_id:
			return deepcopy(application)
	return None
