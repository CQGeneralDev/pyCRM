from pyCRM.HumanResourceManagement.models.CurrentSession import UserSession

u = UserSession('ssss')
print(u)
u['aa'] = 123456
print(u)
u['e'] = 234
print(u)
u.clear()
print(u)
