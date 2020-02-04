def syncterm_connection_type(val):
    return {
        'telnet': 'Telnet',
        'ssh': 'SSH',
    }[val]


def qodem_method(val):
    return {
        'telnet': 'TELNET',
        'ssh': 'SSH',
    }[val]


def etherterm_protocol(val):
    return {
        'telnet': 'TELNET',
        'ssh': 'SSH',
    }[val]


def magiterm_connection_type(val):
    return val


filters = {
    'syncterm_connection_type': syncterm_connection_type,
    'magiterm_connection_type': magiterm_connection_type,
    'qodem_method': qodem_method,
    'etherterm_protocol': etherterm_protocol,
}
