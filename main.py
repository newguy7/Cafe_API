from flask import Flask, jsonify, render_template, request,redirect,url_for

from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkGlBC6O6donzWlSihBXox7C0sKR6b'


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        """
        Converts the object to a dictionary representation.
        Returns a dictionary representation of the object, where the keys are the column names 
        of the table and the values are the corresponding attribute values of the object.
        """
        dictionary = {}

        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_results = result.scalars().all()  
    print(all_results)
    random_cafe = random.choice(all_results)
    
    return jsonify(cafes=random_cafe.to_dict())
    # return jsonify(cafe={
    #             'name' : random_cafe.name,
    #             'map_url' : random_cafe.map_url,
    #             'img_url' : random_cafe.img_url,
    #             'location' : random_cafe.location,

    #             "amenities" : {
    #                 'seats' : random_cafe.seats,
    #                 'has_toilet' : random_cafe.has_toilet,
    #                 'has_wifi' : random_cafe.has_wifi,
    #                 'has_sockets' : random_cafe.has_sockets,
    #                 'can_take_calls' : random_cafe.can_take_calls,
    #                 'coffee_price' : random_cafe.coffee_price
    #             }                   
    #         })

@app.route("/all")
def all_data():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_results = result.scalars().all()
    all_cafe = []
    for cafe in all_results:
        cafe = Cafe.to_dict(cafe)
        all_cafe.append(cafe)    
    return jsonify(cafe=all_cafe)

@app.route("/search")
def cafe_at_location():   
    location = request.args.get("location")     
    print(location)
    cafe = db.session.execute(db.select(Cafe).where(Cafe.location == location)).scalars()
    all_cafe = cafe.all()
    
    if all_cafe:
        cafe_in_the_location = [Cafe.to_dict(cafe) for cafe in all_cafe]  
        return jsonify(cafe=cafe_in_the_location)
    else:        
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"}), 404

# HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_cafe():                  
        name = request.form.get("name")
        map_url = request.form.get("map_url")
        img_url = request.form.get("img_url")
        location = request.form.get("location")                
        seats = request.form.get("seats")
        has_toilet = bool(request.form.get("has_toilet"))
        has_wifi = bool(request.form.get("has_wifi"))
        has_sockets = bool(request.form.get("has_sockets"))
        can_take_calls = bool(request.form.get("can_take_calls"))
        coffee_price = request.form.get("coffee_price")
        cafe = Cafe(name=name, map_url=map_url,img_url=img_url,location=location,seats=seats,has_toilet=has_toilet,
                    has_wifi=has_wifi,has_sockets=has_sockets,can_take_calls=can_take_calls,coffee_price=coffee_price)
        db.session.add(cafe)
        db.session.commit()
        return jsonify(response=dict(Success="Successfully added the new cafe."))  

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>",methods=["PATCH"])
def update_price(cafe_id):    
    new_price = request.form.get("new_price")  
    print(new_price)  
    cafe_to_update = db.get_or_404(Cafe, cafe_id)    
    if cafe_to_update:
        cafe_to_update.coffee_price = f"£{new_price}"
        db.session.commit()
        return jsonify(response=dict(Success="Successfully updated the price.")) 
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404
# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.form.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response=dict(Success="Successfully deleted the cafe.")) 
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 40
    else:
        return jsonify(invalid={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."})

if __name__ == '__main__':
    app.run(debug=True)
