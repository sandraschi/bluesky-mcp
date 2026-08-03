import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import { motion } from "framer-motion";
import { CheckCircle, Cpu, Loader2, XCircle } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { API } from "../lib/api";
import { LLM_PROVIDERS, probeProviders } from "../lib/provider";
import { useLLMStore } from "../store/llm";

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

function Inner() {
  const setOllamaUrl = useLLMStore((s) => s.setOllamaUrl);
  const [llmProvider, setLlmProvider] = useState<string>(
    () => localStorage.getItem("llm_provider") || "",
  );
  const [llmModel, setLlmModel] = useState<string>(
    () => localStorage.getItem("llm_model") || "",
  );

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: () => fetch(API.health).then((r) => r.json()),
    refetchInterval: 30_000,
  });

  const { data: providers, isLoading: probing } = useQuery({
    queryKey: ["llm-providers"],
    queryFn: async () => {
      const results = await probeProviders();
      const first = LLM_PROVIDERS.find((p) => results[p.name]?.detected);
      if (first) setOllamaUrl(`http://localhost:${first.port}`);
      return { providers: results };
    },
    refetchInterval: 60_000,
  });

  const { data: llmDiscover } = useQuery({
    queryKey: ["llm-discover"],
    queryFn: () => fetch(API.llmProviders).then((r) => r.json()),
    refetchInterval: 60_000,
  });

  const activeProvider =
    LLM_PROVIDERS.find(
      (p) => p.name === llmProvider && providers?.providers?.[p.name]?.detected,
    ) ?? LLM_PROVIDERS.find((p) => providers?.providers?.[p.name]?.detected);

  const providerStatus = (name: string) => {
    const p = providers?.providers?.[name];
    if (!providers || probing)
      return { icon: Loader2, color: "text-zinc-400", label: "Probing..." };
    if (p?.detected)
      return {
        icon: CheckCircle,
        color: "text-green-400",
        label: `Detected (port ${LLM_PROVIDERS.find((x) => x.name === name)!.port})`,
      };
    return { icon: XCircle, color: "text-zinc-600", label: "Not found" };
  };

  const envRows: [string, string][] = [
    [
      "BLUESKY_DRY_RUN",
      health?.dry_run != null ? String(health.dry_run) : "1 (default)",
    ],
    [
      "BLUESKY_HANDLE / APP_PASSWORD",
      health?.instance_configured ? "(configured)" : "(not set)",
    ],
    [
      "BLUESKY_PDS",
      health?.instance_configured ? "(ready)" : "https://bsky.social (default)",
    ],
    ["Backend port", String(health?.ports?.backend ?? 10760)],
    ["Frontend port", String(health?.ports?.frontend ?? 10761)],
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 max-w-2xl"
    >
      <div className="mb-6">
        <h1 className="text-xl font-semibold">Settings</h1>
        <p className="text-sm text-zinc-400 mt-0.5">
          Server status, LLM providers, and environment
        </p>
      </div>

      {health && !health.instance_configured && (
        <div
          className="mb-6 rounded-xl border border-amber-500/40 bg-amber-500/10 p-4"
          data-testid="onboarding-cue"
        >
          <p className="text-sm font-medium text-amber-200 mb-2">
            Setup required — connect a Bluesky account (free, no credit card)
          </p>
          <ol className="text-sm text-amber-100/80 space-y-1.5 mb-2 list-decimal list-inside">
            <li>
              Create an account at{" "}
              <a
                href="https://bsky.app"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-amber-50"
              >
                bsky.app
              </a>{" "}
              (or the Bluesky app on iOS / Android / desktop)
            </li>
            <li>
              In Settings → Privacy and security →{" "}
              <a
                href="https://bsky.app/settings/app-passwords"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-amber-50"
              >
                App Passwords
              </a>{" "}
              create one named e.g.{" "}
              <code className="font-mono">bluesky-mcp</code> and copy it once
            </li>
            <li>
              Set in <code className="font-mono">.env</code>:{" "}
              <code className="font-mono">BLUESKY_HANDLE=you.bsky.social</code>{" "}
              and{" "}
              <code className="font-mono">
                BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
              </code>{" "}
              (never your main password)
            </li>
            <li>
              Restart the backend (
              <code className="font-mono">.\start.bat</code>) — this page flips
              to “Instance configured”
            </li>
          </ol>
          <p className="text-sm text-zinc-400">
            Dry-run works without any of this: drafts, approve, and publish only
            write locally until you set{" "}
            <code className="font-mono">BLUESKY_DRY_RUN=0</code>. Full guide:
            docs/ONBOARDING.md ·{" "}
            <Link to="/help" className="text-violet-400 hover:underline">
              Help page
            </Link>
          </p>
        </div>
      )}

      <div className="space-y-3 mb-8">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 flex items-center gap-3">
          {health ? (
            <CheckCircle size={16} className="text-green-400 shrink-0" />
          ) : (
            <Loader2
              size={16}
              className="text-zinc-400 animate-spin shrink-0"
            />
          )}
          <div>
            <p className="text-sm text-zinc-200">Backend</p>
            <p className="text-sm text-zinc-400">
              {health ? `${health.server} v${health.version}` : "Checking..."}
            </p>
          </div>
          <span
            className={`ml-auto text-sm px-2 py-0.5 rounded ${
              health?.dry_run
                ? "bg-amber-500/10 text-amber-400"
                : "bg-emerald-500/10 text-emerald-400"
            }`}
          >
            {health?.dry_run ? "dry-run" : "live"}
          </span>
        </div>
      </div>

      <div className="mb-8">
        <h2
          className="text-sm font-medium text-zinc-300 mb-3"
          data-testid="llm-providers-heading"
        >
          LLM Providers
        </h2>
        <div className="mb-3">
          <select
            data-testid="llm-provider-select"
            value={activeProvider?.name ?? ""}
            onChange={(e) => {
              setLlmProvider(e.target.value);
              localStorage.setItem("llm_provider", e.target.value);
              const p = LLM_PROVIDERS.find((x) => x.name === e.target.value);
              if (p) setOllamaUrl(`http://localhost:${p.port}`);
            }}
            className="w-full bg-zinc-950 border border-zinc-700 rounded px-2 py-1.5 text-sm text-zinc-300"
          >
            {!activeProvider && <option value="">No local LLM detected</option>}
            {LLM_PROVIDERS.filter(
              (p) => providers?.providers?.[p.name]?.detected,
            ).map((p) => (
              <option key={p.name} value={p.name}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          {LLM_PROVIDERS.map((p) => {
            const status = providerStatus(p.name);
            const Icon = status.icon;
            const models = providers?.providers?.[p.name]?.models;
            return (
              <div
                key={p.name}
                className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <Icon size={16} className={`${status.color} shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-zinc-200">{p.name}</p>
                    <p className="text-sm text-zinc-400">{status.label}</p>
                  </div>
                  {models && models.length > 0 && (
                    <span className="text-sm text-zinc-400 shrink-0">
                      {models.length} models
                    </span>
                  )}
                </div>
                {activeProvider?.name === p.name &&
                  models &&
                  models.length > 0 && (
                    <select
                      data-testid="llm-model-select"
                      className="mt-2 w-full bg-zinc-950 border border-zinc-700 rounded px-2 py-1 text-sm text-zinc-300 font-mono"
                      value={models.includes(llmModel) ? llmModel : models[0]}
                      onChange={(e) => {
                        setLlmModel(e.target.value);
                        localStorage.setItem("llm_model", e.target.value);
                      }}
                    >
                      {models.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  )}
              </div>
            );
          })}
        </div>

        {!activeProvider && providers && (
          <div className="mt-3 bg-amber-900/10 border border-amber-800/30 rounded-lg px-4 py-3 flex items-center gap-2">
            <Cpu size={16} className="text-amber-400 shrink-0" />
            <p className="text-sm text-amber-300">
              No local LLM detected. Install{" "}
              <a
                href="https://ollama.com"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-amber-200"
              >
                Ollama
              </a>{" "}
              or{" "}
              <a
                href="https://lmstudio.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-amber-200"
              >
                LM Studio
              </a>{" "}
              for Chat and Compose assist.
            </p>
          </div>
        )}

        {llmDiscover?.gpu?.detected && !activeProvider && (
          <div
            className="mt-3 bg-emerald-900/10 border border-emerald-800/30 rounded-lg px-4 py-3 flex items-center gap-2"
            data-testid="gpu-opportunity"
          >
            <Cpu size={16} className="text-emerald-400 shrink-0" />
            <p className="text-sm text-emerald-300">
              High-performance GPU detected ({llmDiscover.gpu.name}). Install{" "}
              <a
                href="https://ollama.com"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-emerald-200"
              >
                Ollama
              </a>{" "}
              or{" "}
              <a
                href="https://lmstudio.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-emerald-200"
              >
                LM Studio
              </a>{" "}
              to unlock free local AI features.
            </p>
          </div>
        )}
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <h2 className="text-sm font-medium text-zinc-300 mb-3">
          Environment (from health)
        </h2>
        <div className="space-y-2 text-sm font-mono">
          {envRows.map(([key, val]) => (
            <div key={key} className="flex gap-2">
              <span className="text-zinc-400 w-48 shrink-0">{key}</span>
              <span className="text-zinc-400 truncate">{val}</span>
            </div>
          ))}
        </div>
        <p className="text-sm text-zinc-400 mt-3">
          Edit <code className="text-zinc-400">.env</code> in repo root. Never
          commit secrets.
        </p>
      </div>
    </motion.div>
  );
}

export default function SettingsPage() {
  return (
    <QueryClientProvider client={qc}>
      <Inner />
    </QueryClientProvider>
  );
}
