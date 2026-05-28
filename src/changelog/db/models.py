from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from changelog.db.base import Base


class ChangelogFormat(str, PyEnum):
    KEEP_A_CHANGELOG = "keep_a_changelog"
    CONVENTIONAL_COMMITS = "conventional_commits"
    CUSTOM = "custom"


class AudienceMode(str, PyEnum):
    DEVELOPER = "developer"
    END_USER = "end_user"
    BOTH = "both"


class Installation(Base):
    __tablename__ = "installations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    github_installation_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    account_login: Mapped[str] = mapped_column(String(255), index=True)
    account_type: Mapped[str] = mapped_column(String(50))
    target_type: Mapped[str] = mapped_column(String(50))
    installed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    repositories: Mapped[list[Repository]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    github_repo_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(500), index=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    private: Mapped[bool] = mapped_column(default=False)
    format: Mapped[ChangelogFormat] = mapped_column(
        Enum(ChangelogFormat), default=ChangelogFormat.KEEP_A_CHANGELOG
    )
    audience: Mapped[AudienceMode] = mapped_column(
        Enum(AudienceMode), default=AudienceMode.DEVELOPER
    )
    installation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("installations.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    installation: Mapped[Installation] = relationship(back_populates="repositories")
    changelogs: Mapped[list[Changelog]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )


class Changelog(Base):
    __tablename__ = "changelogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(100), index=True)
    tag: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    format: Mapped[ChangelogFormat] = mapped_column(Enum(ChangelogFormat))
    audience: Mapped[AudienceMode] = mapped_column(Enum(AudienceMode))
    content: Mapped[str] = mapped_column(Text)
    commit_count: Mapped[int] = mapped_column(Integer, default=0)
    pr_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="generated")
    repository_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id"), index=True
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    repository: Mapped[Repository] = relationship(back_populates="changelogs")
