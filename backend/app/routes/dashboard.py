from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..database import engine

import pandas as pd
import numpy as np
import re
import json


router = APIRouter()


# =========================================================
# BASIC HELPERS
# =========================================================

def normalize_column_name(column) -> str:
    name = str(column).strip().lower()

    name = re.sub(
        r"[^a-z0-9]+",
        "_",
        name
    )

    name = re.sub(
        r"_+",
        "_",
        name
    )

    return name.strip("_")


def display_name(column) -> str:
    return (
        str(column)
        .replace("_", " ")
        .strip()
        .title()
    )


def quote_identifier(name: str) -> str:
    if not name or not re.match(
        r"^[A-Za-z0-9_]+$",
        str(name)
    ):
        raise ValueError(
            f"Invalid SQL identifier: {name}"
        )

    return f"`{name}`"


# =========================================================
# NUMERIC CLEANING
# =========================================================

def clean_numeric_series(series: pd.Series) -> pd.Series:

    cleaned = (
        series
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace("%", "", regex=False)
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    )


# =========================================================
# IDENTIFIER DETECTION
# =========================================================

def is_identifier_column(
    column,
    df: pd.DataFrame
) -> bool:

    name = normalize_column_name(column)

    identifier_names = {
        "id",
        "sno",
        "s_no",
        "serial",
        "serial_no",
        "serial_number",
        "index",
        "row_number",
        "row_no",
        "record_id",
        "student_id",
        "employee_id",
        "customer_id",
        "product_id",
        "order_id"
    }

    # Explicit identifier names
    if name in identifier_names:
        return True

    if name.endswith("_id"):
        return True

    if (
        name.startswith("s_no")
        or
        name.startswith("serial")
    ):
        return True

    # Detect sequential numeric columns
    try:

        values = (
            clean_numeric_series(
                df[column]
            )
            .dropna()
        )

        if len(values) >= 10:

            unique_count = values.nunique()

            if (
                values.min() <= 1
                and
                unique_count >= len(df) * 0.90
                and
                values.max() >= len(df) * 0.90
            ):
                return True

    except Exception:
        pass

    return False


# =========================================================
# NUMERIC COLUMN DETECTION
# =========================================================

def get_numeric_columns(df):

    numeric_columns = []

    for column in df.columns:

        if is_identifier_column(
            column,
            df
        ):
            continue

        converted = clean_numeric_series(
            df[column]
        )

        if len(df) == 0:
            continue

        valid_ratio = (
            converted.notna().mean()
        )

        if (
            valid_ratio >= 0.60
            and
            converted.notna().sum() >= 3
        ):
            numeric_columns.append(column)

    return numeric_columns


# =========================================================
# CATEGORY COLUMN DETECTION
# =========================================================

def get_category_columns(df):

    category_columns = []

    for column in df.columns:

        if is_identifier_column(
            column,
            df
        ):
            continue

        series = df[column]

        # Already a datetime column
        if pd.api.types.is_datetime64_any_dtype(
            series
        ):
            continue

        # Do not classify numeric data as category
        converted = clean_numeric_series(
            series
        )

        if (
            len(series) > 0
            and
            converted.notna().mean() >= 0.60
        ):
            continue

        unique_count = (
            series
            .dropna()
            .astype(str)
            .nunique()
        )

        # Useful categorical columns
        if 2 <= unique_count <= 100:
            category_columns.append(column)

    return category_columns


# =========================================================
# DATE DETECTION
# =========================================================

def find_date_column(df):

    # -----------------------------------------------------
    # 1. Date/time column names
    # -----------------------------------------------------

    date_keywords = [
        "date",
        "time",
        "timestamp",
        "created_at",
        "updated_at",
        "dob"
    ]

    for column in df.columns:

        if is_identifier_column(
            column,
            df
        ):
            continue

        name = normalize_column_name(
            column
        )

        if any(
            keyword in name
            for keyword in date_keywords
        ):

            try:

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                if (
                    converted.notna().mean()
                    >= 0.60
                ):
                    return column

            except Exception:
                pass

    # -----------------------------------------------------
    # 2. Existing datetime columns
    # -----------------------------------------------------

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            return column

    # -----------------------------------------------------
    # 3. Conservative automatic detection
    # -----------------------------------------------------

    for column in df.columns:

        if is_identifier_column(
            column,
            df
        ):
            continue

        if pd.api.types.is_numeric_dtype(
            df[column]
        ):
            continue

        try:

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            if (
                converted.notna().mean()
                >= 0.85
                and
                converted.nunique()
                >= 3
            ):
                return column

        except Exception:
            pass

    return None


