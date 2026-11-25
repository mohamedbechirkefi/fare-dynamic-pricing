// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Types and limits shared by the sandbox worker and the page.
import type { Policy, Scenario } from "./engine";

export const MAX_STREAMS = 2000;
export const ARMS = ["FIX", "OCC", "DRP"] as const;
export type Arm = (typeof ARMS)[number];

export interface ArmSummary {
  revenue_mean: number;
  revenue_sd: number;
  sell_through_mean: number;
  availability_mean: number;
  volatility_mean: number;
}
export interface ContrastSummary {
  arm: Arm;
  mean: number;
  lo: number;
  hi: number;
  share_loses: number;
}
export interface SandboxResult {
  seed: number;
  n: number;
  scenario: Scenario;
  policies: Record<Arm, Policy>;
  first: Record<Arm, { prices: number[]; stock: number[] }>;
  arms: Record<Arm, ArmSummary>;
  contrasts: ContrastSummary[];
}

export type WorkerRequest =
  | { type: "run"; seed: number; n: number; scenario: Scenario; policies: Record<Arm, Policy> }
  | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; result: SandboxResult }
  | { type: "cancelled" }
  | { type: "error"; message: string };
