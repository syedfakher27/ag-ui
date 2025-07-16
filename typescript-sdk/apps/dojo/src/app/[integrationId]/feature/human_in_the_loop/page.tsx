"use client";
import React, { useState, useEffect } from "react";
import "@copilotkit/react-ui/styles.css";
import "./style.css";
import { CopilotKit, useCopilotAction, useLangGraphInterrupt, useCoAgent } from "@copilotkit/react-core";
import { TransferPortalFilters, FilterChangeHandler, AvailabilityChangeHandler } from './types';
import { CopilotChat } from "@copilotkit/react-ui";

interface HumanInTheLoopProps {
  params: Promise<{
    integrationId: string;
  }>;
}

// Position options


const HumanInTheLoop: React.FC<HumanInTheLoopProps> = ({ params }) => {
  const { integrationId } = React.use(params);

  return (
    <CopilotKit
      runtimeUrl={`/api/copilotkit/${integrationId}`}
      showDevConsole={false}
      agent="human_in_the_loop"
    >
      <TransferPortalAssistant />
    </CopilotKit>
  );
};

interface Step {
  description: string;
  status: "disabled" | "enabled" | "executing";
}

const InterruptHumanInTheLoop: React.FC<{
  event: { value: { steps: Step[] } };
  resolve: (value: string) => void;
}> = ({ event, resolve }) => {
  let initialSteps: Step[] = [];
  if (event.value && event.value.steps && Array.isArray(event.value.steps)) {
    initialSteps = event.value.steps.map((step: any) => ({
      description: typeof step === "string" ? step : step.description || "",
      status: typeof step === "object" && step.status ? step.status : "enabled",
    }));
  }

  const [localSteps, setLocalSteps] = useState<Step[]>(initialSteps);

  const handleCheckboxChange = (index: number) => {
    setLocalSteps((prevSteps) =>
      prevSteps.map((step, i) =>
        i === index
          ? {
            ...step,
            status: step.status === "enabled" ? "disabled" : "enabled",
          }
          : step,
      ),
    );
  };

  return (
    <div className="flex flex-col gap-4 w-[500px] bg-gray-100 rounded-lg p-8 mb-4">
      <div className="text-black space-y-2">
        <h2 className="text-lg font-bold mb-4">Select Steps</h2>
        {localSteps.map((step, index) => (
          <div key={index} className="text-sm flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={step.status === "enabled"}
                onChange={() => handleCheckboxChange(index)}
                className="mr-2"
              />
              <span className={step.status !== "enabled" ? "line-through" : ""}>
                {step.description}
              </span>
            </label>
          </div>
        ))}
        <button
          className="mt-4 bg-gradient-to-r from-purple-400 to-purple-600 text-white py-2 px-4 rounded cursor-pointer w-48 font-bold"
          onClick={() => {
            const selectedSteps = localSteps
              .filter((step) => step.status === "enabled")
              .map((step) => step.description);
            resolve("The user selected the following steps: " + selectedSteps.join(", "));
          }}
        >
          ✨ Perform Steps
        </button>
      </div>
    </div>
  );
};

