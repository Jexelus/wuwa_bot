import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json

Base = declarative_base()
DATABASE_URL = "postgresql://altushka:rootroot@192.168.1.47:8100/wuwa"


class Guides(Base):
    __tablename__ = "guides"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    constellation_name = sqlalchemy.Column(sqlalchemy.String)
    constellation_rarity = sqlalchemy.Column(sqlalchemy.Integer)
    constellation_element = sqlalchemy.Column(sqlalchemy.String)
    constellation_weapon_type = sqlalchemy.Column(sqlalchemy.String)
    constellation_role = sqlalchemy.Column(sqlalchemy.String)
    constellation_rising_materials = sqlalchemy.Column(sqlalchemy.JSON)
    constellation_rising_talent_materials = sqlalchemy.Column(sqlalchemy.JSON)
    constellation_weapon_image = sqlalchemy.Column(sqlalchemy.String)
    # constellation_artifact_image = sqlalchemy.Column(sqlalchemy.String)
    constellation_image = sqlalchemy.Column(sqlalchemy.String)
    constellation_talents_image = sqlalchemy.Column(sqlalchemy.String, default=None)


class Rating(Base):
    __tablename__ = "rating"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    constellation_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("guides.id"))
    views = sqlalchemy.Column(sqlalchemy.Integer)
    likes = sqlalchemy.Column(sqlalchemy.Integer)


class User(Base):
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    favorite_guides = sqlalchemy.Column(sqlalchemy.JSON, default=json.dumps([]))


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
session = sessionmaker(engine, expire_on_commit=False)


def create_guide(
        constellation_name,
        constellation_rarity,
        constellation_element,
        constellation_weapon_type,
        constellation_role,
        constellation_rising_materials,
        constellation_rising_talent_materials,
        # constellation_artifact_image,
        constellation_image,
        constellation_talents_image,
        constellation_weapon_image

):
    with session() as ss:
        guide = Guides(
            constellation_name=constellation_name,
            constellation_rarity=constellation_rarity,
            constellation_element=constellation_element,
            constellation_weapon_type=constellation_weapon_type,
            constellation_role=constellation_role,
            constellation_rising_materials=constellation_rising_materials,
            constellation_rising_talent_materials=constellation_rising_talent_materials,
            # constellation_artifact_image=constellation_artifact_image,
            constellation_image=constellation_image,
            constellation_talents_image=constellation_talents_image,
            constellation_weapon_image=constellation_weapon_image
        )
        ss.add(guide)
        ss.commit()
        ss.refresh(guide)
        return guide


def get_guides_names():
    with session() as ss:
        guides = ss.query(Guides).order_by(Guides.constellation_rarity).all()
        return [guide.constellation_name for guide in guides]


def get_guide_by_name(name):
    with session() as ss:
        print(name)
        guide = ss.query(Guides).filter(Guides.constellation_name.like(f"%{name}%")).all()
        print(guide)
        return guide


def get_guides():
    with session() as ss:
        guides = ss.query(Guides).order_by(Guides.constellation_rarity.desc()).all()
        return guides


def get_guide_by_id(id):
    with session() as ss:
        guide = ss.query(Guides).filter(Guides.id == id).first()
        return guide


def add_user(user_id):
    with session() as ss:
        user = User(chat_id=user_id)
        ss.add(user)
        ss.commit()
        ss.refresh(user)
        return user


def add_to_favorite(user_id, constellation_id):
    with session() as ss:
        user = ss.query(User).filter(User.chat_id == user_id).first()
        user_fav = json.loads(user.favorite_guides)
        user_fav.append(constellation_id)
        user.favorite_guides = json.dumps(user_fav, ensure_ascii=False, indent=4)
        ss.commit()
        ss.refresh(user)
        return user


def get_favorite(user_id):
    with session() as ss:
        user = ss.query(User).filter(User.chat_id == user_id).first()
        return json.loads(user.favorite_guides)


def get_user(user_id):
    with session() as ss:
        user = ss.query(User).filter(User.chat_id == user_id).first()
        if user:
            return user
        else:
            return add_user(user_id)


def remove_from_favorite(user_id, constellation_id):
    with session() as ss:
        user = ss.query(User).filter(User.chat_id == user_id).first()
        user_fav = json.loads(user.favorite_guides)
        user_fav.remove(constellation_id)
        user.favorite_guides = json.dumps(user_fav, ensure_ascii=False, indent=4)
        ss.commit()
        ss.refresh(user)
        return user


def get_rating(constellation_id):
    with session() as ss:
        rating = ss.query(Rating).filter(Rating.constellation_id == constellation_id).first()
        if rating:
            return rating
        else:
            rating = Rating(constellation_id=constellation_id, views=1, likes=0)
            ss.add(rating)
            ss.commit()
            ss.refresh(rating)
            return rating


def rating_views_add(constellation_id):
    with session() as ss:
        rating = ss.query(Rating).filter(Rating.constellation_id == constellation_id).first()
        rating.views += 1
        ss.commit()
        ss.refresh(rating)
        return rating


def rating_likes_add(constellation_id):
    with session() as ss:
        rating = ss.query(Rating).filter(Rating.constellation_id == constellation_id).first()
        rating.likes += 1
        ss.commit()
        ss.refresh(rating)
        return rating


def get_rating_board():
    with session() as ss:
        ratings = ss.query(Rating).order_by(Rating.likes.desc()).all()
        return ratings


def rating_likes_remove(constellation_id):
    with session() as ss:
        rating = ss.query(Rating).filter(Rating.constellation_id == constellation_id).first()
        rating.likes -= 1
        ss.commit()
        ss.refresh(rating)
        return rating
