import models
from typing import Optional
from sqlalchemy.orm import Session
from db import engine, SessionLocal
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Header, Depends




models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount("/static", StaticFiles(directory="assets"), name="static")
templates = Jinja2Templates(directory="templates")




# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@app.on_event('startup')
def startup_populate_db():
    db = SessionLocal()
    num_films = db.query(models.Film).count()
    if num_films == 0:
        films = models.HARD_CODED_FILMS
        for film in films:
            db.add(models.Film(**film))
        db.commit()
        print('Films successfully created !!!!!!!!!!')
    db.close()







@app.get('/', response_class=HTMLResponse)
async def films_list_view(
    request: Request, 
    hx_request: Optional[str] = Header(None), 
    db: Session = Depends(get_db),
    page: int = 1
):
    
    N = 5 # Films per page
    OFFSET = (page - 1) * N
    
    films = db.query(models.Film).offset(OFFSET).limit(N)
    num_films = db.query(models.Film).count()

    context = {
        'num_films': num_films,
        'request': request,
        'films': films,
        'page': page,
    }
    
    if hx_request:
        return templates.TemplateResponse('partials/table.html', context)
    
    return templates.TemplateResponse('films_list.html', context)






