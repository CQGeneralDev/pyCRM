import logging.config
import os

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.ZHS16GBK"

sql_url = r'sqlite:///D:\PycharmProjects\pyCRM\dev.db'
sql_task_url = r'sqlite:///D:\PycharmProjects\pyCRM\task.db'

# data_conn = create_engine('oracle://gao:gao123159@172.17.254.200:1521/mydev', echo=True, pool_size=10)
data_conn = create_engine(sql_url, echo=True)
task_data_conn = create_engine(sql_task_url, echo=True)
Session = sessionmaker(bind=data_conn, autocommit=False, autoflush=False)


def module_to_dict(module):
    module_json = dict()
    keys = dir(module)
    keys = list(filter(lambda key: key == '__tablename__' or key[0:1] != '_', keys))
    for key in keys:
        if callable(getattr(module, key)):
            continue
        module_json[key] = getattr(module, key)
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
