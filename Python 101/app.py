from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

class Customer(BaseModel):
    id: int
    name: str
    total_spent: float


# Simulate data (copy from .ipynb)
customers = pd.DataFrame({
    'customer_id': [101, 102, 103, 104,105],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eric'],
    'signup_date': pd.to_datetime(['2023-01-15', '2023-02-01', '2023-03-20', '2023-04-05', '2023-04-05']),
    'region': ['North', 'South', 'North', 'East', 'East']
})


orders = pd.DataFrame({
    'order_id': range(1, 11),
    'customer_id': [101, 102, 101, 103, 102, 104, 104, 101, 103, 104],
    'amount': [100, 150, 200, 130, 170, 120, 180, 90, 200, 220],
    'order_date': pd.to_datetime([
        '2023-03-01', '2023-03-05', '2023-03-07', '2023-03-15', '2023-03-22',
        '2023-03-25', '2023-04-01', '2023-04-02', '2023-04-04', '2023-04-10'
    ])
})

# 
merged = customers.merge(orders, on='customer_id', how='left')

spentPerCustomer = merged.groupby(['customer_id', 'name']).agg(
    total_spent=('amount', 'sum')
    ).reset_index()

@app.get("/")
def root():
    return {"message": "Welcome to the Data API"}

@app.get("/customers/top")
def top_customers():
        # Sort by total_spent, take top 3
        top = spentPerCustomer.sort_values(by='total_spent', ascending=False).head(3)
        return top.to_dict(orient='records');

@app.get("/customer/{customer_id}")
def get_customer(customer_id: int):
    customer = spentPerCustomer[spentPerCustomer['customer_id'] == customer_id]
    if customer.empty:
        return {'error': 'Customer not found'}
    row = customer.iloc[0]
    return Customer(
         id=int(row['customer_id']),
         name=str(row['name']),
         total_spent=float(row['total_spent'])
    )

@app.get("/customer/early_orders/")
def get_early_orders(days: Optional[int] = 30):
     merged['days_since_signup'] = (merged['order_date'] - merged['signup_date']).dt.days
     early_orders = merged[merged['days_since_signup'] <= days]
     if early_orders.empty:
          return {'error': f"No customer placed orders within {days} days"}
     return early_orders.sort_values(by='days_since_signup').to_dict(orient='records')