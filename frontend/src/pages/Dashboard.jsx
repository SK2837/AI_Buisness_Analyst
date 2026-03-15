import React, { useEffect, useState } from 'react';
import { TrendingUp, Package, Truck, Star, Users } from 'lucide-react';
import axios from 'axios';

const fmt = (n, prefix = '') =>
    n >= 1_000_000 ? `${prefix}${(n / 1_000_000).toFixed(1)}M`
    : n >= 1_000 ? `${prefix}${(n / 1_000).toFixed(1)}K`
    : `${prefix}${n}`;

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get('/api/v1/dashboard/kpis')
            .then(res => setData(res.data))
            .catch(() => setError('Failed to load KPIs'))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            Loading real data...
        </div>
    );

    if (error) return (
        <div className="card" style={{ textAlign: 'center', color: 'red', padding: '40px' }}>
            {error}
        </div>
    );

    const { order_pulse, delivery, top_category, order_statuses, avg_review_score, total_sellers } = data;

    return (
        <div className="grid-2">
            {/* Order Pulse */}
            <div className="card">
                <div className="card-title">Order Pulse</div>
                <div className="stat-value">{fmt(order_pulse.total_orders)}</div>
                <div className="muted">Orders processed in last 30 days</div>
                <div className="stat-change">
                    {order_pulse.order_change_pct >= 0 ? '+' : ''}{order_pulse.order_change_pct}% vs previous period
                </div>
                <div className="grid-3" style={{ marginTop: '18px' }}>
                    <div>
                        <div className="muted">AOV</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>${order_pulse.avg_order_value.toFixed(2)}</div>
                    </div>
                    <div>
                        <div className="muted">Revenue</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>{fmt(order_pulse.total_revenue, '$')}</div>
                    </div>
                    <div>
                        <div className="muted">Cancel Rate</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>{order_pulse.cancel_rate}%</div>
                    </div>
                </div>
            </div>

            {/* Delivery Reliability */}
            <div className="card">
                <div className="card-title">Delivery Reliability</div>
                <div className="stat-value">{delivery.on_time_pct}%</div>
                <div className="muted">Orders delivered on or before estimated date</div>
                <div className="grid-3" style={{ marginTop: '18px' }}>
                    <div>
                        <div className="muted">Avg Ship Time</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>{delivery.avg_ship_days} days</div>
                    </div>
                    <div>
                        <div className="muted">Late Orders</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>{delivery.late_pct}%</div>
                    </div>
                    <div>
                        <div className="muted">Total Delivered</div>
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>{fmt(delivery.total_delivered)}</div>
                    </div>
                </div>
            </div>

            {/* Order Status Breakdown */}
            <div className="card">
                <div className="card-title">Order Status Breakdown</div>
                <div style={{ display: 'grid', gap: '10px', marginTop: '14px' }}>
                    {order_statuses.map(s => (
                        <div key={s.status} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span className="pill">{s.status}</span>
                            <span style={{ fontWeight: 600 }}>{fmt(s.count)}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Highlights */}
            <div className="card">
                <div className="card-title">Highlights</div>
                <div style={{ display: 'grid', gap: '14px', marginTop: '14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <TrendingUp className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Top category: {top_category.name}</div>
                            <div className="muted">Revenue {fmt(top_category.revenue, '$')}</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Star className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Avg Review Score</div>
                            <div className="muted">{avg_review_score} / 5.0</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Users className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Active Sellers</div>
                            <div className="muted">{total_sellers} sellers on platform</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Truck className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Late deliveries</div>
                            <div className="muted">{delivery.late_pct}% of all delivered orders</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Package className="w-4 h-4" />
                        <div>
                            <div style={{ fontWeight: 600 }}>Cancellation Rate</div>
                            <div className="muted">{order_pulse.cancel_rate}% of orders canceled</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
