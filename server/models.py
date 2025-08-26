from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = relationship("Recipe", back_populates="user")

    # @validates('username')
    # def validate_username(self, key, username):
    #     if not username:
    #         raise ValueError("Username is required")
    #     return username


    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not a readable attribute")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))
    
    def __repr__(self):
        return f"User {self.username}, ID {self.id}"

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="recipes")

    def __repr__(self):
        return f"Recipe {self.title}, ID {self.id}"
    
    # @validates('title')
    # def validate_title(self, key, title):
    #     if not title:
    #         raise ValueError("Title is required")
    #     return title

    # @validates('instructions')
    # def validate_instructions(self, key, instructions):
    #     if not instructions:
    #         raise ValueError("Instructions are required")
    #     if len(instructions) < 50:
    #         raise ValueError("Instructions must be at least 50 characters long")
    #     return instructions