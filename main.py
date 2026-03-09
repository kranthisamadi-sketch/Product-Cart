from fastapi import Depends, FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from models import product
from database import session, engine
import database_models
from sqlalchemy.orm import Session


app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
    )

database_models.Base.metadata.create_all(bind=engine)
@app.get("/")
def greek():
    return "Hello, Greek!"

products = [
   product(id=1, name="Laptop", description="A high-performance laptop", price=999.99, quantity=10),
   product(id=2, name="Smartphone", description="A powerful smartphone", price=499.99, quantity=20),
   product(id=3, name="Headphones", description="Noise-cancelling headphones", price=199.99, quantity=15),
   product(id=4, name="Smartwatch", description="A stylish smartwatch", price=299.99, quantity=5),
   product(id=5, name="Tablet", description="A versatile tablet", price=399.99, quantity=8)
]

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
        
# Too display the data in the database.
def init_db():
    db = session()
    
    count = db.query(database_models.Product).count
    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
    
    db.commit()
    

init_db()

@app.get("/products") 
def get_all_products(db: Session = Depends(get_db)):
    # db = session() 
    # db.query()
    db_products = db.query(database_models.Product).all()
    return db_products   

@app.get("/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if  db_product:
        return db_product
    return "Product not found"

@app.post("/products")
def create_product(product: product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product

@app.put("/products/{id}")
def update_product(id:int,product: product, db: Session = Depends(get_db)):
   db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
   if db_product:
       db_product.name = product.name
       db_product.description = product.description
       db_product.price = product.price
       db_product.quantity = product.quantity
       db.commit()
       return "Product updated successfully"
   else:    
    return "Product Not Found"

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product) 
        db.commit()  
    else:
        return "Product Not Found"