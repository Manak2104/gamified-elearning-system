from flask import request, jsonify, session, send_from_directory
from app import web_application, storage_layer
from models import (PersonEntity, CredentialResetTicket, LearningModule, ClassMembership,
                    ResourceDocument, TaskItem, WorkSubmission, TrophyDefinition,
                    TrophyOwnership, MilestoneRecord, InteractiveActivity, PlaySession)
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import secrets
import random

def craft_random_token(token_length=40):
    return secrets.token_urlsafe(token_length)

def verify_session_active(handler_func):
    def wrapper_function(*positional_args, **keyword_args):
        if 'user_id' not in session:
            return jsonify({'error': 'Must be logged in'}), 401
        return handler_func(*positional_args, **keyword_args)
    wrapper_function.__name__ = handler_func.__name__
    return wrapper_function

def verify_role_access(*permitted_roles):
    def outer_wrapper(handler_func):
        def inner_wrapper(*positional_args, **keyword_args):
            if 'user_id' not in session:
                return jsonify({'error': 'Must be logged in'}), 401
            person = PersonEntity.query.get(session['user_id'])
            if not person or person.role not in permitted_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return handler_func(*positional_args, **keyword_args)
        inner_wrapper.__name__ = handler_func.__name__
        return inner_wrapper
    return outer_wrapper

def persist_uploaded_asset(asset_file, subfolder_name):
    if asset_file and asset_file.filename:
        sanitized_name = secure_filename(asset_file.filename)
        time_marker = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_name = f"{time_marker}_{sanitized_name}"
        storage_path = os.path.join(web_application.config['FILE_STORAGE_PATH'], subfolder_name, final_name)
        asset_file.save(storage_path)
        return f'/uploads/{subfolder_name}/{final_name}'
    return None

# ===== AUTHENTICATION ENDPOINTS =====

@web_application.route('/')
def landing_page():
    return send_from_directory(web_application.static_folder, 'login.html')

@web_application.route('/api/auth/signup', methods=['POST'])
def create_new_account():
    incoming_data = request.get_json()
    
    if not incoming_data.get('username') or not incoming_data.get('email') or not incoming_data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    account_role = incoming_data.get('role', 'student')
    if account_role not in ['student', 'teacher']:
        return jsonify({'error': 'Role must be student or teacher'}), 400
    
    existing_person = PersonEntity.query.filter(
        (PersonEntity.username == incoming_data['username']) | (PersonEntity.email == incoming_data['email'])
    ).first()
    
    if existing_person:
        return jsonify({'error': 'Account already exists'}), 409
    
    fresh_person = PersonEntity(
        username=incoming_data['username'],
        email=incoming_data['email'],
        role=account_role
    )
    fresh_person.encode_credential(incoming_data['password'])
    
    if 'profile_picture' in request.files:
        picture_file = request.files['profile_picture']
        fresh_person.profile_picture = persist_uploaded_asset(picture_file, 'profiles')
    
    storage_layer.session.add(fresh_person)
    storage_layer.session.commit()
    
    return jsonify({
        'message': 'Account created successfully',
        'user': fresh_person.serialize_info()
    }), 201

@web_application.route('/api/auth/signin', methods=['POST'])
def authenticate_person():
    incoming_data = request.get_json()
    
    if not incoming_data.get('username') or not incoming_data.get('password'):
        return jsonify({'error': 'Username and password needed'}), 400
    
    person = PersonEntity.query.filter_by(username=incoming_data['username']).first()
    
    if not person or not person.authenticate_credential(incoming_data['password']):
        return jsonify({'error': 'Authentication failed'}), 401
    
    session.permanent = True
    session['user_id'] = person.user_id
    session['role'] = person.role
    session['username'] = person.username
    
    return jsonify({
        'message': 'Authentication successful',
        'user': person.serialize_info()
    }), 200

@web_application.route('/api/auth/signout', methods=['POST'])
@verify_session_active
def terminate_session():
    session.clear()
    return jsonify({'message': 'Signed out'}), 200

