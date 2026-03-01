import React, { useEffect, useState } from 'react';
import { FileText, Download, Eye, Loader2 } from 'lucide-react';

const Reports = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Mock data for now since we don't have a list endpoint yet
        // In real implementation: 
        // const fetchReports = async () => { ... }
        // fetchReports();

        setTimeout(() => {
            setReports([
                { id: '1', title: 'Monthly Sales Report', created_at: '2023-10-01', status: 'completed' },
                { id: '2', title: 'Q3 Performance Review', created_at: '2023-09-15', status: 'completed' },
            ]);
            setLoading(false);
        }, 1000);
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
                    <div className="card-title">Reports Library</div>
                    <div style={{ fontSize: '20px', fontWeight: 600 }}>Executive-ready narratives with visuals</div>
                </div>
                <button className="button-primary">Generate new report</button>
            </div>

            <table className="table" style={{ marginTop: '18px' }}>
                <thead>
                    <tr>
                        <th>Report</th>
                        <th>Created</th>
                        <th>Status</th>
                        <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {reports.map((report) => (
                        <tr key={report.id}>
                            <td>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <FileText className="w-4 h-4" />
                                    <div>
                                        <div style={{ fontWeight: 600 }}>{report.title}</div>
                                        <div className="muted">Olist + clickstream insights</div>
                                    </div>
                                </div>
                            </td>
                            <td className="muted">{report.created_at}</td>
                            <td>
                                <span className="pill">{report.status}</span>
                            </td>
                            <td style={{ textAlign: 'right' }}>
                                <div style={{ display: 'inline-flex', gap: '8px' }}>
                                    <button className="button-ghost" title="View">
                                        <Eye className="w-4 h-4" />
                                        View
                                    </button>
                                    <button className="button-ghost" title="Download">
                                        <Download className="w-4 h-4" />
                                        Export
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Reports;
