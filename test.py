from pyCRM.Authentication import UserAuthService
from pyCRM.Interfaces import add, run


@add
def ping():
    return 'pong'


if __name__ == '__main__':
    print(dir(UserAuthService))
    print(run('{"jsonrpc": "2.0", "method": "ping", "id": 1}'))
