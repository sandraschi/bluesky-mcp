import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Bell, Inbox as InboxIcon } from "lucide-react";
import { Link } from "react-router-dom";
import { API } from "../lib/api";

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 2, staleTime: 15_000 } },
});

type Notification = {
  id?: string;
  type?: string;
  account?: { display_name?: string; acct?: string };
  status?: { content?: string };
  created_at?: string;
};

function Inner() {
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: () => fetch(API.health).then((r) => r.json()),
    refetchInterval: 15_000,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => fetch(API.notifications).then((r) => r.json()),
    refetchInterval: 30_000,
  });

  const configured = Boolean(health?.instance_configured);
  const notifications: Notification[] = data?.notifications ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 max-w-3xl"
      data-testid="inbox-page"
    >
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-zinc-100">Inbox</h1>
        <p className="text-sm text-zinc-400 mt-0.5">
          Bluesky notifications — mentions, follows, boosts.
        </p>
      </div>

      {!configured && (
        <div
          className="mb-4 rounded-xl border-2 border-red-500/50 bg-red-950/30 p-4"
          data-testid="onboarding-banner"
        >
          <p className="text-sm text-rose-100/80 mb-3">
            Notifications come from your Bluesky account. Connect one to see
            mentions, follows and boosts here.
          </p>
          <Link
            to="/settings"
            className="inline-flex items-center justify-center rounded-lg bg-red-600 hover:bg-red-500 px-4 py-2.5 text-sm font-bold text-white"
            data-testid="onboarding-cue"
          >
            Connect Bluesky
          </Link>
        </div>
      )}

      {configured && isLoading && (
        <p className="text-sm text-zinc-400">Loading notifications…</p>
      )}

      {configured && !isLoading && notifications.length === 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-10 text-center">
          <Bell size={36} className="mx-auto mb-3 text-zinc-700" />
          <p className="text-sm text-zinc-400">No notifications yet.</p>
        </div>
      )}

      <div className="space-y-3">
        {notifications.map((n, i) => (
          <div
            key={n.id ?? i}
            className="bg-zinc-900 border border-zinc-800 rounded-lg p-4"
            data-testid="inbox-item"
          >
            <div className="flex items-center gap-2 mb-2 text-sm">
              <InboxIcon size={14} className="text-violet-400" />
              <span className="text-violet-300">
                {n.type ?? "notification"}
              </span>
              <span className="text-zinc-400 ml-auto">
                {n.created_at?.slice(0, 19) ?? ""}
              </span>
            </div>
            {n.account && (
              <p className="text-sm text-zinc-400 mb-1">
                @{n.account.acct ?? n.account.display_name}
                {n.account.display_name && (
                  <span className="text-zinc-400">
                    {" "}
                    ({n.account.display_name})
                  </span>
                )}
              </p>
            )}
            {n.status?.content && (
              <p className="text-sm text-zinc-300 whitespace-pre-wrap">
                {String(n.status.content).replace(/<[^>]+>/g, "")}
              </p>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default function Inbox() {
  return (
    <QueryClientProvider client={qc}>
      <Inner />
    </QueryClientProvider>
  );
}
