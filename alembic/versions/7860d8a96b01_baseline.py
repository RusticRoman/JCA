"""baseline

Revision ID: 7860d8a96b01
Revises:
Create Date: 2026-02-19 06:33:43.565598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7860d8a96b01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('firebase_uid', sa.String(128), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255), server_default='', nullable=False),
        sa.Column('role', sa.String(20), server_default='STUDENT', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('hebrew_name', sa.String(255), nullable=True),
        sa.Column('enrollment_semester', sa.Integer(), server_default='1', nullable=False),
        sa.Column('program_year', sa.Integer(), server_default='1', nullable=False),
        sa.Column('mentor_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_mentor_id', 'users', ['mentor_id'])

    # Programs
    op.create_table(
        'programs',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('year', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Semesters
    op.create_table(
        'semesters',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('program_id', sa.Uuid(), sa.ForeignKey('programs.id'), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Subjects
    op.create_table(
        'subjects',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('semester_id', sa.Uuid(), sa.ForeignKey('semesters.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Videos
    op.create_table(
        'videos',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('subject_id', sa.Uuid(), sa.ForeignKey('subjects.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('gcs_path', sa.String(512), server_default='', nullable=False),
        sa.Column('duration_seconds', sa.Integer(), server_default='0', nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Video Progress
    op.create_table(
        'video_progress',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('video_id', sa.Uuid(), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('last_position_seconds', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_duration_seconds', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('attendance_type', sa.String(20), server_default='RECORDED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video'),
    )
    op.create_index('ix_video_progress_user_id', 'video_progress', ['user_id'])
    op.create_index('ix_video_progress_video_id', 'video_progress', ['video_id'])

    # Quizzes
    op.create_table(
        'quizzes',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('video_id', sa.Uuid(), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('passing_score', sa.Integer(), server_default='70', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Questions
    op.create_table(
        'questions',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('quiz_id', sa.Uuid(), sa.ForeignKey('quizzes.id'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('option_a', sa.String(500), nullable=False),
        sa.Column('option_b', sa.String(500), nullable=False),
        sa.Column('option_c', sa.String(500), nullable=False),
        sa.Column('option_d', sa.String(500), nullable=False),
        sa.Column('correct_option', sa.String(1), nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Quiz Attempts
    op.create_table(
        'quiz_attempts',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('quiz_id', sa.Uuid(), sa.ForeignKey('quizzes.id'), nullable=False),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_questions', sa.Integer(), server_default='0', nullable=False),
        sa.Column('passed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Answers
    op.create_table(
        'answers',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('attempt_id', sa.Uuid(), sa.ForeignKey('quiz_attempts.id'), nullable=False),
        sa.Column('question_id', sa.Uuid(), sa.ForeignKey('questions.id'), nullable=False),
        sa.Column('selected_option', sa.String(1), nullable=False),
        sa.Column('is_correct', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Beit Din Cases
    op.create_table(
        'beit_din_cases',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('student_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('rabbi_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', sa.String(20), server_default='OPEN', nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_beit_din_cases_student_id', 'beit_din_cases', ['student_id'])

    # Case Notes
    op.create_table(
        'case_notes',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('case_id', sa.Uuid(), sa.ForeignKey('beit_din_cases.id'), nullable=False),
        sa.Column('author_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Case Documents
    op.create_table(
        'case_documents',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('case_id', sa.Uuid(), sa.ForeignKey('beit_din_cases.id'), nullable=False),
        sa.Column('uploaded_by', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('gcs_path', sa.String(512), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Monthly Questionnaires
    op.create_table(
        'monthly_questionnaires',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_questionnaire_active_year_month', 'monthly_questionnaires', ['is_active', 'year', 'month'])

    # Questionnaire Fields
    op.create_table(
        'questionnaire_fields',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('questionnaire_id', sa.Uuid(), sa.ForeignKey('monthly_questionnaires.id'), nullable=False),
        sa.Column('label', sa.String(500), nullable=False),
        sa.Column('field_type', sa.String(20), server_default='TEXT', nullable=False),
        sa.Column('options', sa.Text(), server_default='', nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('required', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Questionnaire Responses
    op.create_table(
        'questionnaire_responses',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('questionnaire_id', sa.Uuid(), sa.ForeignKey('monthly_questionnaires.id'), nullable=False),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('answers', sa.Text(), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_response_questionnaire_user', 'questionnaire_responses', ['questionnaire_id', 'user_id'])

    # Resources
    op.create_table(
        'resources',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('category', sa.String(100), server_default='general', nullable=False),
        sa.Column('gcs_path', sa.String(512), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # FAQs
    op.create_table(
        'faqs',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_published', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Events
    op.create_table(
        'events',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('event_type', sa.String(20), server_default='OTHER', nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('location', sa.String(255), server_default='', nullable=False),
        sa.Column('capacity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('google_calendar_event_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Event Registrations
    op.create_table(
        'event_registrations',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('event_id', sa.Uuid(), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('event_id', 'user_id', name='uq_event_user'),
    )


def downgrade() -> None:
    op.drop_table('event_registrations')
    op.drop_table('events')
    op.drop_table('faqs')
    op.drop_table('resources')
    op.drop_table('questionnaire_responses')
    op.drop_table('questionnaire_fields')
    op.drop_table('monthly_questionnaires')
    op.drop_table('case_documents')
    op.drop_table('case_notes')
    op.drop_table('beit_din_cases')
    op.drop_table('answers')
    op.drop_table('quiz_attempts')
    op.drop_table('questions')
    op.drop_table('quizzes')
    op.drop_table('video_progress')
    op.drop_table('videos')
    op.drop_table('subjects')
    op.drop_table('semesters')
    op.drop_table('programs')
    op.drop_table('users')
