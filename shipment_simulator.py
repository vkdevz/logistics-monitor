"""
Real-Time Logistics Bottleneck Monitor
Live Shipment Simulation Data Generator
Generates 5,000 realistic global shipments with delays, regions, routes, and financial impact
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)

class ShipmentSimulator:
    def __init__(self, num_shipments=5000):
        self.num_shipments = num_shipments
        self.regions = ['APAC', 'EMEA', 'AMER', 'LATAM']
        self.carriers = ['FedEx', 'DHL', 'UPS', 'Maersk', 'Hapag-Lloyd', 'CMA CGM', 'Local Courier']
        self.routes = {
            'APAC': ['SG-HK', 'SG-JP', 'HK-AU', 'SH-SG', 'BK-SH'],
            'EMEA': ['NL-DE', 'UK-FR', 'DE-PL', 'NL-IT', 'UK-DE'],
            'AMER': ['LA-NY', 'NY-MX', 'SF-LA', 'TX-NY', 'LA-TX'],
            'LATAM': ['BR-AR', 'MX-BR', 'CL-BR', 'CO-BR', 'MX-CL']
        }
        self.statuses = ['On-Time', 'Delayed', 'Critical Delay', 'In Transit', 'Pending']
        
    def generate_delay_hours(self, status):
        """Generate realistic delay hours based on status"""
        if status == 'On-Time':
            return np.random.normal(0, 2, 1)[0]  # -2 to +2 hours variance
        elif status == 'Delayed':
            return np.random.normal(24, 12, 1)[0]  # 12-36 hours delay
        elif status == 'Critical Delay':
            return np.random.normal(72, 24, 1)[0]  # 48-96+ hours delay
        else:
            return 0
    
    def generate_shipments(self):
        """Generate realistic shipment dataset"""
        shipments = []
        base_date = datetime.now() - timedelta(days=7)
        
        for i in range(self.num_shipments):
            region = np.random.choice(self.regions, p=[0.35, 0.25, 0.25, 0.15])
            route = np.random.choice(self.routes[region])
            carrier = np.random.choice(self.carriers, p=[0.20, 0.18, 0.17, 0.12, 0.11, 0.10, 0.12])
            
            # Status distribution: 70% on-time, 20% delayed, 10% critical
            status = np.random.choice(
                self.statuses[:3],
                p=[0.70, 0.20, 0.10]
            )
            
            delay_hours = max(0, self.generate_delay_hours(status))
            
            # Shipment value ($) - varies by region and carrier
            region_multiplier = {'APAC': 15000, 'EMEA': 18000, 'AMER': 12000, 'LATAM': 8000}
            base_value = region_multiplier[region]
            shipment_value = base_value + np.random.normal(0, base_value * 0.2, 1)[0]
            
            # Financial loss calculation: $500/hour for delay + 0.5% of shipment value per 24hrs
            financial_loss = delay_hours * 500 + (shipment_value * 0.005 * (delay_hours / 24))
            
            shipment_date = base_date + timedelta(hours=np.random.randint(0, 168))
            
            shipments.append({
                'Shipment_ID': f'SHP{i+1:06d}',
                'Region': region,
                'Route': route,
                'Carrier': carrier,
                'Status': status,
                'Shipment_Value_USD': round(shipment_value, 2),
                'Delay_Hours': round(delay_hours, 1),
                'Financial_Loss_USD': round(financial_loss, 2),
                'Ship_Date': shipment_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Expected_Delivery': (shipment_date + timedelta(days=np.random.randint(5, 15))).strftime('%Y-%m-%d'),
                'Current_Location': f"{route.split('-')[0]}-HUB",
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return pd.DataFrame(shipments)
    
    def calculate_regional_analytics(self, df):
        """Calculate key metrics by region"""
        analytics = df.groupby('Region').agg({
            'Delay_Hours': ['mean', 'max', 'sum'],
            'Financial_Loss_USD': ['sum', 'mean'],
            'Shipment_ID': 'count',
            'Status': lambda x: (x == 'Delayed').sum()
        }).round(2)
        
        analytics.columns = ['Avg_Delay_Hours', 'Max_Delay_Hours', 'Total_Delay_Hours',
                           'Total_Financial_Loss_USD', 'Avg_Financial_Loss_USD',
                           'Total_Shipments', 'Delayed_Count']
        
        analytics['Delay_Rate_%'] = (analytics['Delayed_Count'] / analytics['Total_Shipments'] * 100).round(2)
        
        return analytics
    
    def calculate_carrier_analytics(self, df):
        """Calculate key metrics by carrier"""
        analytics = df.groupby('Carrier').agg({
            'Delay_Hours': 'mean',
            'Financial_Loss_USD': ['sum', 'mean'],
            'Shipment_ID': 'count'
        }).round(2)
        
        analytics.columns = ['Avg_Delay_Hours', 'Total_Financial_Loss_USD',
                           'Avg_Financial_Loss_USD', 'Total_Shipments']
        
        return analytics.sort_values('Total_Financial_Loss_USD', ascending=False)

# Generate dataset
simulator = ShipmentSimulator(num_shipments=5000)
shipments_df = simulator.generate_shipments()

# Save to CSV
shipments_df.to_csv('/home/claude/shipments_live_data.csv', index=False)
print("✓ Live shipment data generated: shipments_live_data.csv")
print(f"✓ Total shipments: {len(shipments_df)}")
print(f"\nDataset Preview (first 5 rows):")
print(shipments_df.head())

# Generate analytics
print("\n" + "="*80)
print("REGIONAL ANALYTICS")
print("="*80)
regional_analytics = simulator.calculate_regional_analytics(shipments_df)
print(regional_analytics)

print("\n" + "="*80)
print("CARRIER ANALYTICS")
print("="*80)
carrier_analytics = simulator.calculate_carrier_analytics(shipments_df)
print(carrier_analytics)

# Save analytics to CSV
regional_analytics.to_csv('/home/claude/regional_analytics.csv')
carrier_analytics.to_csv('/home/claude/carrier_analytics.csv')
print("\n✓ Analytics saved to regional_analytics.csv and carrier_analytics.csv")