@web_application.route('/api/auth/whoami', methods=['GET'])
@verify_session_active
def fetch_active_user():
    person = PersonEntity.query.get(session['user_id'])
    if not person:
        return jsonify({'error': 'User not located'}), 404
    return jsonify({'user': person.serialize_info()}), 200

@web_application.route('/api/auth/request-reset', methods=['POST'])
def begin_credential_reset():
    incoming_data = request.get_json()
    
    if not incoming_data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    person = PersonEntity.query.filter_by(email=incoming_data['email']).first()
    
    if not person:
        return jsonify({'message': 'Reset request processed'}), 200
    
    reset_token = craft_random_token(48)
    expiry_time = datetime.utcnow() + timedelta(hours=1)
    
    reset_ticket = CredentialResetTicket(
        user_id=person.user_id,
        token=reset_token,
        expires_at=expiry_time
    )
    
    storage_layer.session.add(reset_ticket)
    storage_layer.session.commit()
    
    return jsonify({
        'message': 'Reset initiated',
        'reset_token': reset_token
    }), 200

@web_application.route('/api/auth/finalize-reset', methods=['POST'])
def execute_credential_reset():
    incoming_data = request.get_json()
    
    if not incoming_data.get('token') or not incoming_data.get('new_password'):
        return jsonify({'error': 'Token and password required'}), 400
    
    reset_ticket = CredentialResetTicket.query.filter_by(
        token=incoming_data['token'],
        used=False
    ).first()
    
    if not reset_ticket or reset_ticket.expires_at < datetime.utcnow():
        return jsonify({'error': 'Invalid token'}), 400
    
    person = PersonEntity.query.get(reset_ticket.user_id)
    person.encode_credential(incoming_data['new_password'])
    reset_ticket.used = True
    
    storage_layer.session.commit()
    
    return jsonify({'message': 'Password updated'}), 200

# ===== PROFILE MANAGEMENT =====

@web_application.route('/api/profile/modify', methods=['PUT'])
@verify_session_active
def alter_profile():
    person = PersonEntity.query.get(session['user_id'])
    incoming_data = request.get_json()
    
    if incoming_data.get('email'):
        person.email = incoming_data['email']
    
    storage_layer.session.commit()
    return jsonify({'message': 'Profile modified', 'user': person.serialize_info()}), 200

@web_application.route('/api/profile/avatar-upload', methods=['POST'])
@verify_session_active
def store_avatar_image():
    if 'picture' not in request.files:
        return jsonify({'error': 'No picture file'}), 400
    
    picture_file = request.files['picture']
    person = PersonEntity.query.get(session['user_id'])
    
    avatar_path = persist_uploaded_asset(picture_file, 'profiles')
    person.profile_picture = avatar_path
    
    storage_layer.session.commit()
    return jsonify({'message': 'Avatar updated', 'url': avatar_path}), 200

# ===== ADMIN CONTROL PANEL =====

@web_application.route('/api/admin/person-list', methods=['GET'])
@verify_role_access('admin')
def fetch_all_persons():
    persons = PersonEntity.query.all()
    return jsonify({'users': [p.serialize_info() for p in persons]}), 200

