import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

const QueryInput = ({ onAnalyze, isLoading }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        onAnalyze(query);
    };

    return (
        <div className="input-shell">
            <form onSubmit={handleSubmit} className="relative">
                <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question (e.g., 'Show AOV by state and delivery delay last month')"
                    className="h-28 resize-none pr-14"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={!query.trim() || isLoading}
                    className="button-primary"
                    style={{ position: 'absolute', right: '14px', bottom: '12px' }}
                >
                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    Run analysis
                </button>
            </form>
        </div>
    );
};

export default QueryInput;
