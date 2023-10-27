from datetime import datetime

# datetime to String (date)
def date_to_str(c_date: datetime, frmt="%d/%m/%Y"):
    """
    Convierte un datetime a string (sólo fecha).

    :param c_date: fecha en formato datetime
    :param frmt: formato deseado para el string (default es "%d/%m/%Y")
    :return: fecha en formato de string
    """
    return c_date.strftime(frmt)


# datetime to String (date + hour)
def date_time_to_str(c_date: datetime, frmt="%d/%m/%Y %H:%M:%S.%f"):
    """
    Convierte un datetime a string (fecha y hora).

    :param c_date: fecha y hora en formato datetime
    :param frmt: formato deseado para el string (default es "%d/%m/%Y %H:%M%S")
    :return: fecha y hora en formato de string
    """
    return c_date.strftime(frmt)
