// @ts-nocheck
"use client";
import React, { useState, useEffect } from "react";
import "@copilotkit/react-ui/styles.css";
import "./style.css";
import { CopilotKit, useCopilotAction, useLangGraphInterrupt, useCoAgent } from "@copilotkit/react-core";
import { Play, Calendar, Users, Video as VideoIcon, Clock, FileText } from 'lucide-react';
import { FilterState, FilterChangeHandler, AvailabilityChangeHandler, TEAM_OPTIONS } from './types';
import { CopilotChat } from "@copilotkit/react-ui";
import AgentTransferUI from "@/components/agent-ui/agent_ui";
import ToolExecutionUI from "@/components/tool-ui/tool_ui";
import MultiRecipientEmailApprovalComponent from "@/components/email_approval/email_approval";
import SidebarVideoPlayer from "@/components/video_player/SidebarVideoPlayer";
import VideoResultsTable from "@/components/video_player/VideoResultsTable";

interface HumanInTheLoopProps {
  params: Promise<{
    integrationId: string;
  }>;
}

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
  const [enableVerbose, setEnableVerbose] = useState(true);
  const initialFilters: FilterState = {
    filters: {
      excludeCommitted: false
    }
  };
  const { state: filters, setState: setFilters } = useCoAgent<FilterState>(
    {
      name: "human_in_the_loop",
      initialState: initialFilters
    }
  );

  useLangGraphInterrupt({
    render: ({ event, resolve }) => <InterruptHumanInTheLoop event={event} resolve={resolve} />,
  });

  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  // For analyze_player_relevance_tool - shows selected relevant videos directly
  useCopilotAction({
  name: "analyze_player_relevance_tool",
  parameters: [
    {
      name: "gcs_links",
      type: "string",
      description: "Array of GCS links to analysis files"
    },
    {
      name: "selected_videos", 
      type: "string",
      description: "Array of selected video objects that are most relevant"
    },
    {
      name: "selection_reasoning",
      type: "string", 
      description: "Explanation of why these videos were selected"
    }
  ],
  render: ({ args, result, status }) => {
    return (
      <div className="space-y-4">
        {/* Tool Execution UI */}
        {enableVerbose && (
          <ToolExecutionUI
            toolName="analyze_player_relevance_tool"
            args={args}
            result={result}
            status={status}
          />
        )}
        
        <VideoResultsTable 
          args={{ query: result?.query || "Selected Videos" }} 
          result={result} 
          status={status}
          enableVerbose={enableVerbose}
          title="Selected Relevant Videos"
          onVideoPlay={setSelectedVideo} // Pass the video setter function
        />
      </div>
    );
  },
  });

  useCopilotAction({
    name: "shortlist_players",
    parameters: [
      {
        name: "player_ids",
        type: "string[]",
      }
    ],
    render: ({ args, result, status }) => {
      return (
      <div className="space-y-4">
        {/* Tool Execution UI */}
        {enableVerbose && (
          <ToolExecutionUI
            toolName="shortlist_players"
            args={args}
            result={result}
            status={status}
          />
        )}
        
        {/* Steps Feedback UI */}
        <StepsFeedback 
          args={args} 
          result={result} 
          status={status} 
          selectedPlayer={selectedPlayer} 
          setSelectedPlayer={setSelectedPlayer} 
        />
      </div>
    );
    },
  });

 useCopilotAction({
  name: "search_player_stats_tool",
  parameters: [
    {
      name: "query",
      type: "string",
      description: "The search query for player performance, stats, or physical traits (e.g., 'Jonah Hinton vertical jump progression')"
    },
    {
      name: "meta_data",
      type: "object",
      description: "Structured filters for precise search, e.g. { data_type: 'stats', player_name: 'jonah hinton', team: 'Rhode Island', recorded_date: 'Spring 2025' }"
    }
  ],
  render: ({ args, result, status }) => {
    return enableVerbose ? (
      <ToolExecutionUI
        toolName="search_player_stats_tool"
        args={args}
        result={result}
        status={status}
        />
      ) : null;
    },
  });
  
  useCopilotAction({
    name: "transfer_to_agent",
    parameters: [
      {
        name: "agent_name",
        type: "string",
      }
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
        <AgentTransferUI args={args} result={result} status={status} />
      ) : null;
    },
  });

  useCopilotAction({
    name: "fetch_team_name",
    parameters: [
      {
        name: "team",
        type: "string",
      }
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
         <ToolExecutionUI
            toolName="fetch_team_name"
            args={args}
            result={result}
            status={status}
          />
      ) : null;
    },
  });

  useCopilotAction({
    name: "fetch_team_official_name",
    parameters: [
      {
        name: "abbrev",
        type: "string",
      }
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
         <ToolExecutionUI
            toolName="fetch_team_official_name"
            args={args}
            result={result}
            status={status}
          />
      ) : null;
    },
  });


  useCopilotAction({
    name: "text2sql_query_transfer_portal",
    parameters: [
      {
        name: "sql_query",
        type: "string",
      }
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
         <ToolExecutionUI
            toolName="text2sql_query_transfer_portal"
            args={args}
            result={result}
            status={status}
          />
      ) : null;
    },
  });

  useCopilotAction({
    name: "fetch_team_basketball_data",
    parameters: [
      {
        name: "university_team",
        type: "string",
      }
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
        <ToolExecutionUI
          toolName="fetch_team_basketball_data"
          args={args}
          result={result}
          status={status}
        />
      ) : null;
    },
  });

  useCopilotAction({
    name: "filter_transfer_portal_players",
    parameters: [
      {
        name: "class_",
        type: "string",
      },
      {
        name: "position",
        type: "string",
      },
      {
        name: "efficiencyRating",
        type: "integer",
      },
      {
        name: "excludeCommitted",
        type: "boolean",
      },
      {
        name: "additional_filter",
        type: "string",
      },
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
        <ToolExecutionUI
          toolName="filter_transfer_portal_players"
          args={args}
          result={result}
          status={status}
        />
      ) : null;
    },
  });

  useCopilotAction({
  name: "prepare_email_for_approval_tool",
  parameters: [
    {
      name: "recipients",
      type: "object[]",
      attributes: [
        {
          name: "name",
          type: "string",
          description: "Name of the recipient"
        },
        {
          name: "email", 
          type: "string",
          description: "Email address of the recipient"
        }
      ],
      description: "Array of recipients with name and email - REQUIRED"
    },
    {
      name: "conversation_summary",
      type: "string",
      description: "Summary of the conversation to be emailed - REQUIRED"
    },
  ],
  renderAndWaitForResponse: ({ args, respond, status}) => {
    return <MultiRecipientEmailApprovalComponent args={args} respond={respond} status={status}/>;
  },
  });

  useCopilotAction({
    name: "search_player_development_tool",
    parameters: [
      {
        name: "query",
        type: "string",
      },
      {
        name: "meta_data",
        type: "string",
      },
    ],
    render: ({ args, result, status }) => {
      return enableVerbose ? (
        <ToolExecutionUI
          toolName="search_player_development_tool"
          args={args}
          result={result}
          status={status}
        />
      ) : null;
    },
  });

  const handleFilterChange = (filterType: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  // Updated handler function
  const handleCommitmentChange = (checked: boolean) => {
    setFilters(prev => ({
      ...prev,
      filters: {
        ...prev.filters,
        excludeCommitted: checked
      }
    }));
  };

  // Component implementation example
  const PlayerCommitmentToggle = () => {
    return (
      <div className="commitment-filter">
        <label>
          <input
            type="checkbox"
            checked={filters?.filters?.excludeCommitted || false}
            onChange={(e) => handleCommitmentChange(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          Show only committed players
        </label>
      </div>
    );
  };
  const handleCloseDetails = () => {
    setSelectedPlayer(null);
  };
  const handleCloseVideo = () => {
    setSelectedVideo(null);
  };
  return (
    <div className="flex h-screen bg-gray-50">

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">Transfer Portal Assistant</h1>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableVerbose}
                  onChange={(e) => setEnableVerbose(e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2"
                />
                <span className="text-sm text-gray-700">Enable verbose</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters?.filters?.excludeCommitted || false}
                  onChange={(e) => handleCommitmentChange(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                />
                <span className="text-sm text-gray-700">Exclude committed players</span>
              </label>
            </div>
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

          {/* Right Sidebar - Player Details or Video Player*/}

          {(selectedPlayer || selectedVideo) && (
            <div className="w-96">
              {selectedVideo ? (
                <SidebarVideoPlayer
                  video={selectedVideo}
                  onClose={handleCloseVideo}
                />
              ) : selectedPlayer ? (
                <PlayerDetails
                  player={selectedPlayer}
                  onClose={handleCloseDetails}
                />
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};



const PlayerCard = ({ player, onPlayerClick }) => {
  return (
    <div
      className="bg-white rounded-lg shadow-md border border-gray-200 p-4 cursor-pointer hover:shadow-lg transition-shadow duration-200"
      onClick={() => onPlayerClick(player)}
    >
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-900 truncate">
          {player.name || 'Unknown Player'}
        </h3>

        <div className="flex items-center justify-between text-sm text-gray-600">
          <span className="font-medium">{player.class || player.class_ || 'N/A'}</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
            {player.position || 'N/A'}
          </span>
        </div>

        <div className="text-sm text-gray-500 truncate">
          {player.team || 'N/A'}
        </div>
      </div>
    </div>
  );
};

const PlayerDetails = ({ player, onClose }) => {
  // Helper function to safely get numeric values and handle 'nan' strings
  const getNumericValue = (value, defaultValue = 0) => {
    if (value === 'nan' || value === null || value === undefined) {
      return defaultValue;
    }
    const numValue = parseFloat(value);
    return isNaN(numValue) ? defaultValue : numValue;
  };

  // Helper function to format BPR values with proper colors
  const formatBPR = (value) => {
    const numValue = getNumericValue(value);
    const formatted = numValue.toFixed(2);
    if (numValue > 0) {
      return { value: `+${formatted}`, color: 'text-green-600' };
    } else if (numValue < 0) {
      return { value: formatted, color: 'text-red-600' };
    }
    return { value: formatted, color: 'text-gray-600' };
  };

  // Helper function to get height in feet and inches
  const formatHeight = (heightInInches) => {
    const inches = getNumericValue(heightInInches);
    if (inches === 0) return 'N/A';
    const feet = Math.floor(inches / 12);
    const remainingInches = inches % 12;
    return `${feet}'${remainingInches}"`;
  };

  // Helper function to get availability status color
  const getAvailabilityColor = (eligible) => {
    if (eligible === 'True' || eligible === true) {
      return 'bg-green-100 text-green-800';
    }
    return 'bg-red-100 text-red-800';
  };

  // Helper function to get availability status text
  const getAvailabilityText = (eligible, newTeam) => {
    if (eligible === 'True' || eligible === true) {
      return newTeam && newTeam !== 'nan' && newTeam !== 'N/A' ? 'Committed' : 'Available';
    }
    return 'Not Available';
  };

  const bprPredicted = formatBPR(player.bpr_predicted);
  const obprPredicted = formatBPR(player.obpr_predicted);
  const dbprPredicted = formatBPR(player.dbpr_predicted);

  return (
    <div className="w-96 bg-white border-l border-gray-200 h-full overflow-y-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 sticky top-0 z-10">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-1">{player.name || 'Unknown Player'}</h3>
            <p className="text-blue-100 text-sm">
              {player.position || 'N/A'} • {player.team || 'N/A'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="ml-2 p-1 hover:bg-white hover:bg-opacity-20 rounded"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="mt-2 text-right">
          <div className="text-sm text-blue-100">Rank</div>
          <div className="text-lg font-bold">#{player.Rank || 'N/A'}</div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-gray-800">
              {formatHeight(player.height)}
            </div>
            <div className="text-sm text-gray-600">Height</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-gray-800">
              {player.weight && player.weight !== 'nan' ? `${player.weight} lbs` : 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Weight</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-gray-800">
              {player.class_ || player.class || 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Class</div>
          </div>
        </div>

        {/* BPR Performance Metrics */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Performance Metrics</h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-gray-50 p-3 rounded text-center">
              <div className={`text-lg font-semibold ${bprPredicted.color}`}>
                {bprPredicted.value}
              </div>
              <div className="text-xs text-gray-600">BPR</div>
            </div>
            <div className="bg-gray-50 p-3 rounded text-center">
              <div className={`text-lg font-semibold ${obprPredicted.color}`}>
                {obprPredicted.value}
              </div>
              <div className="text-xs text-gray-600">OBPR</div>
            </div>
            <div className="bg-gray-50 p-3 rounded text-center">
              <div className={`text-lg font-semibold ${dbprPredicted.color}`}>
                {dbprPredicted.value}
              </div>
              <div className="text-xs text-gray-600">DBPR</div>
            </div>
          </div>
        </div>

        {/* Team Performance */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Team Performance</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-sm font-medium text-blue-800">Off Efficiency</div>
              <div className="text-xl font-bold text-blue-600">
                {getNumericValue(player.adj_team_off_eff).toFixed(1)}
              </div>
            </div>
            <div className="bg-red-50 p-3 rounded">
              <div className="text-sm font-medium text-red-800">Def Efficiency</div>
              <div className="text-xl font-bold text-red-600">
                {getNumericValue(player.adj_team_def_eff).toFixed(1)}
              </div>
            </div>
          </div>
        </div>

        {/* Additional Stats */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Statistics</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Possessions</span>
              <span className="font-medium">{player.possessions || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Plus/Minus</span>
              <span className={`font-medium ${getNumericValue(player.plus_minus) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {getNumericValue(player.plus_minus) >= 0 ? '+' : ''}{getNumericValue(player.plus_minus).toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Role</span>
              <span className="font-medium">{getNumericValue(player.role).toFixed(1)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Team Margin</span>
              <span className={`font-medium ${getNumericValue(player.adj_team_eff_margin) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {getNumericValue(player.adj_team_eff_margin) >= 0 ? '+' : ''}{getNumericValue(player.adj_team_eff_margin).toFixed(1)}
              </span>
            </div>
          </div>
        </div>

        {/* Transfer Status */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Transfer Status</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getAvailabilityColor(player.eligible)}`}>
                {getAvailabilityText(player.eligible, player.new_team)}
              </span>
            </div>

            {player.new_team && player.new_team !== 'nan' && player.new_team !== 'N/A' && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">New Team</span>
                <span className="font-medium text-green-600">{player.new_team}</span>
              </div>
            )}
          </div>
        </div>

        {/* NIL Value */}
        {player.dollar_value_string && player.dollar_value_string !== 'nan' && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">NIL Value</h4>
            <div className="bg-green-50 p-3 rounded text-center">
              <div className="text-xl font-bold text-green-600">{player.dollar_value_string}</div>
            </div>
          </div>
        )}

        {/* Notes */}
        {player.notes && player.notes !== 'nan' && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Notes</h4>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-700">{player.notes}</p>
            </div>
          </div>
        )}

        {/* Recent Updates */}
        {player.recent && player.recent !== '' && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Recent Updates</h4>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                {player.recent}
              </span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2 pt-4 border-t border-gray-200">
          <button className="w-full py-3 px-4 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition-colors">
            Compare to URI roster
          </button>
          <button className="w-full py-3 px-4 bg-orange-500 text-white rounded-md font-medium hover:bg-orange-600 transition-colors">
            Flag for recruiting
          </button>
          <button className="w-full py-3 px-4 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-colors">
            View HS video
          </button>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-gray-100">
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>ID: {player.player_id || 'N/A'}</span>
            <span>Updated: {new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const StepsFeedback = ({ args, result, status, selectedPlayer, setSelectedPlayer }) => {
  const [accepted, setAccepted] = useState(null);

  const players = result?.result || [];
  // const [selectedPlayer, setSelectedPlayer] = useState(null);
  const handlePlayerClick = (player) => {
    console.log('selected player', player)
    setSelectedPlayer(player);
  };

  const handleCloseDetails = () => {
    setSelectedPlayer(null);
  };
  // Handle case where players is undefined or not an array
  if (!players || !Array.isArray(players)) {
    return (
      <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
        <div className="text-black space-y-2">
          <h2 className="text-lg font-bold mb-4">Player Results</h2>
          <div className="text-center py-8">
            <p className="text-gray-600">No player data available</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle case where players array is empty
  if (players.length === 0) {
    return (
      <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
        <div className="text-black space-y-2">
          <h2 className="text-lg font-bold mb-4">Player Results</h2>
          <div className="text-center py-8">
            <p className="text-gray-600">No players found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
      <div className="text-black space-y-2">
        <h2 className="text-lg font-bold mb-4">Player Results</h2>
        {/* Table View */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Player
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Class
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Team
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {players.map((player, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handlePlayerClick(player)}
                        className="text-blue-600 hover:text-blue-800 font-medium text-left"
                      >
                        {player.name || 'Unknown Player'}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {player.class || player.class_ || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {player.position || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {player.team || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      #{player.Rank || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${player.eligible === 'True' || player.eligible === true
                          ? (player.new_team && player.new_team !== 'nan' && player.new_team !== 'N/A'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800')
                          : 'bg-red-100 text-red-800'
                        }`}>
                        {player.eligible === 'True' || player.eligible === true
                          ? (player.new_team && player.new_team !== 'nan' && player.new_team !== 'N/A'
                            ? 'Committed'
                            : 'Available')
                          : 'Not Available'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        {/* Player Cards Grid */}
        {/* <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {players.map((player, index) => (
            <PlayerCard key={index} player={player}  onPlayerClick={handlePlayerClick} />
          ))}
        </div> */}

        {/* Raw Data (collapsed by default) */}
        <details className="mt-6">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
            Show Raw Data
          </summary>
          <pre className="text-sm mt-2 bg-gray-50 p-4 rounded overflow-x-auto">
            {JSON.stringify(players, null, 2)}
          </pre>
        </details>
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