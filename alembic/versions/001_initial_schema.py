"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "installations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("github_installation_id", sa.Integer(), nullable=False),
        sa.Column("account_login", sa.String(length=255), nullable=False),
        sa.Column("account_type", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("installed_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_installation_id"),
    )
    op.create_index(op.f("ix_installations_account_login"), "installations", ["account_login"])

    op.create_table(
        "repositories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("github_repo_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=500), nullable=False),
        sa.Column("default_branch", sa.String(length=100), nullable=False),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column(
            "format",
            sa.Enum("keep_a_changelog", "conventional_commits", "custom", name="changelogformat"),
            nullable=False,
        ),
        sa.Column(
            "audience",
            sa.Enum("developer", "end_user", "both", name="audiencemode"),
            nullable=False,
        ),
        sa.Column("installation_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["installation_id"], ["installations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_repo_id"),
    )
    op.create_index(op.f("ix_repositories_full_name"), "repositories", ["full_name"])
    op.create_index(op.f("ix_repositories_installation_id"), "repositories", ["installation_id"])

    op.create_table(
        "changelogs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column("tag", sa.String(length=255), nullable=True),
        sa.Column(
            "format",
            sa.Enum("keep_a_changelog", "conventional_commits", "custom", name="changelogformat"),
            nullable=False,
        ),
        sa.Column(
            "audience",
            sa.Enum("developer", "end_user", "both", name="audiencemode"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("commit_count", sa.Integer(), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_changelogs_repository_id"), "changelogs", ["repository_id"])
    op.create_index(op.f("ix_changelogs_version"), "changelogs", ["version"])


def downgrade() -> None:
    op.drop_index(op.f("ix_changelogs_version"), table_name="changelogs")
    op.drop_index(op.f("ix_changelogs_repository_id"), table_name="changelogs")
    op.drop_table("changelogs")
    op.drop_index(op.f("ix_repositories_installation_id"), table_name="repositories")
    op.drop_index(op.f("ix_repositories_full_name"), table_name="repositories")
    op.drop_table("repositories")
    op.drop_index(op.f("ix_installations_account_login"), table_name="installations")
    op.drop_table("installations")
