# A factory of different types of roles

from ..models import *

def role_factory(role):

    roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }

    desired_role = Role()
    
    try: 
        for permission in roles[role]:
            desired_role.add_permission(permission)
        desired_role.name = role
    except KeyError as e:
        raise

    return desired_role

