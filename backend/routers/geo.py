from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Location, Base
from fastapi import status
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "coordinates": mapping(to_shape(loc.geom))["coordinates"]
        } for loc in locations
    ]

@router.post("/locations", status_code=status.HTTP_201_CREATED)
def add_location(name: str, lat: float, lng: float, db: Session = Depends(get_db)):
    from geoalchemy2.elements import WKTElement
    geom = WKTElement(f'POINT({lng} {lat})', srid=4326)
    loc = Location(name=name, geom=geom)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return {"id": loc.id, "name": loc.name, "coordinates": [lng, lat]}