const TransferPortalAssistant = () => {
  // const [filters, setFilters] = useState({
  //   positionGap: "PF",
  //   styleOfPlay: "Transition offense",
  //   developmentReadiness: "Multi-year potential",
  //   minutesPerGame: 23,
  //   efficiencyRating: 55,
  //   reboundBlockAssist: 54,
  //   availability: {
  //     stillAvailable: true,
  //     committed: false,
  //     draftBound: false
  //   }
  // });
  const initialFilters: TransferPortalFilters = {
    positionGap: "PF",
    styleOfPlay: "Transition offense",
    developmentReadiness: "Multi-year potential",
    minutesPerGame: 22,
    efficiencyRating: 54,
    reboundBlockAssist: 55,
    availability: {
      stillAvailable: true,
      committed: false,
      draftBound: false
    }
  };

  const { state: filters, setState: setFilters } = useCoAgent<TransferPortalFilters>(
    {
      name: "shared_state",
      initialState: initialFilters
    }
  );

  useLangGraphInterrupt({
    render: ({ event, resolve }) => <InterruptHumanInTheLoop event={event} resolve={resolve} />,
  });

  useCopilotAction({
    name: "weather",
    parameters: [
      {
        name: "city",
        type: "string",
      },
    ],
    render: ({ args, result, status }) => {
      return <StepsFeedback args={args} result={result} status={status} />;
    },
  });

  const handleFilterChange = (filterType: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleAvailabilityChange = (key: string, checked: boolean) => {
    setFilters(prev => ({
      ...prev,
      availability: {
        ...prev.availability,
        [key]: checked
      }
    }));
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Filters */}
      <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
        <div className="space-y-6">
          {/* Team Needs Focus */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Team Needs Focus</h3>
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
              value={filters.positionGap}
              onChange={(e) => handleFilterChange('positionGap', e.target.value)}
            >
              <option value="PG">PG</option>
              <option value="SG">SG</option>
              <option value="SF">SF</option>
              <option value="PF">PF</option>
              <option value="C">C</option>
            </select>
          </div>

          {/* Style of Play */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Style of Play</h3>
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
              value={filters.styleOfPlay}
              onChange={(e) => handleFilterChange('styleOfPlay', e.target.value)}
            >
              <option value="Transition offense">Transition offense</option>
              <option value="Half-court offense">Half-court offense</option>
              <option value="Defense-first">Defense-first</option>
              <option value="Balanced">Balanced</option>
            </select>
          </div>

          {/* Development Readiness */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Development Readiness</h3>
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
              value={filters.developmentReadiness}
              onChange={(e) => handleFilterChange('developmentReadiness', e.target.value)}
            >
              <option value="Immediate impact">Immediate impact</option>
              <option value="Multi-year potential">Multi-year potential</option>
              <option value="Project player">Project player</option>
            </select>
          </div>

          {/* Performance Section */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-4">Performance</h3>

            {/* Minutes/game slider */}
            <div className="mb-4">
              <label className="text-xs text-gray-600 mb-2 block">Minutes/game</label>
              <input
                type="range"
                min="0"
                max="40"
                value={filters.minutesPerGame}
                onChange={(e) => handleFilterChange('minutesPerGame',  parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>{filters.minutesPerGame}</span>
                <span>40</span>
              </div>
            </div>

            {/* Efficiency rating slider */}
            <div className="mb-4">
              <label className="text-xs text-gray-600 mb-2 block">Efficiency rating</label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.efficiencyRating}
                onChange={(e) => handleFilterChange('efficiencyRating', [0, parseInt(e.target.value)])}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>{filters.efficiencyRating}</span>
                <span>100</span>
              </div>
            </div>

            {/* Rebound/block/assist % slider */}
            <div className="mb-4">
              <label className="text-xs text-gray-600 mb-2 block">Rebound/block/assist %</label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.reboundBlockAssist}
                onChange={(e) => handleFilterChange('reboundBlockAssist', [0, parseInt(e.target.value)])}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>{filters.reboundBlockAssist}</span>
                <span>100</span>
              </div>
            </div>
          </div>

          {/* Availability Status */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Availability Status</h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.availability.stillAvailable}
                  onChange={(e) => handleAvailabilityChange('stillAvailable', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Still available</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.availability.committed}
                  onChange={(e) => handleAvailabilityChange('committed', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Committed</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.availability.draftBound}
                  onChange={(e) => handleAvailabilityChange('draftBound', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Draft-bound</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold text-gray-900">Transfer Portal Assistant</h1>
            <button className="p-2 border border-gray-300 rounded-md hover:bg-gray-50">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex">
          <div className="flex-1 p-4">
            <CopilotChat
              className="h-full rounded-lg border border-gray-200"
              labels={{
                initial: "Ask about a transfer prospect",
              }}
            />
          </div>

          {/* Player Card */}
          <div className="w-80 bg-white border-l border-gray-200 p-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Player X</h3>
                <span className="text-sm text-gray-500">C</span>
              </div>

              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gray-300 rounded-full mr-3"></div>
                <div>
                  <div className="text-sm font-medium">2 YRs</div>
                  <div className="text-xs text-gray-500">Past Team</div>
                </div>
                <div className="ml-auto">
                  <div className="text-sm font-medium">2 yo</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-lg font-bold">10.5</div>
                  <div className="text-xs text-gray-500">PPG</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold">9.4</div>
                  <div className="text-xs text-gray-500">RPG</div>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <div className="text-xs text-gray-600">Multi-year fit</div>
                <div className="text-xs text-gray-600">High rebound rate</div>
                <div className="text-xs text-gray-600">NIL value undervalued</div>
              </div>

              <div className="space-y-2">
                <button className="w-full py-2 px-4 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                  Compare to URI roster
                </button>
                <button className="w-full py-2 px-4 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                  Flag for recruiting
                </button>
                <button className="w-full py-2 px-4 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                  View HS video
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StepsFeedback = ({ args, result, status }: { args: any; result: any; status: any }) => {
  const [accepted, setAccepted] = useState<boolean | null>(null);

  return (
    <div className="flex flex-col gap-4 w-[500px] bg-gray-100 rounded-lg p-8 mb-4">
      <div className="text-black space-y-2">
        <h2 className="text-lg font-bold mb-4">Action Result</h2>
        <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
      </div>
      {accepted !== null && (
        <div className="flex justify-end">
          <div className="mt-4 bg-gray-200 text-black py-2 px-4 rounded inline-block">
            {accepted ? "✓ Accepted" : "✗ Rejected"}
          </div>
        </div>
      )}
    </div>
  );
};

export default HumanInTheLoop;