# =========================================================
# FIND BUSINESS COLUMN
# =========================================================

def find_column(
    columns,
    keywords
):

    normalized = {
        column:
            normalize_column_name(column)
        for column in columns
    }

    for keyword in keywords:

        keyword_normalized = (
            normalize_column_name(
                keyword
            )
        )

        for original, name in normalized.items():

            if (
                name == keyword_normalized
                or
                keyword_normalized in name
            ):
                return original

    return None


# =========================================================
# DATABASE
# =========================================================

def get_dataset(dataset_id=None):

    if dataset_id is not None:

        query = text("""
            SELECT
                dataset_id,
                dataset_name,
                original_filename,
                table_name,
                row_count,
                column_count
            FROM datasets
            WHERE dataset_id = :dataset_id
        """)

        with engine.connect() as connection:

            return connection.execute(
                query,
                {
                    "dataset_id": dataset_id
                }
            ).mappings().first()

    query = text("""
        SELECT
            dataset_id,
            dataset_name,
            original_filename,
            table_name,
            row_count,
            column_count
        FROM datasets
        ORDER BY dataset_id DESC
        LIMIT 1
    """)

    with engine.connect() as connection:

        return connection.execute(
            query
        ).mappings().first()


def load_dataframe(table_name):

    safe_table = quote_identifier(
        table_name
    )

    query = text(
        f"SELECT * FROM {safe_table}"
    )

    with engine.connect() as connection:

        return pd.read_sql(
            query,
            connection
        )


# =========================================================
# APPLY DASHBOARD FILTERS
# =========================================================

