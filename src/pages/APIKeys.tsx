import React, { useState, useEffect } from 'react';
import { Key, Plus, Copy, Check, Trash2, Loader2, AlertCircle } from 'lucide-react';
import api from '../lib/api';
import { motion, AnimatePresence } from 'framer-motion';

interface APIKey {
  id: number;
  key: string;
  created_at: string;
}

const APIKeys = () => {
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [copied, setCopied] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchKeys = async () => {
    setLoading(true);
    try {
      const response = await api.get('/files/keys');
      setKeys(response.data);
    } catch (err: any) {
      setError('Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const response = await api.post('/files/keys');
      // The backend returns the full key only once
      alert(`Your new API Key is: ${response.data.api_key}\n\nPlease copy it now, as it won't be shown again.`);
      fetchKeys();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create key');
    } finally {
      setCreating(false);
    }
  };

  const copyToClipboard = (text: string, id: number) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto pt-24 px-6 pb-12">
      <header className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-bold tracking-tight mb-2">API Keys</h1>
          <p className="text-muted-foreground">Manage keys for SaaS integration and CLI tools.</p>
        </div>
        <button
          onClick={handleCreate}
          disabled={creating}
          className="bg-white text-black font-bold px-6 py-3 rounded-xl hover:bg-neutral-200 transition-all flex items-center gap-2 disabled:opacity-50"
        >
          {creating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
          Generate Key
        </button>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-500 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="space-y-4">
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <AnimatePresence>
            {keys.length === 0 && (
              <div className="text-center py-12 border-2 border-dashed border-border rounded-2xl opacity-50">
                <Key className="w-12 h-12 mx-auto mb-4" />
                <p className="text-sm">No API keys generated yet.</p>
              </div>
            )}
            {keys.map((key) => (
              <motion.div
                key={key.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-card border border-border rounded-xl p-6 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                    <Key className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-mono text-sm">{key.key}</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      Created on {new Date(key.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyToClipboard(key.key, key.id)}
                    className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-white"
                    title="Copy Key"
                  >
                    {copied === key.id ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                  </button>
                  <button
                    className="p-2 hover:bg-red-500/10 rounded-lg transition-colors text-muted-foreground hover:text-red-500"
                    title="Revoke Key"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      <div className="mt-12 p-6 bg-secondary/30 border border-border rounded-2xl">
        <h3 className="text-sm font-bold mb-2 uppercase tracking-widest">Usage Guide</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Include your API key in the request header to authenticate your requests:
        </p>
        <div className="bg-black p-4 rounded-xl font-mono text-xs text-green-400 overflow-x-auto">
          curl -H "X-API-Key: YOUR_KEY" https://api.securecodex.com/v1/files/upload
        </div>
      </div>
    </div>
  );
};

export default APIKeys;
