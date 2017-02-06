def has_function(obj, func):
    '''Returns True if /obj/ has a callable attribute /func/.
    '''
    return callable(getattr(obj, func))
