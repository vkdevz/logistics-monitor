"""
Real-Time Logistics Bottleneck Monitor
Advanced Analytics Engine
Calculates delays, financial impact, bottleneck hotspots, and trend analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class LogisticsAnalytics:
    def __init__(self, csv_path):
        """Load shipment data"""
        self.df = pd.read_csv(csv_path)
        self.df['Ship_Date'] = pd.to_datetime(self.df['Ship_Date'])
        
    def calculate_delay_by_region(self):
        """Calculate average delay per region with detailed breakdown"""
        print("\n" + "="*100)
        print("1. AVERAGE DELAY PER REGION (Detailed Breakdown)")
        print("="*100)
        
        delay_by_region = self.df.groupby('Region').agg({
            'Delay_Hours': ['mean', 'median', 'min', 'max', 'std'],
            'Shipment_ID': 'count'
        }).round(2)
        
        delay_by_region.columns = ['Avg_Delay', 'Median_Delay', 'Min_Delay', 'Max_Delay', 'Std_Dev', 'Shipment_Count']
        
        print(delay_by_region)
        print(f"\n→ INSIGHT: {delay_by_region['Avg_Delay'].idxmax()} region has highest avg delay ({delay_by_region['Avg_Delay'].max():.1f}h)")
        return delay_by_region
    
    def calculate_financial_loss_hourly(self):
        """Calculate financial loss per hour of delay globally and by region"""
        print("\n" + "="*100)
        print("2. FINANCIAL LOSS PER HOUR OF DELAY")
        print("="*100)
        
        # Global calculation
        total_loss = self.df['Financial_Loss_USD'].sum()
        total_delay_hours = self.df['Delay_Hours'].sum()
        loss_per_hour_global = total_loss / total_delay_hours if total_delay_hours > 0 else 0
        
        print(f"\nGLOBAL METRICS:")
        print(f"  • Total Financial Loss: ${total_loss:,.2f}")
        print(f"  • Total Delay Hours: {total_delay_hours:,.1f} hours")
        print(f"  • Loss per Hour (Global): ${loss_per_hour_global:,.2f}")
        
        # By region
        print(f"\nBY REGION:")
        regional_loss = self.df.groupby('Region').agg({
            'Financial_Loss_USD': 'sum',
            'Delay_Hours': 'sum',
            'Shipment_ID': 'count'
        }).round(2)
        
        regional_loss['Loss_Per_Hour'] = (regional_loss['Financial_Loss_USD'] / regional_loss['Delay_Hours']).round(2)
        regional_loss.columns = ['Total_Loss_USD', 'Total_Delay_Hours', 'Shipment_Count', 'Loss_Per_Hour_USD']
        
        print(regional_loss)
        
        # By carrier
        print(f"\nBY CARRIER (Top 10):")
        carrier_loss = self.df.groupby('Carrier').agg({
            'Financial_Loss_USD': 'sum',
            'Delay_Hours': 'sum',
            'Shipment_ID': 'count'
        }).round(2)
        
        carrier_loss['Loss_Per_Hour'] = (carrier_loss['Financial_Loss_USD'] / carrier_loss['Delay_Hours']).round(2)
        carrier_loss.columns = ['Total_Loss_USD', 'Total_Delay_Hours', 'Shipment_Count', 'Loss_Per_Hour_USD']
        carrier_loss = carrier_loss.sort_values('Total_Loss_USD', ascending=False)
        
        print(carrier_loss.head(10))
        
        return {
            'global': loss_per_hour_global,
            'by_region': regional_loss,
            'by_carrier': carrier_loss
        }
    
    def identify_bottlenecks(self):
        """Identify critical bottleneck routes and regions"""
        print("\n" + "="*100)
        print("3. CRITICAL BOTTLENECK ANALYSIS")
        print("="*100)
        
        # Route analysis
        route_metrics = self.df.groupby('Route').agg({
            'Delay_Hours': 'mean',
            'Financial_Loss_USD': 'sum',
            'Shipment_ID': 'count'
        }).round(2)
        
        route_metrics.columns = ['Avg_Delay', 'Total_Loss', 'Shipment_Count']
        route_metrics['Delay_Rate_%'] = (self.df.groupby('Route')['Status'].apply(
            lambda x: (x.isin(['Delayed', 'Critical Delay'])).sum() / len(x) * 100
        )).round(2)
        
        route_metrics = route_metrics.sort_values('Total_Loss', ascending=False)
        
        print(f"\nTOP 15 BOTTLENECK ROUTES (by Financial Loss):")
        print(route_metrics.head(15))
        
        # Status distribution
        print(f"\n\nSHIPMENT STATUS DISTRIBUTION:")
        status_dist = self.df['Status'].value_counts()
        status_pct = (status_dist / len(self.df) * 100).round(2)
        
        for status in status_dist.index:
            print(f"  • {status}: {status_dist[status]:,} shipments ({status_pct[status]:.1f}%)")
        
        return route_metrics
    
    def trend_analysis(self):
        """Analyze delay trends over the past 7 days"""
        print("\n" + "="*100)
        print("4. DELAY TREND ANALYSIS (7-Day Window)")
        print("="*100)
        
        self.df['Date'] = self.df['Ship_Date'].dt.date
        daily_trends = self.df.groupby('Date').agg({
            'Delay_Hours': ['mean', 'sum'],
            'Financial_Loss_USD': 'sum',
            'Shipment_ID': 'count'
        }).round(2)
        
        daily_trends.columns = ['Avg_Delay_Hours', 'Total_Delay_Hours', 'Total_Loss_USD', 'Shipment_Count']
        
        print(daily_trends)
        
        print(f"\nTREND INSIGHT:")
        avg_delay_trend = daily_trends['Avg_Delay_Hours'].values
        if len(avg_delay_trend) > 1:
            trend = "↑ INCREASING" if avg_delay_trend[-1] > avg_delay_trend[0] else "↓ DECREASING"
            change = abs(((avg_delay_trend[-1] - avg_delay_trend[0]) / avg_delay_trend[0]) * 100)
            print(f"  • Average delay is {trend} by {change:.1f}% over 7 days")
        
        return daily_trends
    
    def cost_optimization_opportunities(self):
        """Identify opportunities to save 10% in shipping costs"""
        print("\n" + "="*100)
        print("5. COST OPTIMIZATION OPPORTUNITIES")
        print("="*100)
        
        total_loss = self.df['Financial_Loss_USD'].sum()
        potential_savings_10pct = total_loss * 0.10
        
        print(f"\nCURRENT FINANCIAL IMPACT:")
        print(f"  • Total Financial Loss: ${total_loss:,.2f}")
        print(f"  • Potential 10% Savings Target: ${potential_savings_10pct:,.2f}")
        
        # Opportunity 1: Reduce delays in worst-performing regions
        print(f"\nOPPORTUNITY #1 - Focus on High-Loss Regions:")
        region_loss = self.df.groupby('Region')['Financial_Loss_USD'].sum().sort_values(ascending=False)
        worst_region = region_loss.idxmax()
        worst_region_loss = region_loss.max()
        savings_from_worst = worst_region_loss * 0.15  # 15% improvement target
        print(f"  • {worst_region} accounts for ${worst_region_loss:,.2f} in losses")
        print(f"  • 15% reduction in {worst_region} delays = ${savings_from_worst:,.2f} saved")
        
        # Opportunity 2: Optimize carrier selection
        print(f"\nOPPORTUNITY #2 - Optimize Carrier Selection:")
        carrier_performance = self.df.groupby('Carrier').agg({
            'Delay_Hours': 'mean',
            'Financial_Loss_USD': 'sum'
        }).sort_values('Delay_Hours')
        
        best_carrier = carrier_performance.index[0]
        worst_carrier = carrier_performance.index[-1]
        carrier_loss_diff = carrier_performance.loc[worst_carrier, 'Financial_Loss_USD'] - carrier_performance.loc[best_carrier, 'Financial_Loss_USD']
        
        print(f"  • Best performer: {best_carrier} (avg {carrier_performance.loc[best_carrier, 'Delay_Hours']:.1f}h delay)")
        print(f"  • Worst performer: {worst_carrier} (avg {carrier_performance.loc[worst_carrier, 'Delay_Hours']:.1f}h delay)")
        print(f"  • Consolidating to top 3 carriers = ${carrier_loss_diff * 0.5:,.2f} potential savings")
        
        # Opportunity 3: Route optimization
        print(f"\nOPPORTUNITY #3 - Route Optimization:")
        route_loss = self.df.groupby('Route')['Financial_Loss_USD'].sum().sort_values(ascending=False)
        critical_routes = route_loss.head(5)
        route_savings = critical_routes.sum() * 0.20  # 20% improvement from rerouting
        print(f"  • Top 5 problem routes account for ${critical_routes.sum():,.2f} in losses")
        print(f"  • 20% improvement via rerouting = ${route_savings:,.2f} saved")
        
        # Opportunity 4: Proactive delay mitigation
        print(f"\nOPPORTUNITY #4 - Proactive Delay Mitigation:")
        delayed_shipments = self.df[self.df['Status'].isin(['Delayed', 'Critical Delay'])]
        avg_delayed_loss = delayed_shipments['Financial_Loss_USD'].mean()
        count_delayed = len(delayed_shipments)
        mitigation_savings = (count_delayed * 0.25) * avg_delayed_loss  # 25% of delays prevented
        print(f"  • {count_delayed} delayed/critical shipments = ${delayed_shipments['Financial_Loss_USD'].sum():,.2f} loss")
        print(f"  • Preventing 25% of delays = ${mitigation_savings:,.2f} saved")
        
        return {
            'total_loss': total_loss,
            'target_savings': potential_savings_10pct,
            'opportunity_sum': savings_from_worst + (carrier_loss_diff * 0.5) + route_savings + mitigation_savings
        }

# Run complete analysis
if __name__ == "__main__":
    print("\n" + "🔴 "*40)
    print("REAL-TIME LOGISTICS BOTTLENECK MONITOR - ANALYTICS REPORT")
    print("Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🔴 "*40)
    
    analytics = LogisticsAnalytics()
    
    # Execute all analyses
    delay_by_region = analytics.calculate_delay_by_region()
    financial_loss = analytics.calculate_financial_loss_hourly()
    bottlenecks = analytics.identify_bottlenecks()
    trends = analytics.trend_analysis()
    opportunities = analytics.cost_optimization_opportunities()
    
    print("\n" + "="*100)
    print("SUMMARY & NEXT STEPS")
    print("="*100)
    print(f"✓ Total Shipments Analyzed: {len(analytics.df):,}")
    print(f"✓ Date Range: {analytics.df['Ship_Date'].min().date()} to {analytics.df['Ship_Date'].max().date()}")
    print(f"✓ Total Financial Loss: ${opportunities['total_loss']:,.2f}")
    print(f"✓ 10% Savings Target: ${opportunities['target_savings']:,.2f}")
    print(f"✓ Identified Opportunities: ${opportunities['opportunity_sum']:,.2f}")
    print("\n→ See Dashboard Design Doc for visualization strategy")
    print("→ Load regional_analytics.csv and carrier_analytics.csv into Tableau/Power BI\n")
