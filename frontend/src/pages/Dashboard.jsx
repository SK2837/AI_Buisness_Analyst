import React from 'react';
import { ArrowUpRight, TrendingUp, Package, Truck, Percent } from 'lucide-react';

const Dashboard = () => {
    return (
        <div className="grid-2">
            <div className="card">
                <div className="card-title">Order Pulse</div>
                <div className="stat-value">128,492</div>
                <div className="muted">Orders processed in last 30 days</div>
                <div className="stat-change">+8.2% vs previous period</div>
                <div className="grid-3" style={{ marginTop: '18px' }}>
                    <div>
                        <div className="muted">AOV</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>$62.40</div>
                    </div>
                    <div>
                        <div className="muted">Revenue</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>$7.9M</div>
                    </div>
                    <div>
                        <div className="muted">Refund Rate</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>2.3%</div>
                    </div>
                </div>
            </div>

            <div className="card">
                <div className="card-title">Delivery Reliability</div>
                <div className="stat-value">93.4%</div>
                <div className="muted">Orders delivered on or before SLA</div>
                <div className="stat-change">+1.5% vs previous period</div>
                <div style={{ marginTop: '18px' }} className="grid-3">
                    <div>
                        <div className="muted">Avg Ship Time</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>3.2 days</div>
                    </div>
                    <div>
                        <div className="muted">Late Orders</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>6.6%</div>
                    </div>
                    <div>
                        <div className="muted">Carrier Mix</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>5 partners</div>
                    </div>
                </div>
            </div>

            <div className="card">
                <div className="card-title">Conversion Funnel</div>
                <div className="grid-3" style={{ marginTop: '18px' }}>
                    <div>
                        <div className="pill">Sessions</div>
                        <div className="stat-value" style={{ fontSize: '22px' }}>1.8M</div>
                    </div>
                    <div>
                        <div className="pill">Add to Cart</div>
                        <div className="stat-value" style={{ fontSize: '22px' }}>12.4%</div>
                    </div>
                    <div>
                        <div className="pill">Checkout</div>
                        <div className="stat-value" style={{ fontSize: '22px' }}>3.8%</div>
                    </div>
                </div>
                <div className="muted" style={{ marginTop: '8px' }}>
                    Clickstream conversion rate (UCI dataset)
                </div>
            </div>

            <div className="card">
                <div className="card-title">This Week Highlights</div>
                <div style={{ display: 'grid', gap: '14px', marginTop: '14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <TrendingUp className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Top category: Bed & Bath</div>
                            <div className="muted">Revenue +11% week over week</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Package className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Inventory risk</div>
                            <div className="muted">24 SKUs below 2-week coverage</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Truck className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Shipping costs up</div>
                            <div className="muted">Average freight +6% in Northeast</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Percent className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Promo lift</div>
                            <div className="muted">Paid search ROAS +14%</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <ArrowUpRight className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Repeat buyers</div>
                            <div className="muted">Retention cohort +3.1%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
