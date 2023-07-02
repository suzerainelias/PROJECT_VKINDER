import sqlalchemy as sql
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config import data_base_url

# Объекты
metadata = MetaData()

Base = declarative_base()

engine = create_engine(data_base_url)

# Классы
class Matches(Base):
    __tablename__ = 'matches'
    profile_id = sql.Column(sql.Integer, primary_key=True)
    unique_id = sql.Column(sql.Integer, primary_key=True)

class Tools(Base):
    __tablename__ = 'UserVK'
    id = sql.Column(sql.Integer, primary_key=True)
    profile_id = sql.Column(sql.Integer)
    unique_id = sql.Column(sql.Integer)

# Функция добавления в таблицу UserVK
def add_database_user(engine, profile_id, unique_id):
    with Session(engine) as session:
        to_bd = Tools(profile_id=profile_id, unique_id=unique_id)
        session.add(to_bd)
        session.commit()

# Функция проверки наличия пользователя в таблице UserVK
def user_check(engine, profile_id, unique_id):
    with Session(engine) as session:
        bd_from = (session.query(Tools).filter(Tools.profile_id == profile_id, Tools.unique_id == unique_id).first())
        return True if bd_from else False

if __name__ == '__main__':
    # Проверка подключения к БД
    # engine = create_engine(data_base_url)
    # with engine.connect() as con:
    #
    #     rs = con.execute('SELECT 1')
    #
    #     for row in rs:
    #         print(row)
    Base.metadata.create_all(engine)