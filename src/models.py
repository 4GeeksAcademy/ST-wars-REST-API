from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name =  db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorite= db.relationship("Favorites", backref= "user", lazy=True)

    def __repr__(self):
        return '<User %r>' % self.first_name

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name":self.first_name,
            "last_name":self.last_name
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__="planets"
    planet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diameter = db.Column(db.Integer, nullable=False)
    climate = db.Column(db.String(150), nullable=False)
    terrain = db.Column(db.String(150), nullable=False)
    favorite= db.relationship("Favorites", backref= "planets", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "diameter": self.diameter,
            "climate":self.climate,
            "terrain":self.terrain
        }
    
class Favorites(db.Model):
    __tablename__="favorites"
    id = db.Column(db.Integer, primary_key=True,)
    user_fk= db.Column(db.Integer, db.ForeignKey("user.id")) 
    planet_fk= db.Column(db.Integer, db.ForeignKey("planets.planet_id")) 
