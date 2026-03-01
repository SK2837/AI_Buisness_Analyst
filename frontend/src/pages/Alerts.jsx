import React, { useEffect, useState } from 'react';
import { Bell, Plus, Trash2, Loader2 } from 'lucide-react';
import { alertService } from '../services/api';

const Alerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await alertService.list();
                setAlerts(response.data);
            } catch (err) {
                console.error('Failed to fetch alerts', err);
            } finally {
                setLoading(false);
            }
        };
        fetchAlerts();
    }, []);

    if (loading) {
        return (
            <div className="card" style={{ display: 'grid', placeItems: 'center', minHeight: '220px' }}>
                <Loader2 className="w-8 h-8 animate-spin" />
            </div>
        );
    }

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <div className="card-title">Alert Center</div>
                    <div style={{ fontSize: '20px', fontWeight: 600 }}>Monitor drops, spikes, and shipping SLA</div>
                </div>
                <button className="button-primary">
                    <Plus className="w-4 h-4" />
                    Create alert
                </button>
            </div>

            <div style={{ marginTop: '18px', display: 'grid', gap: '12px' }}>
                {alerts.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center' }}>
                        <Bell className="w-10 h-10" style={{ margin: '0 auto 10px' }} />
                        <div style={{ fontWeight: 600 }}>No alerts configured</div>
                        <div className="muted">Create your first alert to monitor key metrics.</div>
                    </div>
                ) : (
                    alerts.map((alert) => (
                        <div key={alert.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <div style={{ fontWeight: 600 }}>{alert.name}</div>
                                <div className="muted">{alert.condition_sql}</div>
                                <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                                    <span className="pill">{alert.schedule_cron}</span>
                                    <span className="pill">{alert.is_active ? 'Active' : 'Inactive'}</span>
                                </div>
                            </div>
                            <button className="button-ghost">
                                <Trash2 className="w-4 h-4" />
                                Remove
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Alerts;
