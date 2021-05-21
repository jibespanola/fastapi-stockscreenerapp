import models
import yfinance
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine
from pydantic import BaseModel 
from models import Stock
from sqlalchemy.orm import Session

app = FastAPI()

#engine from database.py file
#Creates all tables
models.Base.metadata.create_all(bind=engine)

#Global directory for our template
templates = Jinja2Templates(directory="templates")

#BaseModel is from Pydantic
#structure and type validation for HTTP requests
class StockRequest(BaseModel):
    symbol: str

#Dependency injection
#Gets a db session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#GET Endpoint
#Home Route
#request object of type Request is received by the home function
@app.get("/")
def home(request: Request, forward_pe = None, dividend_yield = None, ma50 = None, ma200 = None, db: Session = Depends(get_db)):
    """
    Displays all stocks in the database and button to add more
    button next to each stock to delete from database
    Filters to filter this list of stocks
    button next to each to add a note or save for later
    """

    stocks = db.query(Stock)

    if forward_pe:
        stocks = stocks.filter(Stock.forward_pe < forward_pe)

    if dividend_yield:
        stocks = stocks.filter(Stock.dividend_yield > dividend_yield)
    
    if ma50:
        stocks = stocks.filter(Stock.price > Stock.ma50)
    
    if ma200:
        stocks = stocks.filter(Stock.price > Stock.ma200)
    
    stocks = stocks.all()
    
    #Return home file as the template
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "stocks": stocks, 
        "dividend_yield": dividend_yield,
        "forward_pe": forward_pe,
        "ma200": ma200,
        "ma50": ma50
    })


def fetch_stock_data(id: int):
    #db session in background task
    db = SessionLocal()

    stock = db.query(Stock).filter(Stock.id == id).first()

    yahoo_data = yfinance.Ticker(stock.symbol)

    stock.ma200 = yahoo_data.info['twoHundredDayAverage']
    stock.ma50 = yahoo_data.info['fiftyDayAverage']
    stock.price = yahoo_data.info['previousClose']
    stock.forward_pe = yahoo_data.info['forwardPE']
    stock.forward_eps = yahoo_data.info['forwardEps']
    stock.dividend_yield = yahoo_data.info['dividendYield']

    db.add(stock)
    db.commit()

#POST endpoint
#Post data to stock route
@app.post("/stock")
#async function required to execute background_tasks
#get_db function executes first
#create_stock function depends on get_db
async def create_stock(stock_request: StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Add one or more tickers to the database
    Background task will use yfinance and load key statistics
    """

    stock = Stock()
    stock.symbol = stock_request.symbol
    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id)

    return {
        "code": "success",
        "message": "stock was added to the database"
    }