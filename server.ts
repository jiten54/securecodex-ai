import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import multer from "multer";
import { v4 as uuidv4 } from "uuid";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SECRET_KEY = process.env.SECRET_KEY || "super-secret-key";
const UPLOADS_DIR = path.join(__dirname, "uploads");
const PROCESSED_DIR = path.join(__dirname, "processed");

// Ensure directories exist
[UPLOADS_DIR, PROCESSED_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

const upload = multer({ dest: UPLOADS_DIR });

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Mock DB
  const users: any[] = [];
  const files: any[] = [];
  const jobs: any[] = [];
  const apiKeys: any[] = [];

  // Auth Middleware
  const authenticate = (req: any, res: any, next: any) => {
    const authHeader = req.headers.authorization;
    const apiKey = req.headers["x-api-key"];

    if (apiKey) {
      const keyRecord = apiKeys.find(k => k.key === apiKey);
      if (keyRecord) {
        req.user = users.find(u => u.id === keyRecord.user_id);
        return next();
      }
    }

    if (authHeader) {
      const token = authHeader.split(" ")[1];
      try {
        const decoded = jwt.verify(token, SECRET_KEY) as any;
        req.user = users.find(u => u.id === decoded.id);
        if (req.user) return next();
      } catch (err) {}
    }

    res.status(401).json({ error: "Unauthorized" });
  };

  // API Routes
  app.post("/api/v1/auth/signup", async (req, res) => {
    const { email, password } = req.body;
    if (users.find(u => u.email === email)) return res.status(400).json({ error: "User already exists" });
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = { id: users.length + 1, email, password: hashedPassword };
    users.push(user);
    res.status(201).json({ id: user.id, email: user.email });
  });

  app.post("/api/v1/auth/login", async (req, res) => {
    const { email, password } = req.body;
    const user = users.find(u => u.email === email);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    const token = jwt.sign({ id: user.id, email: user.email }, SECRET_KEY, { expiresIn: "24h" });
    res.json({ access_token: token, token_type: "bearer" });
  });

  app.post("/api/v1/files/upload", authenticate, upload.single("file"), (req: any, res) => {
    if (!req.file) return res.status(400).json({ error: "No file uploaded" });
    const fileRecord = {
      id: files.length + 1,
      filename: req.file.originalname,
      filepath: req.file.path,
      user_id: req.user.id,
      created_at: new Date().toISOString()
    };
    files.push(fileRecord);
    res.status(201).json(fileRecord);
  });

  app.post("/api/v1/process/:fileId", authenticate, (req: any, res) => {
    const fileId = parseInt(req.params.fileId);
    const file = files.find(f => f.id === fileId && f.user_id === req.user.id);
    if (!file) return res.status(404).json({ error: "File not found" });

    const job = {
      id: jobs.length + 1,
      file_id: fileId,
      status: "processing",
      level: req.body.level || "medium",
      created_at: new Date().toISOString()
    };
    jobs.push(job);

    // Simulate processing
    setTimeout(() => {
      const content = fs.readFileSync(file.filepath, "utf-8");
      // Simple mock obfuscation: reverse lines or something
      const obfuscated = "# Obfuscated by SecureCodeX\n" + content.split("").reverse().join("");
      const processedPath = path.join(PROCESSED_DIR, `${uuidv4()}.py`);
      fs.writeFileSync(processedPath, obfuscated);
      
      job.status = "completed";
      (job as any).processed_path = processedPath;
    }, 5000);

    res.status(202).json(job);
  });

  app.get("/api/v1/jobs/:jobId", authenticate, (req: any, res) => {
    const job = jobs.find(j => j.id === parseInt(req.params.jobId));
    if (!job) return res.status(404).json({ error: "Job not found" });
    res.json(job);
  });

  app.get("/api/v1/files/download/:jobId", authenticate, (req: any, res) => {
    const job = jobs.find(j => j.id === parseInt(req.params.jobId));
    if (!job || job.status !== "completed") return res.status(404).json({ error: "File not ready" });
    res.download((job as any).processed_path, "obfuscated_code.py");
  });

  app.post("/api/v1/ai/analyze", authenticate, async (req: any, res) => {
    const { code } = req.body;
    if (!code) return res.status(400).json({ error: "No code provided" });

    // Rule-based analysis
    const sensitive = [];
    if (code.includes("api_key") || code.includes("sk-")) sensitive.push("Potential API Key detected");
    if (code.includes("password")) sensitive.push("Hardcoded password detected");

    const complexity = {
      lines_of_code: code.split("\n").length,
      function_count: (code.match(/def /g) || []).length,
      variable_count: (code.match(/=/g) || []).length
    };

    let recommended_level = "low";
    if (sensitive.length > 0) recommended_level = "high";
    else if (complexity.function_count > 5) recommended_level = "medium";

    let ai_explanation = "Rule-based analysis complete.";

    if (process.env.GEMINI_API_KEY) {
      try {
        const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
        const result = await ai.models.generateContent({
          model: "gemini-3-flash-preview",
          contents: `Analyze this code for security risks and obfuscation needs: ${code.substring(0, 2000)}`
        });
        ai_explanation = result.text || "No explanation generated.";
      } catch (err) {}
    }

    res.json({
      sensitive_findings: sensitive,
      critical_functions: [],
      complexity,
      recommended_level,
      reasons: sensitive.length > 0 ? ["Sensitive data found"] : ["Standard complexity"],
      ai_explanation
    });
  });

  app.post("/api/v1/files/keys", authenticate, (req: any, res) => {
    const newKey = {
      id: apiKeys.length + 1,
      key: `scx_${uuidv4()}`,
      user_id: req.user.id,
      created_at: new Date().toISOString()
    };
    apiKeys.push(newKey);
    res.status(201).json({ api_key: newKey.key });
  });

  app.get("/api/v1/files/keys", authenticate, (req: any, res) => {
    const userKeys = apiKeys.filter(k => k.user_id === req.user.id);
    res.json(userKeys);
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
