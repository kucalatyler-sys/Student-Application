from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from .modles import (
    get_application_snapshot,
    get_user_submissions,
    save_application_snapshot,
    get_submitted_applications,
    get_submitted_application_by_id,
    update_application_status,
)
from .notifications import send_submission_confirmation, send_status_update

views = Blueprint('views', __name__)


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You are not authorized to view that page.', category='error')
            return redirect(url_for('views.home'))
        return view_func(*args, **kwargs)

    return wrapped_view


def get_current_application_data():
    application_id = session.get('application_id')
    if not application_id:
        return {}

    application = get_application_snapshot(application_id, user_id=current_user.id if current_user.is_authenticated else None)
    if not application:
        session.pop('application_id', None)
        return {}

    return application['data']


def save_current_application(status='Draft'):
    saved_application = save_application_snapshot(
        personal_info=session.get('personal_info', {}),
        financial_info=session.get('financial_info', {}),
        academic_info=session.get('academic_info', {}),
        parental_info=session.get('parental_info', {}),
        major_info=session.get('major_info', {}),
        additional_info=session.get('additional_info', {}),
        application_id=session.get('application_id'),
        user_id=current_user.id,
        status=status,
    )
    session['application_id'] = saved_application['id']
    return saved_application


def is_pdf_file(file_obj):
    if not file_obj or not file_obj.filename:
        return False
    return file_obj.filename.lower().endswith('.pdf')

@views.route('/', methods=['GET'])
@login_required
def home():
    applications = get_submitted_applications(user_id=current_user.id)
    has_submitted_application = len(applications) > 0
    latest_application = applications[0] if has_submitted_application else None

    return render_template(
        'home.html',
        applications=applications,
        has_submitted_application=has_submitted_application,
        latest_application=latest_application,
    )


@views.route('/start-application', methods=['GET', 'POST'])
@login_required
def start_application():
    if request.method == 'POST':
        existing_application = get_application_snapshot(session.get('application_id'), user_id=current_user.id) if session.get('application_id') else None
        if existing_application and existing_application['status'] == 'Submitted':
            session.pop('application_id', None)
            session.pop('financial_info', None)
            session.pop('academic_info', None)
            session.pop('parental_info', None)
            session.pop('major_info', None)
            session.pop('additional_info', None)

        first_name = request.form.get('firstName', '').strip()
        middle_initial = request.form.get('middleInitial', '').strip()
        last_name = request.form.get('lastName', '').strip()
        dob = request.form.get('dob', '').strip()
        contact = request.form.get('contact', '').strip()
        citizenship = request.form.get('citizenship', '').strip()
        street_address = request.form.get('streetAddress', '').strip()
        state = request.form.get('state', '').strip()
        city = request.form.get('City', '').strip()
        zipcode = request.form.get('zipCode', '').strip()
        phone_number = request.form.get('phoneNumber', '').strip()

        # Required fields for all
        required_fields = [first_name, last_name, dob, contact, phone_number, citizenship]

        if citizenship == 'us_citizen':
            # Add address fields if US citizen
            required_fields.extend([street_address, state, city, zipcode])

        if not all(required_fields):
            flash('Please fill out all required fields before continuing.', category='error')
            return render_template('base.html', personal_info=session.get('personal_info', {}))

        # Store personal information in session
        session['personal_info'] = {
            'first_name': first_name,
            'middle_initial': middle_initial,
            'last_name': last_name,
            'dob': dob,
            'contact': contact,
            'citizenship': citizenship,
            'street_address': street_address,
            'state': state,
            'city': city,
            'zipcode': zipcode,
            'phone_number': phone_number
        }
        save_current_application()

        return redirect(url_for('views.financial'))

    application_data = get_current_application_data()
    personal_info = session.get('personal_info') or application_data.get('personal_info', {})
    return render_template('base.html', personal_info=personal_info)

