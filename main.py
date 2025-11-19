import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from schemas import Choreography, Marker
from database import db, create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Choreography API is running"}


@app.get("/api/choreographies")
def list_choreographies():
    try:
        items = get_documents("choreography")
        # Convert ObjectId to string
        for it in items:
            it["_id"] = str(it["_id"]) if "_id" in it else None
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/choreographies")
def create_choreography(choreo: Choreography):
    try:
        inserted_id = create_document("choreography", choreo)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MarkerUpdate(BaseModel):
    markers: List[Marker]


@app.put("/api/choreographies/{choreo_id}/markers")
def update_markers(choreo_id: str, payload: MarkerUpdate):
    try:
        if db is None:
            raise Exception("Database not available")
        # Validate ObjectId
        try:
            oid = ObjectId(choreo_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid choreography id")

        # Replace markers array
        result = db.choreography.update_one(
            {"_id": oid},
            {"$set": {"markers": [m.model_dump() for m in payload.markers]}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Choreography not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
