from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from .database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(30),
        default="business_user"
    )


class Dataset(Base):

    __tablename__ = "datasets"

    dataset_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    dataset_name = Column(
        String(255),
        nullable=False
    )

    original_filename = Column(
        String(255),
        nullable=False
    )

    table_name = Column(
        String(255),
        nullable=False
    )

    row_count = Column(
        Integer,
        default=0
    )

    column_count = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime
    )


class DatasetColumn(Base):

    __tablename__ = "dataset_columns"

    column_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.dataset_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    column_name = Column(
        String(255),
        nullable=False
    )

    data_type = Column(
        String(50),
        nullable=False
    )

    column_order = Column(
        Integer
    )


class Report(Base):

    __tablename__ = "reports"

    report_id = Column(
        Integer,
        primary_key=True
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    report_name = Column(
        String(200)
    )

    file_path = Column(
        String(300)
    )

    created_at = Column(
        DateTime
    )