from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly
import plotly.express as px
import json
import os
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class SalesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    product = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    if not SalesData.query.first():
        # Generate mock data
        products = ['Laptop', 'Phone', 'Tablet', 'Desktop', 'Accessories']
        categories = ['Electronics', 'Mobile', 'Computing']
        
        for _ in range(100):
            sale = SalesData(
                date=datetime(2024, np.random.randint(1, 13), np.random.randint(1, 28)),
                product=np.random.choice(products),
                category=np.random.choice(categories),
                quantity=np.random.randint(1, 50),
                revenue=np.random.uniform(100, 2000)
            )
            db.session.add(sale)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales')
def sales():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([{
        'date': sale.date,
        'product': sale.product,
        'category': sale.category,
        'quantity': sale.quantity,
        'revenue': sale.revenue
    } for sale in sales_data])
    
    # Create revenue by category plot
    fig1 = px.bar(df.groupby('category')['revenue'].sum().reset_index(), 
                  x='category', y='revenue', title='Revenue by Category')
    
    # Create product sales distribution
    fig2 = px.histogram(df, x='quantity', nbins=20, 
                       title='Distribution of Sales Quantities')
    
    # Create time series of revenue
    fig3 = px.line(df.groupby('date')['revenue'].sum().reset_index(), 
                   x='date', y='revenue', title='Daily Revenue')
    
    graphs = [
        json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder),
        json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder),
        json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    ]
    
    return render_template('sales.html', graphs=graphs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