@views.route('/financial', methods=['GET', 'POST'])
@login_required
def financial():
    if request.method == 'POST':
        household_income = request.form.get('householdIncome', '').strip()
        financial_aid = request.form.get('financialAid', '').strip()
        aid_amount = request.form.get('aidAmount', '').strip()
        employment = request.form.get('employment', '').strip()
        volunteer_work = request.form.get('volunteerWork', '').strip()
        assets = request.form.get('assets', '').strip()
        expenses = request.form.get('expenses', '').strip()
        financial_notes = request.form.get('financialNotes', '').strip()

        required_fields2 = [household_income, financial_aid, employment, volunteer_work, assets, expenses]
        
        if financial_aid == 'yes':
            required_fields2.extend([aid_amount])
        
        if not all(required_fields2):
            flash('Please fill out all required fields before continuing.', category='error')
            return render_template('financial.html')

        # Store financial information in session
        session['financial_info'] = {
            'household_income': household_income,
            'financial_aid': financial_aid,
            'aid_amount': aid_amount,
            'employment': employment,
            'volunteer_work': volunteer_work,
            'assets': assets,
            'expenses': expenses,
            'financial_notes': financial_notes
        }
        save_current_application()

        return redirect(url_for('views.academic_history'))

    application_data = get_current_application_data()
    financial_info = session.get('financial_info') or application_data.get('financial_info', {})
    return render_template('financial.html', financial_info=financial_info)

@views.route('/academic-history', methods=['GET', 'POST'])
@login_required
def academic_history():
    if request.method == 'POST':
        school_name = request.form.get('schoolName', '').strip()
        gpa = request.form.get('gpa', '').strip()
        academic_notes = request.form.get('academicNotes', '').strip()
        transcript = request.files.get('transcriptUpload')

        if not all([school_name, gpa, academic_notes]) or not transcript or transcript.filename == '':
            flash('Please fill out all required academic fields and upload your transcript.', category='error')
            return render_template('academic_history.html')

        if not is_pdf_file(transcript):
            flash('Transcript upload must be a PDF file (.pdf).', category='error')
            return render_template('academic_history.html', academic_info=session.get('academic_info', {}))

        # Store academic information in session
        session['academic_info'] = {
            'school_name': school_name,
            'gpa': gpa,
            'academic_notes': academic_notes,
            'transcript_filename': transcript.filename
        }
        save_current_application()

        return redirect(url_for('views.income'))

    application_data = get_current_application_data()
    academic_info = session.get('academic_info') or application_data.get('academic_info', {})
    return render_template('academic_history.html', academic_info=academic_info)

@views.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    if request.method == 'POST':
        guardianfirst_name = request.form.get('guardianfirstName', '').strip()
        guardianmiddle_initial = request.form.get('guardianmiddleInitial', '').strip()
        guardianlast_name = request.form.get('guardianlastName', '').strip()
        guardian_relationship = request.form.get('guardianRelationship', '').strip()
        parent_income = request.form.get('parentIncome', '').strip()
        employment_details = request.form.get('employmentDetails', '').strip()
        support_source = request.form.get('supportSource', '').strip()
        household_size = request.form.get('householdSize', '').strip()
        income_notes = request.form.get('incomeNotes', '').strip()
        income_documents = request.files.get('incomeDocuments')

        if not all([guardianfirst_name, guardianmiddle_initial, guardianlast_name, guardian_relationship, parent_income, employment_details, support_source, household_size, income_notes]) or not income_documents or income_documents.filename == '':
            flash('Please fill out all required parental income fields and upload your documents.', category='error')
            parental_info = {
                'guardian_first_name': guardianfirst_name,
                'guardian_middle_initial': guardianmiddle_initial,
                'guardian_last_name': guardianlast_name,
                'guardian_relationship': guardian_relationship,
                'parent_income': parent_income,
                'employment_details': employment_details,
                'support_source': support_source,
                'household_size': household_size,
                'income_notes': income_notes,
            }
            return render_template('income.html', parental_info=parental_info)

        if not is_pdf_file(income_documents):
            flash('Guardian income document upload must be a PDF file (.pdf).', category='error')
            return render_template('income.html', parental_info=session.get('parental_info', {}))

        # Store parental income information in session
        session['parental_info'] = {
            'guardian_first_name': guardianfirst_name,
            'guardian_middle_initial': guardianmiddle_initial,
            'guardian_last_name': guardianlast_name,
            'guardian_relationship': guardian_relationship,
            'parent_income': parent_income,
            'employment_details': employment_details,
            'support_source': support_source,
            'household_size': household_size,
            'income_notes': income_notes,
            'income_documents_filename': income_documents.filename
        }
        save_current_application()

        return redirect(url_for('views.major'))

    application_data = get_current_application_data()
    parental_info = session.get('parental_info') or application_data.get('parental_info', {})
    return render_template('income.html', parental_info=parental_info)

