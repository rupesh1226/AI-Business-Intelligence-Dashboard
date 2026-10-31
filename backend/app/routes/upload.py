from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException

import pandas as pd
import os

from sqlalchemy import (
    text, MetaData, Table, Column,
    Integer, BigInteger, Float, Boolean, DateTime, Text
)

from ..database import engine
from ..services.cleaning import clean_data
from ..services.dataset import create_table_name
from ..services.profiler import profile_dataset


router = APIRouter()


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    # =========================
    # 1. Validate filename
    # =========================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing"
        )

    filename = file.filename


    # =========================
    # 2. Validate extension
    # =========================

    allowed_extensions = (
        ".csv",
        ".xlsx",
        ".xls"
    )

    if not filename.lower().endswith(
        allowed_extensions
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are allowed"
        )


    # =========================
    # 3. Save uploaded file
    # =========================

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    contents = await file.read()

    with open(
        file_path,
        "wb"
    ) as file_object:

        file_object.write(
            contents
        )


    # =========================
    # 4. Read CSV / Excel
    # =========================

    try:

        if filename.lower().endswith(
            ".csv"
        ):

            df = pd.read_csv(
                file_path
            )

        else:

            df = pd.read_excel(
                file_path
            )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Could not read file: {str(e)}"
        )


    # =========================
    # 5. Clean data
    # =========================

    df = clean_data(df)


    # =========================
    # 6. Get dataset information
    # =========================

    row_count = len(df)

    column_count = len(df.columns)

    columns = list(
        df.columns
    )


    # =========================
    # 6.5. Automatically profile dataset
    # =========================

    profile = profile_dataset(df)



    # =========================
    # 7. Create MySQL table name
    # =========================

    table_name = create_table_name(
        filename
    )


    # =========================
    # 8. Store DataFrame in MySQL
    # =========================

   try:

    metadata = MetaData()

    # Create an automatic primary key
    primary_key_name = "record_id"

    while primary_key_name in df.columns:
        primary_key_name += "_"

    sql_columns = [
        Column(
            primary_key_name,
            Integer,
            primary_key=True,
            autoincrement=True
        )
    ]

    # Automatically detect column data types
    for column in df.columns:

        if pd.api.types.is_integer_dtype(df[column]):
            column_type = BigInteger

        elif pd.api.types.is_float_dtype(df[column]):
            column_type = Float

        elif pd.api.types.is_bool_dtype(df[column]):
            column_type = Boolean

        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            column_type = DateTime

        else:
            column_type = Text

        sql_columns.append(
            Column(str(column), column_type)
        )

    # Create table with primary key
    dataset_table = Table(
        table_name,
        metadata,
        *sql_columns
    )

    with engine.begin() as connection:

        dataset_table.create(connection)

        # Insert uploaded dataset
        df.to_sql(
            table_name,
            con=connection,
            if_exists="append",
            index=False
        )

except Exception as e:

    raise HTTPException(
        status_code=500,
        detail=f"Could not store data in MySQL: {str(e)}"
    )


    # =========================
    # 9. Save dataset metadata
    # =========================

    try:

        with engine.begin() as connection:

            result = connection.execute(
                text("""
                    INSERT INTO datasets
                    (
                        dataset_name,
                        original_filename,
                        table_name,
                        row_count,
                        column_count
                    )
                    VALUES
                    (
                        :dataset_name,
                        :original_filename,
                        :table_name,
                        :row_count,
                        :column_count
                    )
                """),
                {
                    "dataset_name":
                        filename.rsplit(
                            ".",
                            1
                        )[0],

                    "original_filename":
                        filename,

                    "table_name":
                        table_name,

                    "row_count":
                        row_count,

                    "column_count":
                        column_count
                }
            )

            dataset_id = result.lastrowid


            # =========================
            # 10. Save column metadata
            # =========================

            for index, column in enumerate(
                df.columns
            ):

                data_type = str(
                    df[column].dtype
                )

                connection.execute(
                    text("""
                        INSERT INTO dataset_columns
                        (
                            dataset_id,
                            column_name,
                            data_type,
                            column_order
                        )
                        VALUES
                        (
                            :dataset_id,
                            :column_name,
                            :data_type,
                            :column_order
                        )
                    """),
                    {
                        "dataset_id":
                            dataset_id,

                        "column_name":
                            column,

                        "data_type":
                            data_type,

                        "column_order":
                            index
                    }
                )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save dataset metadata: {str(e)}"
        )


    # =========================
    # 11. Return response
    # =========================

    return {

        "message":
            "Dataset uploaded and stored successfully",

        "dataset_id":
            dataset_id,

        "filename":
            filename,

        "table_name":
            table_name,

        "rows":
            row_count,

        "columns_count":
            column_count,

        "columns":
            columns,
        
         "profile":
            profile
    }
