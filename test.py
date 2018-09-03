from pyCRM.HumanResourceManagement.Authentication import AuthenticationDao

# UserAuthService.create_user('gao', '123456')
ado = AuthenticationDao('gao', '123456')
print(ado.login())
