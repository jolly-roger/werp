from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, Date, DateTime, Boolean, ForeignKey, and_, Text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship, backref, column_property

DBase = declarative_base()