import pandas as pd


def clean_data(df):

    # Make a copy
    df = df.copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Clean column names
    df.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        for column in df.columns
    ]

    # Remove completely empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Remove completely empty rows
    df = df.dropna(
        axis=0,
        how="all"
    )

    # Detect and convert date/time columns
    for column in df.columns:

        column_name = column.lower()

        if (
            "date" in column_name
            or "time" in column_name
        ):

            try:

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                if converted.notna().sum() > 0:

                    df[column] = converted

            except Exception:

                pass

    # Clean text columns
    for column in df.select_dtypes(
        include=["object"]
    ).columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    # Fill numeric missing values
    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numeric_columns:

        df[column] = df[column].fillna(0)

    # Fill text missing values
    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for column in text_columns:

        df[column] = df[column].fillna("")

    return df