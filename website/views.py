from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .modles import (
    save_submitted_application,
    get_submitted_applications,
    get_submitted_application_by_id,
)

views = Blueprint('views', __name__)


def is_pdf_file(file_obj):
    if not file_obj or not file_obj.filename:
        return False
    return file_obj.filename.lower().endswith('.pdf')

@views.route('/', methods=['GET'])
def home():
    applications = get_submitted_applications()
    has_submitted_application = len(applications) > 0
    latest_application = applications[0] if has_submitted_application else None

    return render_template(
        'home.html',
        has_submitted_application=has_submitted_application,
        latest_application=latest_application,
    )


@views.route('/start-application', methods=['GET', 'POST'])
def start_application():
    if request.method == 'POST':
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

        return redirect(url_for('views.financial'))

    # Pre-populate form with session data
    personal_info = session.get('personal_info', {})
    return render_template('base.html', personal_info=personal_info)

@views.route('/financial', methods=['GET', 'POST'])
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

        return redirect(url_for('views.academic_history'))

    # Pre-populate form with session data
    financial_info = session.get('financial_info', {})
    return render_template('financial.html', financial_info=financial_info)

@views.route('/academic-history', methods=['GET', 'POST'])
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

        return redirect(url_for('views.income'))

    # Pre-populate form with session data
    academic_info = session.get('academic_info', {})
    return render_template('academic_history.html', academic_info=academic_info)

@views.route('/income', methods=['GET', 'POST'])
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
            return render_template('income.html')

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

        return redirect(url_for('views.major'))

    # Pre-populate form with session data
    parental_info = session.get('parental_info', {})
    return render_template('income.html', parental_info=parental_info)

@views.route('/major', methods=['GET', 'POST'])
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

        return redirect(url_for('views.additional_info'))

    # Pre-populate form with session data
    major_info = session.get('major_info', {})
    return render_template('major.html', major_info=major_info)

@views.route('/additional-info', methods=['GET', 'POST'])
def additional_info():
    if request.method == 'POST':
        additional_info_text = request.form.get('additionalInfo', '').strip()

        # Store additional information in session
        session['additional_info'] = {
            'additional_info_text': additional_info_text
        }

        return redirect(url_for('views.review_and_submit'))

    # Pre-populate form with session data
    additional_info = session.get('additional_info', {})
    return render_template('additional_info.html', additional_info=additional_info)

@views.route('/review-and-submit', methods=['GET', 'POST'])
def review_and_submit():
    # Retrieve all stored data from session
    personal_info = session.get('personal_info', {})
    financial_info = session.get('financial_info', {})
    academic_info = session.get('academic_info', {})
    parental_info = session.get('parental_info', {})
    major_info = session.get('major_info', {})
    additional_info = session.get('additional_info', {})

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

        saved_application = save_submitted_application({
            'personal_info': personal_info,
            'financial_info': financial_info,
            'academic_info': academic_info,
            'parental_info': parental_info,
            'major_info': major_info,
            'additional_info': additional_info
        })

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
def admin_review_applications():
    applications = get_submitted_applications()
    return render_template('admin_list.html', applications=applications)


@views.route('/admin/review-applications/<int:application_id>', methods=['GET'])
def admin_verification(application_id):
    application = get_submitted_application_by_id(application_id)
    if not application:
        flash('Application not found.', category='error')
        return redirect(url_for('views.admin_review_applications'))

    return render_template('admin_verification.html', application=application)


@views.route('/information', methods=['GET'])
def information():
    return render_template('information.html')


@views.route('/staff-inquiries', methods=['GET'])
def staff_inquiries():
    return render_template('staff_inquiries.html')


