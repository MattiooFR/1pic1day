from app import create_app, db
from app.models import Album, Image, db_reset

app = create_app()



@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Album": Album, "Image": Image, "db_reset": db_reset()}
