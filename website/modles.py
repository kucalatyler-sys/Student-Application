from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	first_name = db.Column(db.String(150), nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	is_admin = db.Column(db.Boolean, nullable=False, default=False)

	applications = db.relationship('Application', back_populates='user')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


class Student(db.Model):
	__tablename__ = 'student'

	id = db.Column('StudentID', db.Integer, primary_key=True)
	last_name = db.Column('LastName', db.String(255), nullable=False, default='')
	first_name = db.Column('FirstName', db.String(255), nullable=False, default='')
	middle_initial = db.Column('MiddleInitial', db.String(10), nullable=False, default='')
	date_of_birth = db.Column('DateOfBirth', db.String(20), nullable=True)
	contact = db.Column('Contact', db.String(255), nullable=True)
	phone_number = db.Column('PhoneNumber', db.String(30), nullable=True)
	citizenship = db.Column('Citizenship', db.String(50), nullable=True)
	street_address = db.Column('StreetAddress', db.String(255), nullable=True)
	state = db.Column('State', db.String(50), nullable=True)
	city = db.Column('City', db.String(100), nullable=True)
	zipcode = db.Column('ZipCode', db.String(20), nullable=True)

	applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')
	finance = db.relationship('Finance', back_populates='student', uselist=False, cascade='all, delete-orphan')
	academic = db.relationship('Academic', back_populates='student', uselist=False, cascade='all, delete-orphan')
	income = db.relationship('Income', back_populates='student', uselist=False, cascade='all, delete-orphan')
	major_selection = db.relationship('MajorSelection', back_populates='student', uselist=False, cascade='all, delete-orphan')


class Finance(db.Model):
	__tablename__ = 'finance'

	id = db.Column('FinanceID', db.Integer, primary_key=True)
	household_income = db.Column('HouseholdIncome', db.String(100), nullable=True)
	financial_aid = db.Column('FinancialAid', db.String(20), nullable=True)
	aid_amount = db.Column('AidAmount', db.String(100), nullable=True)
	employment = db.Column('Employment', db.String(255), nullable=True)
	volunteer_work = db.Column('VolunteerWork', db.Text, nullable=True)
	assets = db.Column('Assets', db.String(100), nullable=True)
	expenses = db.Column('Expenses', db.String(100), nullable=True)
	financial_notes = db.Column('FinancialNotes', db.Text, nullable=True)
	student_id = db.Column('StudentID', db.Integer, db.ForeignKey('student.StudentID'), nullable=False, unique=True)

	student = db.relationship('Student', back_populates='finance')


class Academic(db.Model):
	__tablename__ = 'academics'

	id = db.Column('GradeID', db.Integer, primary_key=True)
	gpa = db.Column('GPA', db.String(20), nullable=True)
	school_name = db.Column('SchoolName', db.String(255), nullable=True)
	notes = db.Column('Notes', db.Text, nullable=True)
	transcript_path = db.Column('TranscriptPath', db.String(255), nullable=True)
	student_id = db.Column('StudentID', db.Integer, db.ForeignKey('student.StudentID'), nullable=False, unique=True)

	student = db.relationship('Student', back_populates='academic')


class Income(db.Model):
	__tablename__ = 'income'

	id = db.Column('IncomeID', db.Integer, primary_key=True)
	guardian_first_name = db.Column('GuardianFirstName', db.String(255), nullable=True)
	guardian_middle_initial = db.Column('GuardianMiddleInitial', db.String(10), nullable=True)
	guardian_last_name = db.Column('GuardianLastName', db.String(255), nullable=True)
	guardian_relationship = db.Column('GuardianRelationship', db.String(50), nullable=True)
	guardian_income = db.Column('GuardianIncome', db.String(100), nullable=True)
	guardian_employment = db.Column('GuardianEmployment', db.String(255), nullable=True)
	income_support = db.Column('IncomeSupport', db.String(255), nullable=True)
	people_supported = db.Column('PeopleSupported', db.String(20), nullable=True)
	guardian_notes = db.Column('GuardianNotes', db.Text, nullable=True)
	income_documents_path = db.Column('IncomeDocumentsPath', db.String(255), nullable=True)
	student_id = db.Column('StudentID', db.Integer, db.ForeignKey('student.StudentID'), nullable=False, unique=True)

	student = db.relationship('Student', back_populates='income')


class MajorSelection(db.Model):
	__tablename__ = 'major'

	id = db.Column('MajorID', db.Integer, primary_key=True)
	major_choice = db.Column('MajorChoice', db.String(255), nullable=False, default='')
	minor_choice = db.Column('MinorChoice', db.String(255), nullable=True)
	notes = db.Column('Notes', db.Text, nullable=True)
	student_id = db.Column('StudentID', db.Integer, db.ForeignKey('student.StudentID'), nullable=False, unique=True)

	student = db.relationship('Student', back_populates='major_selection')


class Application(db.Model):
	__tablename__ = 'applications'

	id = db.Column('ApplicationID', db.Integer, primary_key=True)
	student_id = db.Column('StudentID', db.Integer, db.ForeignKey('student.StudentID'), nullable=False)
	user_id = db.Column('UserID', db.Integer, db.ForeignKey('users.id'), nullable=True)
	submitted_at = db.Column('SubmittedAt', db.DateTime, nullable=False, default=datetime.utcnow)
	status = db.Column('Status', db.String(30), nullable=False, default='Draft')
	reviewed_by = db.Column('ReviewedBy', db.Integer, nullable=True)
	reviewed_at = db.Column('ReviewedAt', db.DateTime, nullable=True)
	admin_notes = db.Column('AdminNotes', db.Text, nullable=True)
	additional_info_text = db.Column('AdditionalInfo', db.Text, nullable=True)

	student = db.relationship('Student', back_populates='applications')
	user = db.relationship('User', back_populates='applications')


def _has_values(section_data):
	if not section_data:
		return False
	return any(str(value).strip() for value in section_data.values() if value is not None)



def _application_belongs_to_user(application, user_id):
	if application is None:
		return False
	if user_id is None:
		return True
	return application.user_id == user_id


def _get_or_create_application(application_id=None, create_new_draft=False, user_id=None):
	application = db.session.get(Application, application_id) if application_id else None
	if application and not _application_belongs_to_user(application, user_id):
		application = None

	if application and not (create_new_draft and application.status == 'Submitted'):
		return application

	application = Application(student=Student(), status='Draft', submitted_at=datetime.utcnow(), user_id=user_id)
	db.session.add(application)
	return application


def _get_or_create_related(model_class, student_id):
	record = model_class.query.filter_by(student_id=student_id).first()
	if record is None:
		record = model_class(student_id=student_id)
		db.session.add(record)
	return record


def _update_student(student, personal_info):
	student.first_name = personal_info.get('first_name', '')
	student.middle_initial = personal_info.get('middle_initial', '')
	student.last_name = personal_info.get('last_name', '')
	student.date_of_birth = personal_info.get('dob', '')
	student.contact = personal_info.get('contact', '')
	student.citizenship = personal_info.get('citizenship', '')
	student.street_address = personal_info.get('street_address', '')
	student.state = personal_info.get('state', '')
	student.city = personal_info.get('city', '')
	student.zipcode = personal_info.get('zipcode', '')
	student.phone_number = personal_info.get('phone_number', '')


def _update_finance(student_id, financial_info):
	finance = _get_or_create_related(Finance, student_id)
	finance.household_income = financial_info.get('household_income', '')
	finance.financial_aid = financial_info.get('financial_aid', '')
	finance.aid_amount = financial_info.get('aid_amount', '')
	finance.employment = financial_info.get('employment', '')
	finance.volunteer_work = financial_info.get('volunteer_work', '')
	finance.assets = financial_info.get('assets', '')
	finance.expenses = financial_info.get('expenses', '')
	finance.financial_notes = financial_info.get('financial_notes', '')


def _update_academic(student_id, academic_info):
	academic = _get_or_create_related(Academic, student_id)
	academic.school_name = academic_info.get('school_name', '')
	academic.gpa = academic_info.get('gpa', '')
	academic.notes = academic_info.get('academic_notes', '')
	academic.transcript_path = academic_info.get('transcript_filename', '')


def _update_income(student_id, parental_info):
	income = _get_or_create_related(Income, student_id)
	income.guardian_first_name = parental_info.get('guardian_first_name', '')
	income.guardian_middle_initial = parental_info.get('guardian_middle_initial', '')
	income.guardian_last_name = parental_info.get('guardian_last_name', '')
	income.guardian_relationship = parental_info.get('guardian_relationship', '')
	income.guardian_income = parental_info.get('parent_income', '')
	income.guardian_employment = parental_info.get('employment_details', '')
	income.income_support = parental_info.get('support_source', '')
	income.people_supported = parental_info.get('household_size', '')
	income.guardian_notes = parental_info.get('income_notes', '')
	income.income_documents_path = parental_info.get('income_documents_filename', '')


def _update_major(student_id, major_info):
	major = _get_or_create_related(MajorSelection, student_id)
	major.major_choice = major_info.get('major_choice', '')
	major.minor_choice = major_info.get('minor_choice', '')
	major.notes = major_info.get('major_comments', '')


def _serialize_personal_info(student):
	if student is None:
		return {}
	return {
		'first_name': student.first_name or '',
		'middle_initial': student.middle_initial or '',
		'last_name': student.last_name or '',
		'dob': student.date_of_birth or '',
		'contact': student.contact or '',
		'citizenship': student.citizenship or '',
		'street_address': student.street_address or '',
		'state': student.state or '',
		'city': student.city or '',
		'zipcode': student.zipcode or '',
		'phone_number': student.phone_number or '',
	}


def _serialize_financial_info(finance):
	if finance is None:
		return {}
	return {
		'household_income': finance.household_income or '',
		'financial_aid': finance.financial_aid or '',
		'aid_amount': finance.aid_amount or '',
		'employment': finance.employment or '',
		'volunteer_work': finance.volunteer_work or '',
		'assets': finance.assets or '',
		'expenses': finance.expenses or '',
		'financial_notes': finance.financial_notes or '',
	}


def _serialize_academic_info(academic):
	if academic is None:
		return {}
	return {
		'school_name': academic.school_name or '',
		'gpa': academic.gpa or '',
		'academic_notes': academic.notes or '',
		'transcript_filename': academic.transcript_path or '',
	}


def _serialize_parental_info(income):
	if income is None:
		return {}
	return {
		'guardian_first_name': income.guardian_first_name or '',
		'guardian_middle_initial': income.guardian_middle_initial or '',
		'guardian_last_name': income.guardian_last_name or '',
		'guardian_relationship': income.guardian_relationship or '',
		'parent_income': income.guardian_income or '',
		'employment_details': income.guardian_employment or '',
		'support_source': income.income_support or '',
		'household_size': income.people_supported or '',
		'income_notes': income.guardian_notes or '',
		'income_documents_filename': income.income_documents_path or '',
	}


def _serialize_major_info(major):
	if major is None:
		return {}
	return {
		'major_choice': major.major_choice or '',
		'minor_choice': major.minor_choice or '',
		'major_comments': major.notes or '',
	}


def _serialize_application(application):
	student = application.student
	return {
		'id': application.id,
		'submitted_at': application.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if application.submitted_at else '',
		'status': application.status,
		'data': {
			'personal_info': _serialize_personal_info(student),
			'financial_info': _serialize_financial_info(student.finance if student else None),
			'academic_info': _serialize_academic_info(student.academic if student else None),
			'parental_info': _serialize_parental_info(student.income if student else None),
			'major_info': _serialize_major_info(student.major_selection if student else None),
			'additional_info': {
				'additional_info_text': application.additional_info_text or '',
			},
		}
	}


def save_application_snapshot(
	personal_info=None,
	financial_info=None,
	academic_info=None,
	parental_info=None,
	major_info=None,
	additional_info=None,
	application_id=None,
	user_id=None,
	status='Draft'
):
	application = _get_or_create_application(application_id, create_new_draft=(status == 'Draft'), user_id=user_id)
	student = application.student
	application.user_id = user_id

	if _has_values(personal_info):
		_update_student(student, personal_info)

	db.session.flush()

	if _has_values(financial_info):
		_update_finance(student.id, financial_info)

	if _has_values(academic_info):
		_update_academic(student.id, academic_info)

	if _has_values(parental_info):
		_update_income(student.id, parental_info)

	if _has_values(major_info):
		_update_major(student.id, major_info)

	if additional_info is not None:
		application.additional_info_text = additional_info.get('additional_info_text', '')

	if status == 'Submitted':
		application.status = 'Submitted'
		application.submitted_at = datetime.utcnow()
	elif application.status != 'Submitted':
		application.status = 'Draft'
		if application.submitted_at is None:
			application.submitted_at = datetime.utcnow()

	db.session.commit()
	return _serialize_application(application)



def get_application_snapshot(application_id, user_id=None):
	application = db.session.get(Application, application_id)
	if application is None or not _application_belongs_to_user(application, user_id):
		return None
	return _serialize_application(application)



def get_submitted_applications(user_id=None):
	query = Application.query.filter(Application.status != 'Draft')
	if user_id is not None:
		query = query.filter_by(user_id=user_id)
	applications = query.order_by(Application.submitted_at.desc()).all()
	return [_serialize_application(application) for application in applications]



def get_submitted_application_by_id(application_id, user_id=None):
	application = db.session.get(Application, application_id)
	if application is None or not _application_belongs_to_user(application, user_id):
		return None
	return _serialize_application(application)


def get_user_by_email(email):
	return User.query.filter(db.func.lower(User.email) == email.lower()).first()


def create_user(email, first_name, password):
	user = User(email=email, first_name=first_name)
	user.set_password(password)
	db.session.add(user)
	db.session.commit()
	return user


def get_user_submissions(user_id):
	applications = (
		Application.query
		.filter(Application.user_id == user_id, Application.status != 'Draft')
		.order_by(Application.submitted_at.desc())
		.all()
	)
	return [_serialize_application(a) for a in applications]
	return [_serialize_application(a) for a in applications]


def update_application_status(application_id, new_status, admin_id=None, admin_notes=None):
	"""Update the status of an application. Returns the serialized application or None."""
	application = db.session.get(Application, application_id)
	if application is None:
		return None
	application.status = new_status
	if admin_id is not None:
		application.reviewed_by = admin_id
		application.reviewed_at = datetime.utcnow()
	if admin_notes is not None:
		application.admin_notes = admin_notes
	db.session.commit()
	return _serialize_application(application)
