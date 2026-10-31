import pandas as pd


def profile_dataset(df):

    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),

        "columns": [],

        "numeric_columns": [],
        "categorical_columns": [],
        "date_columns": [],
        "text_columns": [],

        "suggested_kpis": [],
        "suggested_charts": []
    }

    # =========================================================
    # ANALYZE COLUMNS
    # =========================================================

    for column in df.columns:

        series = df[column]

        column_info = {
            "name": column,
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique_values": int(series.nunique())
        }

        profile["columns"].append(column_info)

        # -----------------------------------------------------
        # NUMERIC
        # -----------------------------------------------------

        if pd.api.types.is_numeric_dtype(series):

            profile["numeric_columns"].append(column)

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        elif pd.api.types.is_datetime64_any_dtype(series):

            profile["date_columns"].append(column)

        # -----------------------------------------------------
        # TEXT / CATEGORY
        # -----------------------------------------------------

        elif pd.api.types.is_object_dtype(series):

            unique_count = series.nunique()

            if unique_count <= 50:

                profile["categorical_columns"].append(column)

            else:

                profile["text_columns"].append(column)

    # =========================================================
    # KPI SUGGESTIONS
    # =========================================================

    for column in profile["numeric_columns"]:

        column_lower = column.lower()

        if any(
            word in column_lower
            for word in [
                "sales",
                "revenue",
                "amount",
                "income",
                "profit",
                "price",
                "salary",
                "cost",
                "quantity",
                "total"
            ]
        ):

            profile["suggested_kpis"].append({

                "title": column.replace("_", " ").title(),

                "column": column,

                "aggregation": "sum"
            })

    # ---------------------------------------------------------
    # FALLBACK NUMERIC KPIs
    # ---------------------------------------------------------

    if not profile["suggested_kpis"]:

        for column in profile["numeric_columns"][:4]:

            profile["suggested_kpis"].append({

                "title": column.replace("_", " ").title(),

                "column": column,

                "aggregation": "sum"
            })

    # =========================================================
    # DATE + NUMERIC CHARTS
    # =========================================================

    for date_column in profile["date_columns"]:

        for numeric_column in profile["numeric_columns"]:

            numeric_lower = numeric_column.lower()

            if any(
                word in numeric_lower
                for word in [
                    "sales",
                    "revenue",
                    "amount",
                    "profit",
                    "income",
                    "cost",
                    "quantity",
                    "price"
                ]
            ):

                profile["suggested_charts"].append({

                    "type": "line",

                    "title": (
                        f"{numeric_column.replace('_', ' ').title()} "
                        f"Trend"
                    ),

                    "x": date_column,

                    "y": numeric_column,

                    "aggregation": "sum"
                })

    # =========================================================
    # CATEGORY + NUMERIC
    # =========================================================

    for category_column in profile["categorical_columns"]:

        for numeric_column in profile["numeric_columns"]:

            if len(profile["suggested_charts"]) >= 6:

                break

            profile["suggested_charts"].append({

                "type": "bar",

                "title": (
                    f"{numeric_column.replace('_', ' ').title()} "
                    f"by "
                    f"{category_column.replace('_', ' ').title()}"
                ),

                "x": category_column,

                "y": numeric_column,

                "aggregation": "sum",

                "limit": 10
            })

    # =========================================================
    # CATEGORY DISTRIBUTION
    # =========================================================
    #
    # IMPORTANT:
    # This works even when there are NO numeric columns.
    #
    # Example:
    #
    # branch
    # CSE       1000
    # ECE        300
    # AI         250
    #
    # =========================================================

    for category_column in profile["categorical_columns"]:

        if len(profile["suggested_charts"]) >= 8:

            break

        profile["suggested_charts"].append({

            "type": "category",

            "title": (
                f"{category_column.replace('_', ' ').title()} "
                f"Distribution"
            ),

            "column": category_column,

            "aggregation": "count",

            "limit": 10
        })

    # =========================================================
    # NUMERIC DISTRIBUTIONS
    # =========================================================

    for numeric_column in profile["numeric_columns"][:3]:

        if len(profile["suggested_charts"]) >= 8:

            break

        profile["suggested_charts"].append({

            "type": "histogram",

            "title": (
                f"{numeric_column.replace('_', ' ').title()} "
                f"Distribution"
            ),

            "column": numeric_column
        })

    # =========================================================
    # RETURN
    # =========================================================

    return profile