def apply_dashboard_filters(
    df,
    filters,
    date_column=None
):

    if not filters:
        return df

    filtered = df.copy()

    # -----------------------------------------------------
    # CATEGORY / TEXT FILTERS
    # -----------------------------------------------------

    for column, selected_value in filters.items():

        # Skip date filters
        if column in [
            "date_from",
            "date_to"
        ]:
            continue

        if column not in filtered.columns:
            continue

        if (
            selected_value is None
            or str(selected_value).strip() == ""
            or str(selected_value).lower() == "all"
        ):
            continue

        selected_value = str(
            selected_value
        ).strip()

        filtered = filtered[
            filtered[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .eq(selected_value)
        ]

    # -----------------------------------------------------
    # DATE FROM
    # -----------------------------------------------------

    if (
        date_column
        and
        filters.get("date_from")
    ):

        dates = pd.to_datetime(
            filtered[date_column],
            errors="coerce"
        )

        from_date = pd.to_datetime(
            filters["date_from"],
            errors="coerce"
        )

        if not pd.isna(from_date):

            filtered = filtered[
                dates >= from_date
            ]

    # -----------------------------------------------------
    # DATE TO
    # -----------------------------------------------------

    if (
        date_column
        and
        filters.get("date_to")
    ):

        dates = pd.to_datetime(
            filtered[date_column],
            errors="coerce"
        )

        to_date = pd.to_datetime(
            filters["date_to"],
            errors="coerce"
        )

        if not pd.isna(to_date):

            # Include the complete selected day
            to_date = (
                to_date
                + pd.Timedelta(days=1)
            )

            filtered = filtered[
                dates < to_date
            ]

    return filtered


# =========================================================
# KPI GENERATION
# =========================================================

def generate_kpis(
    df,
    numeric_columns,
    category_columns
):

    kpis = [

        {
            "title": "Total Records",
            "value": int(len(df)),
            "column": "Rows",
            "format": "number"
        },

        {
            "title": "Total Columns",
            "value": int(len(df.columns)),
            "column": "Columns",
            "format": "number"
        },

        {
            "title": "Numeric Columns",
            "value": int(len(numeric_columns)),
            "column": "Numeric Data",
            "format": "number"
        },

        {
            "title": "Category Columns",
            "value": int(len(category_columns)),
            "column": "Text / Category Data",
            "format": "number"
        }
    ]

    business_keywords = {
        "sales": "sum",
        "revenue": "sum",
        "profit": "sum",
        "amount": "sum",
        "income": "sum",
        "cost": "sum",
        "expense": "sum",
        "quantity": "sum",
        "qty": "sum",
        "price": "average",
        "salary": "average",
        "discount": "average"
    }

    used = set()

    for column in numeric_columns:

        name = normalize_column_name(
            column
        )

        keyword = next(
            (
                key
                for key in business_keywords
                if key in name
            ),
            None
        )

        if (
            not keyword
            or
            column in used
        ):
            continue

        values = (
            clean_numeric_series(
                df[column]
            )
            .dropna()
        )

        if values.empty:
            continue

        aggregation = (
            business_keywords[keyword]
        )

        if aggregation == "average":
            value = values.mean()
        else:
            value = values.sum()

        title_suffix = (
            "Avg"
            if aggregation == "average"
            else "Total"
        )

        kpis.append({

            "title":
                f"{display_name(column)} "
                f"({title_suffix})",

            "value":
                round(
                    float(value),
                    2
                ),

            "column":
                column,

            "format":
                "decimal"
        })

        used.add(column)

        if len(kpis) >= 6:
            break

    return kpis[:6]


# =========================================================
# CATEGORY DISTRIBUTION
# =========================================================

def category_distribution(
    df,
    column,
    limit=10
):

    series = (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    series = series.replace(
        "",
        "Unknown"
    )

    counts = (
        series
        .value_counts()
        .head(limit)
    )

    return [

        {
            "x": str(label),
            "y": int(value)
        }

        for label, value
        in counts.items()
    ]


# =========================================================
# CATEGORY CHART
# =========================================================

def create_category_chart(
    df,
    column
):

    data = category_distribution(
        df,
        column,
        10
    )

    if len(data) < 2:
        return None

    unique_count = (
        df[column]
        .dropna()
        .astype(str)
        .nunique()
    )

    # Few categories → doughnut
    if unique_count <= 5:

        chart_type = "doughnut"

    # Many categories → horizontal bar
    else:

        chart_type = "horizontalBar"

    return {

        "type":
            chart_type,

        "title":
            f"{display_name(column)} Distribution",

        "x":
            column,

        "y":
            "count",

        "data":
            data,

        "description":
            f"Distribution of "
            f"{display_name(column)}."
    }


# =========================================================
# CATEGORY + NUMERIC AGGREGATION
# =========================================================

def aggregate_category_numeric(
    df,
    category_column,
    numeric_column,
    limit=10
):

    work = pd.DataFrame({

        "category":
            df[category_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip(),

        "value":
            clean_numeric_series(
                df[numeric_column]
            )

    })

    work["category"] = (
        work["category"]
        .replace(
            "",
            "Unknown"
        )
    )

    work = work.dropna(
        subset=["value"]
    )

    if work.empty:
        return []

    grouped = (
        work
        .groupby(
            "category",
            as_index=False
        )["value"]
        .sum()
        .sort_values(
            "value",
            ascending=False
        )
        .head(limit)
    )

    return [

        {
            "x":
                str(row.category),

            "y":
                round(
                    float(row.value),
                    4
                )
        }

        for row
        in grouped.itertuples()
    ]


# =========================================================
# CATEGORY + NUMERIC CHART
# =========================================================

def create_category_numeric_chart(
    df,
    category_column,
    numeric_column
):

    data = aggregate_category_numeric(
        df,
        category_column,
        numeric_column
    )

    if len(data) < 2:
        return None

    unique_count = (
        df[category_column]
        .dropna()
        .astype(str)
        .nunique()
    )

    # Only use doughnut when there are
    # very few categories and values are positive.
    if (
        unique_count <= 5
        and
        all(
            row["y"] >= 0
            for row in data
        )
    ):

        chart_type = "doughnut"

    else:

        chart_type = "horizontalBar"

    return {

        "type":
            chart_type,

        "title":
            f"{display_name(numeric_column)} "
            f"by "
            f"{display_name(category_column)}",

        "x":
            category_column,

        "y":
            numeric_column,

        "data":
            data,

        "description":
            f"{display_name(numeric_column)} "
            f"aggregated by "
            f"{display_name(category_column)}."
    }


# =========================================================
# DATE + NUMERIC LINE CHART
# =========================================================

def create_date_chart(
    df,
    date_column,
    numeric_column
):

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    values = clean_numeric_series(
        df[numeric_column]
    )

    work = pd.DataFrame({

        "date": dates,
        "value": values

    }).dropna()

    if (
        len(work) < 3
        or
        work["date"].nunique() < 2
    ):
        return None

    span_days = max(
        (
            work["date"].max()
            -
            work["date"].min()
        ).days,
        1
    )

    # More than 3 years → yearly
    if span_days > 365 * 3:

        work["period"] = (
            work["date"]
            .dt
            .to_period("Y")
            .dt
            .to_timestamp()
        )

    # More than 3 months → monthly
    elif span_days > 90:

        work["period"] = (
            work["date"]
            .dt
            .to_period("M")
            .dt
            .to_timestamp()
        )

    # Otherwise → daily
    else:

        work["period"] = (
            work["date"]
            .dt
            .to_period("D")
            .dt
            .to_timestamp()
        )

    grouped = (
        work
        .groupby(
            "period",
            as_index=False
        )["value"]
        .sum()
        .sort_values(
            "period"
        )
    )

    data = [

        {
            "x":
                row.period.strftime(
                    "%Y-%m-%d"
                ),

            "y":
                round(
                    float(row.value),
                    4
                )
        }

        for row
        in grouped.itertuples()
    ]

    if len(data) < 2:
        return None

    return {

        "type":
            "line",

        "title":
            f"{display_name(numeric_column)} Trend",

        "x":
            date_column,

        "y":
            numeric_column,

        "data":
            data,

        "description":
            f"{display_name(numeric_column)} over time."
    }


# =========================================================
# HISTOGRAM
# =========================================================

def create_histogram(
    df,
    column,
    bins=10
):

    values = (
        clean_numeric_series(
            df[column]
        )
        .dropna()
    )

    if (
        len(values) < 5
        or
        values.nunique() <= 1
    ):
        return None

    bin_count = min(
        bins,
        max(
            5,
            min(
                15,
                values.nunique()
            )
        )
    )

    counts, edges = np.histogram(
        values,
        bins=bin_count
    )

    data = []

    for i, count in enumerate(
        counts
    ):

        data.append({

            "x":
                f"{edges[i]:,.1f}"
                f" – "
                f"{edges[i + 1]:,.1f}",

            "y":
                int(count)
        })

    return {

        "type":
            "histogram",

        "title":
            f"{display_name(column)} "
            f"Distribution",

        "x":
            column,

        "y":
            "count",

        "data":
            data,

        "description":
            f"Distribution of "
            f"{display_name(column)}."
    }


# =========================================================
# SCATTER CHART
# =========================================================

def create_scatter(
    df,
    x_column,
    y_column
):

    x = clean_numeric_series(
        df[x_column]
    )

    y = clean_numeric_series(
        df[y_column]
    )

    work = pd.DataFrame({

        "x": x,
        "y": y

    }).dropna()

    if len(work) < 5:
        return None

    # Avoid huge scatter charts
    if len(work) > 500:

        work = work.sample(
            500,
            random_state=42
        )

    data = [

        {
            "x":
                round(
                    float(row.x),
                    4
                ),

            "y":
                round(
                    float(row.y),
                    4
                )
        }

        for row
        in work.itertuples()
    ]

    return {

        "type":
            "scatter",

        "title":
            f"{display_name(y_column)} "
            f"vs "
            f"{display_name(x_column)}",

        "x":
            x_column,

        "y":
            y_column,

        "data":
            data,

        "description":
            f"Relationship between "
            f"{display_name(x_column)} "
            f"and "
            f"{display_name(y_column)}."
    }


# =========================================================
# AUTOMATIC CHART SELECTION
# =========================================================

def generate_charts(
    df,
    numeric_columns,
    category_columns,
    date_column
):

    charts = []
    used_keys = set()

    def add_chart(chart):

        if not chart:
            return

        key = (
            chart.get("type"),
            chart.get("x"),
            chart.get("y"),
            chart.get("title")
        )

        if key in used_keys:
            return

        if len(charts) >= 8:
            return

        charts.append(chart)
        used_keys.add(key)

    # -----------------------------------------------------
    # Business-important numeric columns first
    # -----------------------------------------------------

    business_words = [
        "sales",
        "revenue",
        "profit",
        "amount",
        "income",
        "cost",
        "expense",
        "quantity",
        "qty",
        "price",
        "salary",
        "discount"
    ]

    preferred_numeric = [

        column

        for column
        in numeric_columns

        if any(
            word in normalize_column_name(column)
            for word in business_words
        )
    ]

    ordered_numeric = (
        preferred_numeric
        +
        [
            column
            for column
            in numeric_columns
            if column not in preferred_numeric
        ]
    )

    # -----------------------------------------------------
    # 1. DATE + NUMERIC → LINE
    # -----------------------------------------------------

    if date_column:

        for numeric_column in ordered_numeric:

            chart = create_date_chart(
                df,
                date_column,
                numeric_column
            )

            if chart:

                add_chart(chart)

                break

    # -----------------------------------------------------
    # 2. CATEGORY DISTRIBUTIONS
    # -----------------------------------------------------

    for category_column in category_columns:

        chart = create_category_chart(
            df,
            category_column
        )

        add_chart(chart)

        if len(charts) >= 4:
            break

    # -----------------------------------------------------
    # 3. CATEGORY + NUMERIC
    # -----------------------------------------------------

    for category_column in category_columns:

        for numeric_column in ordered_numeric:

            chart = create_category_numeric_chart(
                df,
                category_column,
                numeric_column
            )

            add_chart(chart)

            if len(charts) >= 6:
                break

        if len(charts) >= 6:
            break

    # -----------------------------------------------------
    # 4. SCATTER
    # -----------------------------------------------------

    if len(numeric_columns) >= 2:

        scatter = create_scatter(
            df,
            numeric_columns[0],
            numeric_columns[1]
        )

        add_chart(scatter)

    # -----------------------------------------------------
    # 5. HISTOGRAM
    # -----------------------------------------------------

    for numeric_column in ordered_numeric:

        histogram = create_histogram(
            df,
            numeric_column
        )

        add_chart(histogram)

        if len(charts) >= 8:
            break

    # -----------------------------------------------------
    # 6. CATEGORY-ONLY DATASET
    # -----------------------------------------------------

    if not numeric_columns:

        # IMPORTANT:
        # Do NOT clear charts here.
        # The previous version could lose charts.
        for category_column in category_columns:

            if len(charts) >= 6:
                break

            chart = create_category_chart(
                df,
                category_column
            )

            add_chart(chart)

    return charts[:8]


# =========================================================
# DETECTED COLUMNS
# =========================================================

def build_detected_columns(
    df,
    numeric_columns,
    category_columns,
    date_column
):

    return {

        "sales":
            find_column(
                df.columns,
                [
                    "sales",
                    "sale",
                    "revenue",
                    "amount"
                ]
            ),

        "profit":
            find_column(
                df.columns,
                [
                    "profit",
                    "net_profit",
                    "gross_profit"
                ]
            ),

        "orders":
            find_column(
                df.columns,
                [
                    "order_id",
                    "orderid",
                    "order_number",
                    "order_no"
                ]
            ),

        "products":
            find_column(
                df.columns,
                [
                    "product_id",
                    "product_name",
                    "product"
                ]
            ),

        "quantity":
            find_column(
                df.columns,
                [
                    "quantity",
                    "qty",
                    "units",
                    "units_sold"
                ]
            ),

        "discount":
            find_column(
                df.columns,
                [
                    "discount",
                    "discount_percent"
                ]
            ),

        "shipping":
            find_column(
                df.columns,
                [
                    "shipping",
                    "shipping_cost",
                    "delivery_cost"
                ]
            ),

        "date":
            date_column,

        "numeric":
            [
                str(column)
                for column
                in numeric_columns
            ],

        "category":
            [
                str(column)
                for column
                in category_columns
            ]
    }


# =========================================================
# DASHBOARD API
# =========================================================

@router.get("/dashboard")
def dashboard(
    dataset_id: int | None = None,
    filters: str | None = None
):

    try:

        dataset = get_dataset(
            dataset_id
        )

        if not dataset:

            raise HTTPException(
                status_code=404,
                detail="No dataset found"
            )

        df = load_dataframe(
            dataset["table_name"]
        )

        if df.empty:

            raise HTTPException(
                status_code=404,
                detail="Dataset contains no data"
            )

        # Clean column names
        df.columns = [
            str(column).strip()
            for column
            in df.columns
        ]

        # =====================================================
        # FILTER INFORMATION
        # =====================================================

        original_df = df.copy()

        original_category_columns = (
            get_category_columns(
                original_df
            )
        )

        original_date_column = (
            find_date_column(
                original_df
            )
        )

        # =====================================================
        # READ FILTERS
        # =====================================================

        active_filters = {}

        if filters:

            try:

                active_filters = json.loads(
                    filters
                )

                if not isinstance(
                    active_filters,
                    dict
                ):

                    active_filters = {}

            except Exception:

                active_filters = {}

        # =====================================================
        # APPLY FILTERS
        # =====================================================

        df = apply_dashboard_filters(
            df,
            active_filters,
            original_date_column
        )

        # =====================================================
        # CHECK FILTERED DATA
        # =====================================================

        if df.empty:

            raise HTTPException(
                status_code=404,
                detail="No records match the selected filters"
            )

        numeric_columns = (
            get_numeric_columns(df)
        )

        category_columns = (
            get_category_columns(df)
        )

        date_column = (
            find_date_column(df)
        )

        kpis = generate_kpis(
            df,
            numeric_columns,
            category_columns
        )

        charts = generate_charts(
            df,
            numeric_columns,
            category_columns,
            date_column
        )

        detected = build_detected_columns(
            df,
            numeric_columns,
            category_columns,
            date_column
        )

        return {

           

    "filter_options": {

        "categories": {

            str(column): sorted(

                original_df[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .replace(
                    "",
                    "Unknown"
                )
                .unique()
                .tolist()

            )

            for column
            in original_category_columns
        },

        "date_column":
            original_date_column
    },

    "active_filters":
        active_filters,

    

            "dataset": {

                "dataset_id":
                    dataset["dataset_id"],

                "dataset_name":
                    dataset["dataset_name"],

                "filename":
                    dataset["original_filename"],

                "table_name":
                    dataset["table_name"],

                "rows":
                    int(len(df)),

                "columns":
                    int(len(df.columns))
            },

            "detected_columns":
                detected,

            "kpis":
                kpis,

            "charts":
                charts
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# =========================================================
# KPI API
# =========================================================

@router.get("/kpis")
def get_kpis(
    dataset_id: int | None = None
):

    try:

        dataset = get_dataset(
            dataset_id
        )

        if not dataset:

            raise HTTPException(
                status_code=404,
                detail="No dataset found"
            )

        df = load_dataframe(
            dataset["table_name"]
        )

        numeric_columns = (
            get_numeric_columns(df)
        )

        category_columns = (
            get_category_columns(df)
        )

        return {

            "dataset_id":
                dataset["dataset_id"],

            "dataset_name":
                dataset["dataset_name"],

            "filename":
                dataset["original_filename"],

            "rows":
                int(len(df)),

            "columns":
                int(len(df.columns)),

            "kpis":
                generate_kpis(
                    df,
                    numeric_columns,
                    category_columns
                )
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )