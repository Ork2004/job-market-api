"""create vacancies and skills

Revision ID: 8a722816a155
Revises:
Create Date: 2026-08-20 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a722816a155"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("name", name="uq_skills_name"),
    )
    op.create_index(op.f("ix_skills_name"), "skills", ["name"])

    op.create_table(
        "vacancies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("employment_type", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("source", "external_id", name="uq_vacancies_source_external_id"),
    )
    op.create_index(op.f("ix_vacancies_external_id"), "vacancies", ["external_id"])
    op.create_index(op.f("ix_vacancies_source"), "vacancies", ["source"])

    op.create_table(
        "vacancy_skills",
        sa.Column(
            "vacancy_id",
            sa.Integer(),
            sa.ForeignKey("vacancies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "skill_id",
            sa.Integer(),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("vacancy_skills")
    op.drop_index(op.f("ix_vacancies_source"), table_name="vacancies")
    op.drop_index(op.f("ix_vacancies_external_id"), table_name="vacancies")
    op.drop_table("vacancies")
    op.drop_index(op.f("ix_skills_name"), table_name="skills")
    op.drop_table("skills")
