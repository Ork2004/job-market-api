from typing import Any

import pandas as pd

ALLOWED_GROUP_BY_FIELDS = {"location", "employment_type", "company"}


class InvalidGroupByField(ValueError):
    pass


def salary_stats_by(rows: list[dict[str, Any]], group_by: str) -> list[dict[str, Any]]:
    """Aggregate vacancy salary stats by `group_by`, split by currency so
    figures in different currencies never get averaged together.

    `rows` are plain dicts with at least: id, currency, salary_min,
    salary_max, and the field named by `group_by`.
    """
    if group_by not in ALLOWED_GROUP_BY_FIELDS:
        raise InvalidGroupByField(group_by)

    df = pd.DataFrame(rows)
    if df.empty:
        return []

    df = df.dropna(subset=[group_by, "currency"])
    df = df[df[["salary_min", "salary_max"]].notna().any(axis=1)]
    if df.empty:
        return []

    df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)

    grouped = (
        df.groupby([group_by, "currency"])
        .agg(
            vacancy_count=("id", "count"),
            avg_salary=("salary_avg", "mean"),
            min_salary=("salary_min", "min"),
            max_salary=("salary_max", "max"),
        )
        .reset_index()
        .sort_values("vacancy_count", ascending=False)
    )

    return [
        {
            "group": row[group_by],
            "currency": row["currency"],
            "vacancy_count": int(row["vacancy_count"]),
            "avg_salary": round(float(row["avg_salary"]), 2),
            "min_salary": float(row["min_salary"]) if pd.notna(row["min_salary"]) else None,
            "max_salary": float(row["max_salary"]) if pd.notna(row["max_salary"]) else None,
        }
        for _, row in grouped.iterrows()
    ]
