from pyCRM.Authentication import AuthenticationDao
from pyCRM.Authentication import UserAuthService

# UserAuthService.create_user('gao', '123456')
ado = AuthenticationDao('gao', '123456')
print(ado.login())
