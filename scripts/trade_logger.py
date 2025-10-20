
"""trade_logger.py

AgentX-ready logger to append executions to CSV.
- log_trades(results, csv_path='logs/trades.csv')
"""
from typing import List, Dict, Any
import csv, os
from datetime import datetime

def tool(name=None, description=None):
    def _dec(f):
        return f
    return _dec

@tool(name='Trade Logger', description='Append executions to CSV')
def log_trades(results: List[Dict[str, Any]], csv_path: str = 'logs/trades.csv') -> str:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    write_header = not os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['timestamp','order_id','client_order_id','symbol','side','filled_qty','avg_price','notional','status'])
        for r in results:
            writer.writerow([datetime.utcnow().isoformat(), r.get('order_id'), r.get('client_order_id'), r.get('symbol'), r.get('side'), r.get('filled_qty'), r.get('avg_price'), r.get('notional'), r.get('status')])
    return csv_path

if __name__ == '__main__':
    sample = [{'client_order_id':'id1','order_id':'MOCK-1','symbol':'RELIANCE.NS','side':'BUY','filled_qty':1,'avg_price':2600,'notional':2600,'status':'FILLED'}]
    print(log_trades(sample, 'logs/demo_trades.csv'))
