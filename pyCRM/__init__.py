import logging.config
import os
import yaml
import redis

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute

os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.ZHS16GBK"

main_path = os.path.dirname(os.path.dirname(__file__))
sql_url = os.path.join(main_path, 'dev.db')
sql_task_url = os.path.join(main_path, 'task.db')

# data_conn = create_engine('oracle://gao:gao123159@172.17.254.200:1521/mydev', echo=True, pool_size=10)
data_conn = create_engine('sqlite:///' + sql_url, echo=True)
task_data_conn = create_engine('sqlite:///' + sql_task_url, echo=True)
Session = sessionmaker(bind=data_conn, autocommit=False, autoflush=False)


def module_to_dict(module_class, module):
    """
    module_json = dict()
    keys = dir(module)
    keys = list(filter(lambda key: key == '__tablename__' or key[0:1] != '_' or key != 'MetaData', keys))
    for key in keys:
        if callable(getattr(module, key)):
            continue
        module_json[key] = getattr(module, key)
    return module_json
    """
    module_json = dict()
    for key in dir(module_class):
        if type(getattr(module_class, key)) is InstrumentedAttribute:
            module_json[key] = getattr(module, key)
    module_json['__tablename__'] = getattr(module, '__tablename__', None)
    return module_json


def dict_to_module(module_class, module_dict):
    for key in module_dict.keys():
        setattr(module_class, key, module_dict[key])
    return module_class


main_path = os.path.dirname(os.path.dirname(__file__))
__login_config = os.path.join(main_path, 'configure', 'logging.yaml')

__config = None

with open(__login_config, 'r') as f:
    __config = yaml.load(f)

logging.config.dictConfig(__config)
logger = logging.getLogger('show')

__main_config_path = os.path.join(main_path, 'configure', 'crm.yaml')
main_config = None
with open(__main_config_path, 'r') as f:
    main_config = yaml.load(f)
