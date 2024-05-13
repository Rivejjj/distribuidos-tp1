DATA_SEPARATOR = "\t"


def to_str(fields):
    values = []
    for field in fields:
        if field is None or field == "":
            values.append("")
        else:
            values.append(str(field))

    return DATA_SEPARATOR.join(values)
