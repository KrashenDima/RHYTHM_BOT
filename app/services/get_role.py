from app.bot.enums.roles import UserRole

def get_role(id: int, admin_ids: list[int], 
             owner_ids: list[int]) -> UserRole:
    
    if id in owner_ids:
        return UserRole.OWNER
    elif id in admin_ids:
        return UserRole.ADMIN
    else:
        return UserRole.USER