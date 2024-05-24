from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    match_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    winner_team_id = Column(Integer, ForeignKey('teams.team_id'))

    winner_team = relationship("Team", foreign_keys=[winner_team_id])

class Player(Base):
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String, unique=True)
    username = Column(String)

class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))

    match = relationship("Match", back_populates="teams")

class Hero(Base):
    __tablename__ = 'heroes'
    hero_id = Column(Integer, primary_key=True, autoincrement=True)
    hero_name = Column(String, unique=True)

class MatchDetail(Base):
    __tablename__ = 'matchdetails'
    match_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    player_id = Column(Integer, ForeignKey('players.player_id'))
    hero_id = Column(Integer, ForeignKey('heroes.hero_id'))

    match = relationship("Match", back_populates="matchdetails")
    team = relationship("Team", back_populates="matchdetails")
    player = relationship("Player", back_populates="matchdetails")
    hero = relationship("Hero", back_populates="matchdetails")