@web_application.route('/api/admin/person-remove/<int:person_id>', methods=['DELETE'])
@verify_role_access('admin')
def remove_person(person_id):
    person = PersonEntity.query.get(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    storage_layer.session.delete(person)
    storage_layer.session.commit()
    return jsonify({'message': 'Person removed'}), 200

@web_application.route('/api/admin/person-role-change/<int:person_id>', methods=['PUT'])
@verify_role_access('admin')
def modify_person_role(person_id):
    incoming_data = request.get_json()
    person = PersonEntity.query.get(person_id)
    
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    if incoming_data.get('role') in ['admin', 'teacher', 'student']:
        person.role = incoming_data['role']
        storage_layer.session.commit()
        return jsonify({'message': 'Role modified', 'user': person.serialize_info()}), 200
    
    return jsonify({'error': 'Invalid role'}), 400

@web_application.route('/api/admin/trophy-create', methods=['POST'])
@verify_role_access('admin')
def establish_trophy():
    incoming_data = request.get_json()
    
    trophy = TrophyDefinition(
        name=incoming_data['name'],
        description=incoming_data.get('description'),
        icon=incoming_data.get('icon'),
        points_required=incoming_data.get('points_required', 0)
    )
    
    storage_layer.session.add(trophy)
    storage_layer.session.commit()
    
    return jsonify({'message': 'Trophy established', 'badge': trophy.serialize_info()}), 201

@web_application.route('/api/admin/activity-create', methods=['POST'])
@verify_role_access('admin')
def establish_activity():
    incoming_data = request.get_json()
    
    activity = InteractiveActivity(
        name=incoming_data['name'],
        description=incoming_data.get('description'),
        url=incoming_data.get('url'),
        points_per_play=incoming_data.get('points_per_play', 10)
    )
    
    storage_layer.session.add(activity)
    storage_layer.session.commit()
    
    return jsonify({'message': 'Activity established', 'game': activity.serialize_info()}), 201

# ===== LEARNING MODULE MANAGEMENT =====

@web_application.route('/api/modules/list', methods=['GET'])
@verify_session_active
def retrieve_modules():
    person = PersonEntity.query.get(session['user_id'])
    
    if person.role == 'admin':
        modules = LearningModule.query.all()
    elif person.role == 'teacher':
        modules = LearningModule.query.filter_by(teacher_id=person.user_id).all()
    else:
        memberships = ClassMembership.query.filter_by(user_id=person.user_id).all()
        modules = [m.learning_module for m in memberships]
    
    return jsonify({'courses': [m.serialize_info() for m in modules]}), 200

@web_application.route('/api/modules/establish', methods=['POST'])
@verify_role_access('admin', 'teacher')
def establish_module():
    incoming_data = request.get_json()
    person = PersonEntity.query.get(session['user_id'])
    
    module = LearningModule(
        course_name=incoming_data['course_name'],
        description=incoming_data.get('description'),
        teacher_id=incoming_data.get('teacher_id') if person.role == 'admin' else person.user_id
    )
    
    storage_layer.session.add(module)
    storage_layer.session.commit()
    
    return jsonify({'message': 'Module established', 'course': module.serialize_info()}), 201

@web_application.route('/api/modules/details/<int:module_id>', methods=['GET'])
@verify_session_active
def retrieve_module_details(module_id):
    module = LearningModule.query.get(module_id)
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    return jsonify({'course': module.serialize_info()}), 200

@web_application.route('/api/modules/join/<int:module_id>', methods=['POST'])
@verify_role_access('student')
def join_module(module_id):
    person_id = session['user_id']
    
    existing_membership = ClassMembership.query.filter_by(
        user_id=person_id,
        course_id=module_id
    ).first()
    
    if existing_membership:
        return jsonify({'error': 'Already joined'}), 409
    
    membership = ClassMembership(user_id=person_id, course_id=module_id)
    storage_layer.session.add(membership)
    storage_layer.session.commit()
    
    return jsonify({'message': 'Joined successfully'}), 201

@web_application.route('/api/modules/roster/<int:module_id>', methods=['GET'])
@verify_role_access('teacher', 'admin')
def retrieve_module_roster(module_id):
    memberships = ClassMembership.query.filter_by(course_id=module_id).all()
    roster = [PersonEntity.query.get(m.user_id).serialize_info() for m in memberships]
    return jsonify({'students': roster}), 200

# ===== RESOURCE MANAGEMENT =====

@web_application.route('/api/modules/<int:module_id>/resources', methods=['GET'])
@verify_session_active
def retrieve_resources(module_id):
    resources = ResourceDocument.query.filter_by(course_id=module_id).all()
    return jsonify({'materials': [r.serialize_info() for r in resources]}), 200

@web_application.route('/api/modules/<int:module_id>/resource-upload', methods=['POST'])
@verify_role_access('teacher', 'admin')
def upload_resource(module_id):
    form_data = request.form
    
    resource = ResourceDocument(
        course_id=module_id,
        title=form_data['title'],
        content=form_data.get('content'),
        created_by=session['user_id']
    )
    
    if 'file' in request.files:
        asset_file = request.files['file']
        resource.file_url = persist_uploaded_asset(asset_file, 'coursework')
    
    storage_layer.session.add(resource)
    storage_layer.session.commit()
    
    return jsonify({'message': 'Resource uploaded', 'material': resource.serialize_info()}), 201

# ===== TASK MANAGEMENT =====

@web_application.route('/api/modules/<int:module_id>/tasks', methods=['GET'])
@verify_session_active
def retrieve_tasks(module_id):
    tasks = TaskItem.query.filter_by(course_id=module_id).all()
    return jsonify({'assignments': [t.serialize_info() for t in tasks]}), 200

@web_application.route('/api/modules/<int:module_id>/task-create', methods=['POST'])
@verify_role_access('teacher', 'admin')
def establish_task(module_id):
    incoming_data = request.get_json()
    
    try:
        due_date_obj = datetime.fromisoformat(incoming_data['due_date']) if incoming_data.get('due_date') else None
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    task = TaskItem(
        course_id=module_id,
        title=incoming_data['title'],
        description=incoming_data.get('description'),
        due_date=due_date_obj,
        points=incoming_data.get('points', 0),
        created_by=session['user_id']
    )
    
    storage_layer.session.add(task)
    storage_layer.session.commit()
    
    return jsonify({'message': 'Task established', 'assignment': task.serialize_info()}), 201

@web_application.route('/api/tasks/<int:task_id>/deliver', methods=['POST'])
@verify_role_access('student')
def deliver_task_work(task_id):
    form_data = request.form
    
    existing_work = WorkSubmission.query.filter_by(
        assignment_id=task_id,
        student_id=session['user_id']
    ).first()
    
    if existing_work:
        return jsonify({'error': 'Already delivered'}), 409
    
    work = WorkSubmission(
        assignment_id=task_id,
        student_id=session['user_id'],
        content=form_data.get('content')
    )
    
    if 'file' in request.files:
        asset_file = request.files['file']
        work.file_url = persist_uploaded_asset(asset_file, 'submissions')
    
    storage_layer.session.add(work)
    
    person = PersonEntity.query.get(session['user_id'])
    person.points += 10
    
    storage_layer.session.commit()
    
    return jsonify({'message': 'Work delivered', 'submission': work.serialize_info()}), 201

@web_application.route('/api/tasks/<int:task_id>/responses', methods=['GET'])
@verify_role_access('teacher', 'admin')
def retrieve_task_responses(task_id):
    responses = WorkSubmission.query.filter_by(assignment_id=task_id).all()
    response_list = []
    for resp in responses:
        learner = PersonEntity.query.get(resp.student_id)
        resp_dict = resp.serialize_info()
        resp_dict['student_name'] = learner.username
        response_list.append(resp_dict)
    return jsonify({'submissions': response_list}), 200

@web_application.route('/api/responses/<int:response_id>/evaluate', methods=['PUT'])
@verify_role_access('teacher', 'admin')
def evaluate_response(response_id):
    incoming_data = request.get_json()
    
    response = WorkSubmission.query.get(response_id)
    if not response:
        return jsonify({'error': 'Response not found'}), 404
    
    response.grade = incoming_data.get('grade')
    response.feedback = incoming_data.get('feedback')
    response.graded_by = session['user_id']
    response.graded_at = datetime.utcnow()
    
    if incoming_data.get('grade'):
        learner = PersonEntity.query.get(response.student_id)
        learner.points += incoming_data['grade']
    
    storage_layer.session.commit()
    
    return jsonify({'message': 'Response evaluated', 'submission': response.serialize_info()}), 200

# ===== GAMIFICATION FEATURES =====

@web_application.route('/api/rankings/top-performers', methods=['GET'])
@verify_session_active
def fetch_top_performers():
    performers = PersonEntity.query.filter_by(role='student').order_by(PersonEntity.points.desc()).limit(50).all()
    rankings = [
        {
            'rank': position + 1,
            'username': perf.username,
            'points': perf.points,
            'profile_picture': perf.profile_picture
        }
        for position, perf in enumerate(performers)
    ]
    return jsonify({'leaderboard': rankings}), 200

@web_application.route('/api/trophies/catalog', methods=['GET'])
@verify_session_active
def fetch_trophy_catalog():
    trophies = TrophyDefinition.query.all()
    return jsonify({'badges': [t.serialize_info() for t in trophies]}), 200

@web_application.route('/api/trophies/mine', methods=['GET'])
@verify_session_active
def fetch_personal_trophies():
    ownerships = TrophyOwnership.query.filter_by(user_id=session['user_id']).all()
    trophy_list = []
    for ownership in ownerships:
        trophy = TrophyDefinition.query.get(ownership.badge_id)
        trophy_dict = trophy.serialize_info()
        trophy_dict['earned_at'] = ownership.earned_at.isoformat()
        trophy_list.append(trophy_dict)
    return jsonify({'badges': trophy_list}), 200

@web_application.route('/api/milestones/mine', methods=['GET'])
@verify_session_active
def fetch_personal_milestones():
    milestones = MilestoneRecord.query.filter_by(user_id=session['user_id']).all()
    return jsonify({'achievements': [m.serialize_info() for m in milestones]}), 200

@web_application.route('/api/activities/catalog', methods=['GET'])
@verify_session_active
def fetch_activity_catalog():
    activities = InteractiveActivity.query.all()
    return jsonify({'games': [a.serialize_info() for a in activities]}), 200

@web_application.route('/api/activities/<int:activity_id>/participate', methods=['POST'])
@verify_role_access('student')
def record_participation(activity_id):
    incoming_data = request.get_json()
    
    activity = InteractiveActivity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    play_record = PlaySession(
        game_id=activity_id,
        user_id=session['user_id'],
        score=incoming_data.get('score', 0)
    )
    
    person = PersonEntity.query.get(session['user_id'])
    person.points += activity.points_per_play
    
    storage_layer.session.add(play_record)
    storage_layer.session.commit()
    
    evaluate_trophy_eligibility(person)
    
    return jsonify({'message': 'Participation recorded', 'points_earned': activity.points_per_play}), 201

@web_application.route('/api/activities/<int:activity_id>/records', methods=['GET'])
@verify_session_active
def fetch_activity_records(activity_id):
    records = PlaySession.query.filter_by(game_id=activity_id).order_by(
        PlaySession.score.desc()
    ).limit(10).all()
    
    record_list = []
    for rec in records:
        participant = PersonEntity.query.get(rec.user_id)
        record_list.append({
            'username': participant.username,
            'score': rec.score,
            'played_at': rec.played_at.isoformat()
        })
    
    return jsonify({'highscores': record_list}), 200

def evaluate_trophy_eligibility(person):
    trophies = TrophyDefinition.query.all()
    for trophy in trophies:
        if person.points >= trophy.points_required:
            existing_ownership = TrophyOwnership.query.filter_by(
                user_id=person.user_id,
                badge_id=trophy.badge_id
            ).first()
            
            if not existing_ownership:
                ownership = TrophyOwnership(user_id=person.user_id, badge_id=trophy.badge_id)
                storage_layer.session.add(ownership)
    
    storage_layer.session.commit()

# ===== FILE DELIVERY =====

@web_application.route('/uploads/<path:asset_path>')
def deliver_asset(asset_path):
    return send_from_directory(web_application.config['FILE_STORAGE_PATH'], asset_path)
