import React, { useEffect, useState } from 'react';
import QueryInput from '../components/QueryInput';
import ChartViewer from '../components/ChartViewer';
import { queryService, dataSourceService } from '../services/api';
import { AlertCircle, CheckCircle2, Database, Sparkles } from 'lucide-react';

const Analysis = () => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dataSources, setDataSources] = useState([]);
    const [selectedDataSourceId, setSelectedDataSourceId] = useState('');

    useEffect(() => {
        const loadSources = async () => {
            try {
                const response = await dataSourceService.list();
                const sources = response.data || [];
                setDataSources(sources);
                if (sources.length && !selectedDataSourceId) {
                    setSelectedDataSourceId(sources[0].id);
                }
            } catch (err) {
                console.error('Failed to load data sources', err);
            }
        };
        loadSources();
    }, [selectedDataSourceId]);

    const handleAnalyze = async (query) => {
        if (!selectedDataSourceId) {
            setError('Please select a data source before running analysis.');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await queryService.analyze({
                natural_language_query: query,
                data_source_id: selectedDataSourceId,
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred while analyzing the query.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="grid-2">
            <div className="card">
                <div className="card-title">Analysis Console</div>
                <h1 style={{ fontSize: '22px', fontWeight: 600, marginTop: '10px' }}>
                    Ask questions across orders, shipping, payments, and clickstream.
                </h1>
                <p className="muted" style={{ marginTop: '6px' }}>
                    The assistant will generate SQL, validate safety, and return narrative insights with the raw results.
                </p>

                <div style={{ display: 'grid', gap: '14px', marginTop: '18px' }}>
                    <label className="input-shell">
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <Database className="w-4 h-4" />
                            <span style={{ fontWeight: 600 }}>Data source</span>
                        </div>
                        <select
                            value={selectedDataSourceId}
                            onChange={(e) => setSelectedDataSourceId(e.target.value)}
                            style={{ marginTop: '8px' }}
                        >
                            {dataSources.length === 0 && <option value="">No data sources found</option>}
                            {dataSources.map((source) => (
                                <option key={source.id} value={source.id}>
                                    {source.name}
                                </option>
                            ))}
                        </select>
                    </label>

                    <QueryInput onAnalyze={handleAnalyze} isLoading={loading} />
                </div>

                {error && (
                    <div className="card" style={{ borderColor: '#f3c2c2', background: '#fff5f5' }}>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                            <AlertCircle className="w-5 h-5" />
                            <div>
                                <div style={{ fontWeight: 600 }}>Analysis Failed</div>
                                <div className="muted">{error}</div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="card">
                <div className="card-title">Example Questions</div>
                <div style={{ display: 'grid', gap: '10px', marginTop: '12px' }}>
                    <div className="pill">What is AOV by state and delivery delay last month?</div>
                    <div className="pill">Which product categories have the highest late deliveries?</div>
                    <div className="pill">Show conversion rate by traffic source and device.</div>
                    <div className="pill">How do review scores change with delivery time?</div>
                    <div className="pill">Which sellers contribute most to refunds?</div>
                </div>
                <div style={{ marginTop: '18px' }}>
                    <div className="card-title">Pipeline</div>
                    <div style={{ display: 'grid', gap: '10px', marginTop: '10px' }}>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <Sparkles className="w-4 h-4" />
                            <div>
                                <div style={{ fontWeight: 600 }}>Intent + entity extraction</div>
                                <div className="muted">Metrics, dimensions, filters, time ranges</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <Sparkles className="w-4 h-4" />
                            <div>
                                <div style={{ fontWeight: 600 }}>SQL generation + validation</div>
                                <div className="muted">Read-only, schema-aware SQL</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <Sparkles className="w-4 h-4" />
                            <div>
                                <div style={{ fontWeight: 600 }}>Narrative + visual synthesis</div>
                                <div className="muted">Summary, key points, recommended actions</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {result && (
                <div className="card" style={{ gridColumn: '1 / -1' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <CheckCircle2 className="w-5 h-5" />
                        <div style={{ fontWeight: 600, fontSize: '18px' }}>Analysis Results</div>
                    </div>
                    <div style={{ marginTop: '12px', display: 'grid', gap: '10px' }}>
                        <div style={{ fontSize: '18px', fontWeight: 600 }}>
                            {result.narrative?.summary || 'Summary not available yet.'}
                        </div>
                        {result.narrative?.key_points && (
                            <div className="grid-2">
                                {result.narrative.key_points.map((point, index) => (
                                    <div key={index} className="card" style={{ margin: 0 }}>
                                        {point}
                                    </div>
                                ))}
                            </div>
                        )}
                        {result.generated_sql && (
                            <div className="card" style={{ background: '#f7fafb' }}>
                                <div className="card-title">Generated SQL</div>
                                <pre style={{ marginTop: '10px', whiteSpace: 'pre-wrap' }}>{result.generated_sql}</pre>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {result?.results?.length > 0 && (
                <div className="card" style={{ gridColumn: '1 / -1' }}>
                    <div className="card-title">Top Results</div>
                    <table className="table" style={{ marginTop: '12px' }}>
                        <thead>
                            <tr>
                                {Object.keys(result.results[0]).map((key) => (
                                    <th key={key}>{key}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {result.results.slice(0, 10).map((row, idx) => (
                                <tr key={idx}>
                                    {Object.keys(row).map((key) => (
                                        <td key={key}>{String(row[key])}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {result?.chart_config && (
                <div style={{ gridColumn: '1 / -1' }}>
                    <ChartViewer chartJson={result.chart_config} />
                </div>
            )}
        </div>
    );
};

export default Analysis;
