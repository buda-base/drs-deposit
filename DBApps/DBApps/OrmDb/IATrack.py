"""
SqlAlchemy ORM for tracking IA
"""
import configparser
import logging
import os.path
import sys

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, text, select, insert, Table
from sqlalchemy.orm import declarative_base, relationship, Session

from config.config import DBConfig

Base = declarative_base()


# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)

class Works(Base):
    __tablename__ = 'Works'
    workId = Column(Integer, primary_key = True)

    def __repr__(self):
        return f"Work(id={self.id!r})"

# Not using - reflect exsting database
class IATrack(Base):
    __tablename__ = 'IATrack',
    id = Column(Integer, primary_key=True)
    ia_id = Column(String(45))
    workId = Column(Integer, ForeignKey('Works.workId'))
    task_id = Column(Integer)

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


def BuildORMRepo():
    """
    Defines the entities used in the IA Tracking stack
    """

    # Use the qa section, which is an authorized user
    cnf: DBConfig = DBConfig('qa', '~/.config/bdrc/db_apps.config')
    # We need to reach through the confi parser
    engine_cnf = configparser.ConfigParser()
    engine_cnf.read(os.path.expanduser(cnf.db_cnf))

    conn_str = "mysql+pymysql://%s:%s@%s:%d/%s" % (
        engine_cnf.get(cnf.db_host, "user"),
        engine_cnf.get(cnf.db_host, "password"),
        engine_cnf.get(cnf.db_host, "host"),
        engine_cnf.getint(cnf.db_host, "port", fallback=3306),
        engine_cnf.get(cnf.db_host, "database"))

    # Try in memory
    # conn_str = "sqlite+pysqlite:///:memory:"
    engine = create_engine(conn_str, echo=True, future=True)
    try:
        # Base.metadata.create_all(engine)
        iaTrack = Table("IATrack", Base.metadata, autoload_with=engine )
        [c.name for c in iaTrack.columns]
    except:
        ee = sys.exc_info()
        logging.info(ee)


if __name__ == '__main__':
    BuildORMRepo()
