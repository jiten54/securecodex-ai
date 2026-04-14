import React, { useState, useEffect } from 'react';
import { Upload, FileCode, Play, Download, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import api from '../lib/api';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface FileRecord {
  id: number;
  filename: string;
  created_at: string;
}

interface JobRecord {
  id: number;
  file_id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  level: string;
  created_at: string;
}

const Dashboard = () => {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [jobs, setJobs] = useState<Record<number, JobRecord>>({});
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = async () => {
    try {
      // Note: Backend doesn't have a list files endpoint yet, but we can infer from jobs or just handle uploads
      // For now, let's assume we might have one or just track local state
    } catch (err) {
      console.error(err);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    setUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', acceptedFiles[0]);

    try {
      const response = await api.post('/files/upload', formData);
      setFiles(prev => [response.data, ...prev]);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/x-python': ['.py'], 'text/javascript': ['.js'] },
    multiple: false
  } as any);

  const triggerProcess = async (fileId: number, level: string = 'medium') => {
    try {
      const response = await api.post(`/process/${fileId}`, { level });
      setJobs(prev => ({ ...prev, [response.data.id]: response.data }));
      pollJobStatus(response.data.id);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Processing failed');
    }
  };

  const pollJobStatus = (jobId: number) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`);
        setJobs(prev => ({ ...prev, [jobId]: response.data }));
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 2000);
  };

  const handleDownload = async (jobId: number) => {
    try {
      const response = await api.get(`/files/download/${jobId}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `obfuscated_${jobId}.py`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      setError('Download failed');
    }
  };

  const getJobForFile = (fileId: number) => {
    return Object.values(jobs).find((j: any) => j.file_id === fileId);
  };

  return (
    <div className="max-w-6xl mx-auto pt-24 px-6 pb-12">
      <header className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-2">Code Obfuscation</h1>
        <p className="text-muted-foreground">Upload your Python or JavaScript files to secure them.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Section */}
        <div className="lg:col-span-1">
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer h-64",
              isDragActive ? "border-white bg-white/5" : "border-border hover:border-muted-foreground",
              uploading && "opacity-50 pointer-events-none"
            )}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <Loader2 className="w-10 h-10 animate-spin mb-4 text-muted-foreground" />
            ) : (
              <Upload className="w-10 h-10 mb-4 text-muted-foreground" />
            )}
            <p className="font-medium">
              {isDragActive ? "Drop file here" : "Click or drag file to upload"}
            </p>
            <p className="text-xs text-muted-foreground mt-2">Supports .py and .js (Max 5MB)</p>
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-500 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Files & Jobs List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          <AnimatePresence>
            {files.length === 0 && (
              <p className="text-muted-foreground text-sm italic">No files uploaded yet.</p>
            )}
            {files.map((file) => {
              const job: any = getJobForFile(file.id);
              return (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-card border border-border rounded-xl p-4 flex items-center justify-between group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                      <FileCode className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium text-sm">{file.filename}</h3>
                      <p className="text-xs text-muted-foreground">
                        {new Date(file.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Job Status or Action */}
                    {job ? (
                      <div className="flex items-center gap-3">
                        {(() => {
                          switch (job.status) {
                            case 'pending':
                            case 'processing':
                              return (
                                <div className="flex items-center gap-2 text-xs text-yellow-500 font-medium">
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                  Processing...
                                </div>
                              );
                            case 'completed':
                              return (
                                <div className="flex items-center gap-2">
                                  <span className="text-xs text-green-500 font-medium flex items-center gap-1">
                                    <CheckCircle2 className="w-3 h-3" />
                                    Ready
                                  </span>
                                  <button
                                    onClick={() => handleDownload(job.id)}
                                    className="p-2 hover:bg-secondary rounded-lg transition-colors"
                                    title="Download"
                                  >
                                    <Download className="w-4 h-4" />
                                  </button>
                                </div>
                              );
                            case 'failed':
                              return (
                                <span className="text-xs text-red-500 font-medium flex items-center gap-1">
                                  <AlertCircle className="w-3 h-3" />
                                  Failed
                                </span>
                              );
                          }
                        })()}
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <select 
                          className="bg-secondary text-xs rounded-lg px-2 py-1 border-none outline-none"
                          id={`level-${file.id}`}
                        >
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                        </select>
                        <button
                          onClick={() => {
                            const level = (document.getElementById(`level-${file.id}`) as HTMLSelectElement).value;
                            triggerProcess(file.id, level);
                          }}
                          className="flex items-center gap-2 bg-white text-black text-xs font-bold px-4 py-2 rounded-lg hover:bg-neutral-200 transition-colors"
                        >
                          <Play className="w-3 h-3 fill-current" />
                          Process
                        </button>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