@views.route('/major', methods=['GET', 'POST'])
@login_required
def major():
    if request.method == 'POST':
        major_choice = request.form.get('major', '').strip()
        minor_choice = request.form.get('minor', '').strip()
        major_comments = request.form.get('majorComments', '').strip()

        if not all([major_choice]):
            flash('Please choose a major.', category='error')
            return render_template('major.html')

        # Store major information in session
        session['major_info'] = {
            'major_choice': major_choice,
            'minor_choice': minor_choice,
            'major_comments': major_comments
        }
        save_current_application()

        return redirect(url_for('views.additional_info'))

    application_data = get_current_application_data()
    major_info = session.get('major_info') or application_data.get('major_info', {})
    return render_template('major.html', major_info=major_info)

@views.route('/additional-info', methods=['GET', 'POST'])
@login_required
def additional_info():
    if request.method == 'POST':
        additional_info_text = request.form.get('additionalInfo', '').strip()

        # Store additional information in session
        session['additional_info'] = {
            'additional_info_text': additional_info_text
        }
        save_current_application()

        return redirect(url_for('views.review_and_submit'))

    application_data = get_current_application_data()
    additional_info = session.get('additional_info') or application_data.get('additional_info', {})
    return render_template('additional_info.html', additional_info=additional_info)

@views.route('/review-and-submit', methods=['GET', 'POST'])
@login_required
def review_and_submit():
    application_data = get_current_application_data()
    personal_info = session.get('personal_info') or application_data.get('personal_info', {})
    financial_info = session.get('financial_info') or application_data.get('financial_info', {})
    academic_info = session.get('academic_info') or application_data.get('academic_info', {})
    parental_info = session.get('parental_info') or application_data.get('parental_info', {})
    major_info = session.get('major_info') or application_data.get('major_info', {})
    additional_info = session.get('additional_info') or application_data.get('additional_info', {})

    if request.method == 'POST':
        confirm_submit = request.form.get('confirmSubmit')
        if not confirm_submit:
            flash('Please confirm that all information is accurate before submitting.', category='error')
            return render_template('review_and_submit.html',
                                 personal_info=personal_info,
                                 financial_info=financial_info,
                                 academic_info=academic_info,
                                 parental_info=parental_info,
                                 major_info=major_info,
                                 additional_info=additional_info)

        saved_application = save_current_application(status='Submitted')

        # ── Send confirmation email ──────────────────────────────────────────
        student_email = (
            session.get('personal_info', {}).get('contact')
            or current_user.email
        )
        send_submission_confirmation(student_email, saved_application['id'])

        flash(f"Application #{saved_application['id']} submitted successfully!", category='success')
        return redirect(url_for('views.review_and_submit'))

    return render_template('review_and_submit.html',
                         personal_info=personal_info,
                         financial_info=financial_info,
                         academic_info=academic_info,
                         parental_info=parental_info,
                         major_info=major_info,
                         additional_info=additional_info)


@views.route('/admin/review-applications', methods=['GET'])
@admin_required
def admin_review_applications():
    applications = get_submitted_applications()
    return render_template('admin_list.html', applications=applications)


@views.route('/admin/review-applications/<int:application_id>', methods=['GET', 'POST'])
@admin_required
def admin_verification(application_id):
    application = get_submitted_application_by_id(application_id)
    if not application:
        flash('Application not found.', category='error')
        return redirect(url_for('views.admin_review_applications'))

    if request.method == 'POST':
        new_status = request.form.get('status', '').strip()
        admin_notes = request.form.get('admin_notes', '').strip() or None
        if new_status:
            updated = update_application_status(
                application_id,
                new_status,
                admin_id=current_user.id,
                admin_notes=admin_notes,
            )
            if updated:
                # Notify the student via the contact email they provided
                student_email = (
                    updated['data']['personal_info'].get('contact')
                    or (updated.get('user_email'))
                )
                send_status_update(student_email, application_id, new_status, admin_notes)
                flash(f'Status updated to "{new_status}".', category='success')
            else:
                flash('Could not update status.', category='error')
        return redirect(url_for('views.admin_verification', application_id=application_id))

    return render_template('admin_verification.html', application=application)


@views.route('/my-submissions', methods=['GET'])
@login_required
def my_submissions():
    submissions = get_user_submissions(user_id=current_user.id)
    return render_template('my_submissions.html', submissions=submissions)


@views.route('/my-submissions/<int:application_id>', methods=['GET'])
@login_required
def my_submission_detail(application_id):
    application = get_submitted_application_by_id(application_id, user_id=current_user.id)
    if not application:
        flash('Submission not found.', category='error')
        return redirect(url_for('views.my_submissions'))
    return render_template('my_submission_detail.html', application=application)


@views.route('/information', methods=['GET'])
def information():
    return render_template('information.html')


@views.route('/staff-inquiries', methods=['GET'])
def staff_inquiries():
    return render_template('staff_inquiries.html')


