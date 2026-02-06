from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

storage_layer = SQLAlchemy()

class PersonEntity(storage_layer.Model):
    __tablename__ = 'users'
    
    user_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    username = storage_layer.Column(storage_layer.String(50), unique=True, nullable=False)
    email = storage_layer.Column(storage_layer.String(100), unique=True, nullable=False)
    password_hash = storage_layer.Column(storage_layer.String(255), nullable=False)
    role = storage_layer.Column(storage_layer.Enum('admin', 'teacher', 'student'), nullable=False)
    profile_picture = storage_layer.Column(storage_layer.String(255))
    points = storage_layer.Column(storage_layer.Integer, default=0)
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    class_memberships = storage_layer.relationship('ClassMembership', back_populates='enrolled_person', lazy=True)
    teaching_classes = storage_layer.relationship('LearningModule', back_populates='lead_educator', lazy=True)
    work_submissions = storage_layer.relationship('WorkSubmission', foreign_keys='WorkSubmission.student_id', back_populates='submitting_person', lazy=True)
    graded_works = storage_layer.relationship('WorkSubmission', foreign_keys='WorkSubmission.graded_by', lazy=True)
    trophy_collection = storage_layer.relationship('TrophyOwnership', back_populates='trophy_holder', lazy=True)
    milestones = storage_layer.relationship('MilestoneRecord', back_populates='milestone_owner', lazy=True)
    play_history = storage_layer.relationship('PlaySession', back_populates='participant', lazy=True)
    
    def encode_credential(self, raw_credential):
        salt_bytes = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(raw_credential.encode('utf-8'), salt_bytes)
        self.password_hash = hashed_bytes.decode('utf-8')
    
    def authenticate_credential(self, raw_credential):
        return bcrypt.checkpw(raw_credential.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def serialize_info(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'profile_picture': self.profile_picture,
            'points': self.points,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CredentialResetTicket(storage_layer.Model):
    __tablename__ = 'password_reset_tokens'
    
    token_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    user_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token = storage_layer.Column(storage_layer.String(255), unique=True, nullable=False)
    expires_at = storage_layer.Column(storage_layer.DateTime, nullable=False)
    used = storage_layer.Column(storage_layer.Boolean, default=False)
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)


class LearningModule(storage_layer.Model):
    __tablename__ = 'courses'
    
    course_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    course_name = storage_layer.Column(storage_layer.String(100), nullable=False)
    description = storage_layer.Column(storage_layer.Text)
    teacher_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    lead_educator = storage_layer.relationship('PersonEntity', back_populates='teaching_classes')
    class_roster = storage_layer.relationship('ClassMembership', back_populates='learning_module', lazy=True)
    resource_library = storage_layer.relationship('ResourceDocument', back_populates='owning_module', lazy=True)
    task_collection = storage_layer.relationship('TaskItem', back_populates='owning_module', lazy=True)
    
    def serialize_info(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ClassMembership(storage_layer.Model):
    __tablename__ = 'enrollments'
    
    enrollment_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    user_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    course_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    enrollment_date = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    enrolled_person = storage_layer.relationship('PersonEntity', back_populates='class_memberships')
    learning_module = storage_layer.relationship('LearningModule', back_populates='class_roster')


class ResourceDocument(storage_layer.Model):
    __tablename__ = 'coursework'
    
    coursework_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    course_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    title = storage_layer.Column(storage_layer.String(200), nullable=False)
    content = storage_layer.Column(storage_layer.Text)
    file_url = storage_layer.Column(storage_layer.String(255))
    created_by = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    owning_module = storage_layer.relationship('LearningModule', back_populates='resource_library')
    
    def serialize_info(self):
        return {
            'coursework_id': self.coursework_id,
            'course_id': self.course_id,
            'title': self.title,
            'content': self.content,
            'file_url': self.file_url,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TaskItem(storage_layer.Model):
    __tablename__ = 'assignments'
    
    assignment_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    course_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    title = storage_layer.Column(storage_layer.String(200), nullable=False)
    description = storage_layer.Column(storage_layer.Text)
    due_date = storage_layer.Column(storage_layer.DateTime)
    points = storage_layer.Column(storage_layer.Integer, default=0)
    created_by = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    owning_module = storage_layer.relationship('LearningModule', back_populates='task_collection')
    response_collection = storage_layer.relationship('WorkSubmission', back_populates='related_task', lazy=True)
    
    def serialize_info(self):
        return {
            'assignment_id': self.assignment_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'points': self.points,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkSubmission(storage_layer.Model):
    __tablename__ = 'submissions'
    
    submission_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    assignment_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('assignments.assignment_id', ondelete='CASCADE'), nullable=False)
    student_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = storage_layer.Column(storage_layer.Text)
    file_url = storage_layer.Column(storage_layer.String(255))
    submitted_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    grade = storage_layer.Column(storage_layer.Integer)
    feedback = storage_layer.Column(storage_layer.Text)
    graded_by = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='SET NULL'))
    graded_at = storage_layer.Column(storage_layer.DateTime)
    
    related_task = storage_layer.relationship('TaskItem', back_populates='response_collection')
    submitting_person = storage_layer.relationship('PersonEntity', foreign_keys=[student_id], back_populates='work_submissions')
    
    def serialize_info(self):
        return {
            'submission_id': self.submission_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'content': self.content,
            'file_url': self.file_url,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'grade': self.grade,
            'feedback': self.feedback,
            'graded_by': self.graded_by,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None
        }


class TrophyDefinition(storage_layer.Model):
    __tablename__ = 'badges'
    
    badge_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    name = storage_layer.Column(storage_layer.String(100), nullable=False)
    description = storage_layer.Column(storage_layer.Text)
    icon = storage_layer.Column(storage_layer.String(255))
    points_required = storage_layer.Column(storage_layer.Integer, default=0)
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    ownership_links = storage_layer.relationship('TrophyOwnership', back_populates='trophy_definition', lazy=True)
    
    def serialize_info(self):
        return {
            'badge_id': self.badge_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'points_required': self.points_required,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TrophyOwnership(storage_layer.Model):
    __tablename__ = 'user_badges'
    
    user_badge_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    user_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    badge_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('badges.badge_id', ondelete='CASCADE'), nullable=False)
    earned_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    trophy_holder = storage_layer.relationship('PersonEntity', back_populates='trophy_collection')
    trophy_definition = storage_layer.relationship('TrophyDefinition', back_populates='ownership_links')


class MilestoneRecord(storage_layer.Model):
    __tablename__ = 'achievements'
    
    achievement_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    user_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    title = storage_layer.Column(storage_layer.String(200), nullable=False)
    description = storage_layer.Column(storage_layer.Text)
    points = storage_layer.Column(storage_layer.Integer, default=0)
    achieved_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    milestone_owner = storage_layer.relationship('PersonEntity', back_populates='milestones')
    
    def serialize_info(self):
        return {
            'achievement_id': self.achievement_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'points': self.points,
            'achieved_at': self.achieved_at.isoformat() if self.achieved_at else None
        }


class InteractiveActivity(storage_layer.Model):
    __tablename__ = 'games'
    
    game_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    name = storage_layer.Column(storage_layer.String(100), nullable=False)
    description = storage_layer.Column(storage_layer.Text)
    url = storage_layer.Column(storage_layer.String(255))
    points_per_play = storage_layer.Column(storage_layer.Integer, default=10)
    created_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    session_history = storage_layer.relationship('PlaySession', back_populates='activity_type', lazy=True)
    
    def serialize_info(self):
        return {
            'game_id': self.game_id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'points_per_play': self.points_per_play,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PlaySession(storage_layer.Model):
    __tablename__ = 'game_scores'
    
    score_id = storage_layer.Column(storage_layer.Integer, primary_key=True, autoincrement=True)
    game_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('games.game_id', ondelete='CASCADE'), nullable=False)
    user_id = storage_layer.Column(storage_layer.Integer, storage_layer.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    score = storage_layer.Column(storage_layer.Integer, nullable=False)
    played_at = storage_layer.Column(storage_layer.DateTime, default=datetime.utcnow)
    
    activity_type = storage_layer.relationship('InteractiveActivity', back_populates='session_history')
    participant = storage_layer.relationship('PersonEntity', back_populates='play_history')
    
    def serialize_info(self):
        return {
            'score_id': self.score_id,
            'game_id': self.game_id,
            'user_id': self.user_id,
            'score': self.score,
            'played_at': self.played_at.isoformat() if self.played_at else None
        }
