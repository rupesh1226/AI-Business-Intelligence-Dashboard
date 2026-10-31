import re


def create_table_name(filename: str) -> str:
    """
    Convert an uploaded filename into a safe database table name.
    """

    # Remove file extension
    name = filename.rsplit(".", 1)[0]

    # Convert to lowercase
    name = name.lower()

    # Replace special characters with underscore
    name = re.sub(
        r"[^a-z0-9_]",
        "_",
        name
    )

    # Remove repeated underscores
    name = re.sub(
        r"_+",
        "_",
        name
    )

    # Remove underscores at beginning/end
    name = name.strip("_")

    # If filename becomes empty
    if not name:
        name = "dataset"

    # Add prefix
    return "data_" + name