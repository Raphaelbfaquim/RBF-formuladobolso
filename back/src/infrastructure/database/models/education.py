from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz
import enum

from src.infrastructure.database.base import Base


class ContentType(str, enum.Enum):
    ARTICLE = "article"  # Artigo
    VIDEO = "video"  # Vídeo
    COURSE = "course"  # Curso
    QUIZ = "quiz"  # Quiz
    INFographic = "infographic"  # Infográfico


class EducationalContent(Base):
    __tablename__ = "educational_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    content = Column(Text, nullable=True)  # Conteúdo do artigo
    video_url = Column(String(500), nullable=True)  # URL do vídeo
    image_url = Column(String(500), nullable=True)  # URL da imagem
    duration_minutes = Column(Integer, nullable=True)  # Duração em minutos
    difficulty_level = Column(Integer, default=1, nullable=False)  # 1-5
    tags = Column(String(500), nullable=True)  # Tags separadas por vírgula
    is_active = Column(Boolean, default=True, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content_id = Column(UUID(as_uuid=True), ForeignKey("educational_content.id"), nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)  # 0-100
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="education_progress")
    content = relationship("EducationalContent", backref="user_progress")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("educational_content.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(Text, nullable=False)  # JSON com perguntas
    passing_score = Column(Integer, default=70, nullable=False)  # Pontuação mínima (%)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    content = relationship("EducationalContent", backref="quizzes")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    score = Column(Integer, nullable=False)  # Pontuação obtida (%)
    answers = Column(Text, nullable=False)  # JSON com respostas
    is_passed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", backref="quiz_attempts")
    quiz = relationship("Quiz", backref="attempts")

