from app import create_app, db
from app.models import User, Course

app = create_app()
# flask built -in shell for easy testing without importing
@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User': User, 'Course': Course}